from typing import List, Dict, Tuple
import heapq
from src.models import MapData
from src.astar import State

class ReservationTable:
    def __init__(self, map_data: MapData):
        self.map_data = map_data
        self.zone_usage: Dict[Tuple[int, str], int] = {}
        self.edge_usage: Dict[Tuple[int, str, str], int] = {}

    def is_zone_available(self, zone: str, time: int) -> bool:
        if zone == self.map_data.end_hub:
            return True
        if time == 0 and zone == self.map_data.start_hub:
            return True
        
        used = self.zone_usage.get((time, zone), 0)
        return used < self.map_data.zones[zone].max_drones

    def is_edge_available(self, z1: str, z2: str, time: int) -> bool:
        edge = tuple(sorted([z1, z2]))
        used = self.edge_usage.get((time, edge[0], edge[1]), 0)
        cap = self.map_data.get_connection_capacity(z1, z2)
        return used < cap

    def reserve_path(self, path: List[State]):
        max_time = max(s.time for s in path)
        for i in range(len(path)):
            curr = path[i]
            
            # Réserver la zone (sauf le end_hub qui est infini)
            if curr.zone_name != self.map_data.end_hub:
                self.zone_usage[(curr.time, curr.zone_name)] = self.zone_usage.get((curr.time, curr.zone_name), 0) + 1
                
            # Gérer les attentes en attendant le tour suivant, si ça reste sur place
            if i + 1 < len(path):
                nxt = path[i+1]
                if nxt.zone_name == curr.zone_name:
                    for t in range(curr.time + 1, nxt.time):
                        if curr.zone_name != self.map_data.end_hub:
                            self.zone_usage[(t, curr.zone_name)] = self.zone_usage.get((t, curr.zone_name), 0) + 1

            # Réserver le edge (lien) si on bouge
            if i > 0:
                prev = path[i-1]
                if prev.zone_name != curr.zone_name:
                    edge = tuple(sorted([prev.zone_name, curr.zone_name]))
                    for step_t in range(prev.time + 1, curr.time + 1):
                        self.edge_usage[(step_t, edge[0], edge[1])] = self.edge_usage.get((step_t, edge[0], edge[1]), 0) + 1


class PrioritizedPlanner:
    def __init__(self, map_data: MapData):
        self.map_data = map_data
        self.drones = [f"D{i+1}" for i in range(map_data.nb_drones)]

    def _get_heuristic(self, current_zone: str, goal_zone: str) -> int:
        z1 = self.map_data.zones[current_zone]
        z2 = self.map_data.zones[goal_zone]
        return abs(z1.x - z2.x) + abs(z1.y - z2.y)

    def _find_path(self, start_zone: str, end_zone: str, res_table: ReservationTable) -> List[State]:
        open_set: List[State] = []
        start_node = State(start_zone, 0, False, 0, self._get_heuristic(start_zone, end_zone))
        heapq.heappush(open_set, start_node)
        
        closed_set = set() # (zone, time)
        
        # Security to avoid infinite search if totally blocked
        limit_time = 1000 
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current.zone_name == end_zone:
                path = []
                temp = current
                while temp:
                    path.append(temp)
                    temp = temp.parent
                return path[::-1]

            state_tuple = (current.zone_name, current.time)
            if state_tuple in closed_set:
                continue
            closed_set.add(state_tuple)
            
            if current.time > limit_time:
                continue

            # 1. Action : Wait 
            next_time = current.time + 1
            if res_table.is_zone_available(current.zone_name, next_time):
                wait_state = State(current.zone_name, next_time, False, current.g_score + 1, current.g_score + 1 + self._get_heuristic(current.zone_name, end_zone), current)
                heapq.heappush(open_set, wait_state)

            # 2. Action : Move
            for neighbor in self.map_data.get_neighbors(current.zone_name):
                z = self.map_data.zones[neighbor]
                if not z.is_passable(): 
                    continue
                
                cost = z.get_movement_cost()
                arrive_time = current.time + cost
                is_transit = cost > 1
                
                valid = True
                for step_t in range(current.time + 1, arrive_time + 1):
                    if not res_table.is_edge_available(current.zone_name, neighbor, step_t):
                        valid = False
                        break
                        
                if valid and not res_table.is_zone_available(neighbor, arrive_time):
                    valid = False
                    
                if valid:
                    n_state = State(neighbor, arrive_time, is_transit, current.g_score + cost, current.g_score + cost + self._get_heuristic(neighbor, end_zone), current)
                    heapq.heappush(open_set, n_state)
                    
        return []

    def solve(self) -> Dict[str, List[State]]:
        res_table = ReservationTable(self.map_data)
        paths = {}
        
        for d in self.drones:
            p = self._find_path(self.map_data.start_hub, self.map_data.end_hub, res_table)
            if not p:
                raise Exception(f"Deadlock ou impossibilité de trouver un chemin pour {d} avec Planification Priorisée.")
            res_table.reserve_path(p)
            paths[d] = p
            
        return paths