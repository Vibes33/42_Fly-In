from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import heapq
from concurrent.futures import ProcessPoolExecutor, as_completed
from src.models import MapData
from src.astar import SpaceTimeAStar, Constraint, State

# On crée une fonction au niveau du module pour qu'elle soit "picklable" par ProcessPoolExecutor
def compute_astar_path(args):
    map_data, drone_id, constraints = args
    astar = SpaceTimeAStar(map_data)
    return drone_id, constraints, astar.find_path(drone_id, constraints)

@dataclass
class Conflict:
    time: int
    drone_ids: List[str]
    location: str
    is_edge: bool = False
    is_cardinal: bool = False

@dataclass
class CTNode:
    constraints: List[Constraint]
    paths: Dict[str, List[State]]
    cost: int
    
    def __lt__(self, other: 'CTNode') -> bool:
        return self.cost < other.cost

class ICBSSolver:
    def __init__(self, map_data: MapData):
        self.map_data = map_data
        self.astar_engine = SpaceTimeAStar(map_data)
        self.drones = [f"D{i+1}" for i in range(map_data.nb_drones)]
        self.path_cache: Dict[Tuple[str, frozenset[Tuple[int, str, bool]]], List[State]] = {}
        # Thread pool pour accélérer les batchs de A*
        self.executor = ProcessPoolExecutor(max_workers=4)

    def _get_path(self, drone_id: str, constraints: List[Constraint]) -> Optional[List[State]]:
        # Filtre et formatage pour un cache rapide : (time, location, is_edge)
        my_constraints = frozenset((c.time, c.location, c.is_edge) for c in constraints if c.drone_id == drone_id)
        cache_key = (drone_id, my_constraints)
        
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
            
        path = self.astar_engine.find_path(drone_id, constraints)
        if path:
            self.path_cache[cache_key] = path
        return path
        
    def _batch_get_paths(self, tasks: List[Tuple[str, List[Constraint]]]) -> Dict[str, Optional[List[State]]]:
        results = {}
        to_compute = []
        
        # Check cache first
        for drone_id, constraints in tasks:
            my_constraints = frozenset((c.time, c.location, c.is_edge) for c in constraints if c.drone_id == drone_id)
            cache_key = (drone_id, my_constraints)
            if cache_key in self.path_cache:
                results[drone_id] = self.path_cache[cache_key]
            else:
                to_compute.append((self.map_data, drone_id, constraints))
                
        # Compute the rest with Multiprocessing
        if to_compute:
            futures = {self.executor.submit(compute_astar_path, args): args for args in to_compute}
            for future in as_completed(futures):
                drone_id, constraints, path = future.result()
                results[drone_id] = path
                
                if path:
                    my_constraints = frozenset((c.time, c.location, c.is_edge) for c in constraints if c.drone_id == drone_id)
                    cache_key = (drone_id, my_constraints)
                    self.path_cache[cache_key] = path
                    
        return results

    def solve(self) -> Dict[str, List[State]]:
        root_paths = {}
        for d in self.drones:
            path = self._get_path(d, [])
            if not path:
                raise Exception(f"No initial path found for {d}")
            root_paths[d] = path

        root_cost = sum(len(p) - 1 for p in root_paths.values())
        root = CTNode(constraints=[], paths=root_paths, cost=root_cost)

        open_set: List[CTNode] = []
        heapq.heappush(open_set, root)

        iter_count = 0
        while open_set:
            current = heapq.heappop(open_set)
            
            conflict = self._find_best_conflict(current.paths, current.constraints)
            if not conflict:
                print(f"Optimal solution found in {iter_count} iterations!")
                return current.paths

            iter_count += 1
            if iter_count % 1000 == 0:
                print(f"[CBS] Searching... Iteration: {iter_count}, Current cost: {current.cost}")
            if iter_count > 50000:
                print("Warning: Search space too large. Returning current best effort.")
                return current.paths

            # Résolution de conflit (avec l'optimisation BYPASS)
            children = []
            bypassed = False
            
            # Use Multiprocessing to evaluate constraint impact on all conflicting drones
            batch_tasks = []
            for d in conflict.drone_ids:
                new_constraint = Constraint(d, conflict.time, conflict.location, conflict.is_edge)
                test_constraints = current.constraints.copy()
                test_constraints.append(new_constraint)
                batch_tasks.append((d, test_constraints))
                
            batch_results = self._batch_get_paths(batch_tasks)
            
            for i, d in enumerate(conflict.drone_ids):
                new_constraint = Constraint(d, conflict.time, conflict.location, conflict.is_edge)
                updated_path = batch_results[d]
                
                if not updated_path:
                    continue
                    
                new_paths = current.paths.copy()
                new_paths[d] = updated_path
                new_cost = sum(len(p) - 1 for p in new_paths.values())
                
                new_constraints = current.constraints.copy()
                new_constraints.append(new_constraint)
                child_node = CTNode(new_constraints, new_paths, new_cost)
                
                # BYPASS: Si le coût n'augmente pas, on esquive le conflit gratuitement
                if child_node.cost == current.cost:
                    heapq.heappush(open_set, child_node)
                    bypassed = True
                    break # On ignore les autres branches (élagage massif)
                
                children.append(child_node)
            
            if not bypassed:
                for c in children:
                    heapq.heappush(open_set, c)

        raise Exception("No valid scheduling found")

    def _generate_child_node(self, node: CTNode, new_constraint: Constraint, recompute_drone: str) -> Optional[CTNode]:
        new_constraints = node.constraints.copy()
        new_constraints.append(new_constraint)

        updated_path = self._get_path(recompute_drone, new_constraints)
        if not updated_path:
            return None # Impossible de résoudre pour ce drone avec cette contrainte
            
        new_paths = node.paths.copy()
        new_paths[recompute_drone] = updated_path
        
        new_cost = sum(len(p) - 1 for p in new_paths.values())
        return CTNode(new_constraints, new_paths, new_cost)

    def _find_best_conflict(self, paths: Dict[str, List[State]], node_constraints: List[Constraint]) -> Optional[Conflict]:
        max_time = max(len(p) for p in paths.values()) if paths else 0
        
        all_conflicts = []

        for t in range(max_time):
            # Zone Occupancy
            zone_occupancy: Dict[str, List[str]] = {}
            for d, p in paths.items():
                if t < len(p):
                    z = p[t].zone_name
                    if z == self.map_data.end_hub or (z == self.map_data.start_hub and t == 0):
                        continue
                    if z not in zone_occupancy:
                        zone_occupancy[z] = []
                    zone_occupancy[z].append(d)
            
            for zone, drones in zone_occupancy.items():
                z_limit = self.map_data.zones[zone].max_drones
                if len(drones) > z_limit:
                    all_conflicts.append(Conflict(t, drones, zone, False))

            # Edge Occupancy
            edge_occupancy: Dict[str, List[str]] = {}
            for d, p in paths.items():
                if t > 0 and t < len(p):
                    prev = p[t-1]
                    curr = p[t]
                    if prev.zone_name != curr.zone_name:
                        edge = tuple(sorted([prev.zone_name, curr.zone_name]))
                        edge_str = f"{edge[0]}-{edge[1]}"
                        if edge_str not in edge_occupancy:
                            edge_occupancy[edge_str] = []
                        edge_occupancy[edge_str].append(d)
            
            for edge_str, drones in edge_occupancy.items():
                z1, z2 = edge_str.split('-')
                val = self.map_data.get_connection_capacity(z1, z2)
                if len(drones) > val:
                    all_conflicts.append(Conflict(t, drones, edge_str, True))
            
            # EARLY EXIT: Si on a trouvé des conflits à ce tour T, on s'arrête de scanner le reste du temps
            # C'est l'essence même de l'Earliest Conflict First (ECF). Inutile de calculer la MDD des tours 50
            # si le tour 1 est bloqué !
            if all_conflicts:
                break

        if not all_conflicts:
            return None

        # MDD-like classification using our fast memoized A*
        cardinal_conflicts = []
        semi_cardinal_conflicts = []
        non_cardinal_conflicts = []

        for c in all_conflicts:
            detour_count = 0
            for d in c.drone_ids:
                old_path_len = len(paths[d])
                test_constraint = Constraint(d, c.time, c.location, c.is_edge)
                test_constraints = node_constraints.copy()
                test_constraints.append(test_constraint)
                
                alt_path = self._get_path(d, test_constraints)
                if not alt_path or len(alt_path) > old_path_len:
                    detour_count += 1
            
            if detour_count == len(c.drone_ids):
                c.is_cardinal = True
                cardinal_conflicts.append(c)
            elif detour_count > 0:
                semi_cardinal_conflicts.append(c)
            else:
                non_cardinal_conflicts.append(c)

        # Prioritize: Cardinal > Semi-Cardinal > Non-Cardinal
        if cardinal_conflicts:
            return cardinal_conflicts[0]
        if semi_cardinal_conflicts:
            return semi_cardinal_conflicts[0]
        return non_cardinal_conflicts[0]
