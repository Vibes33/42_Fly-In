import heapq
from typing import Dict, List, Tuple, Set, Optional
from src.models import MapData

class Router:
    def __init__(self, map_data: MapData):
        self.map_data = map_data
        # Zone, heuristique
        self.heuristic: Dict[str, float] = {}
        # [Nom, Temps], nombre de drones prévus
        self.zone_reservations: Dict[Tuple[str, int], int] = {}
        # [Ca, Cb, Temps], nombre de drones actuels
        self.edge_reservations: Dict[Tuple[str, str, int], int] = {}

    def compute_true_distance_heuristic(self) -> None:

        end_hub = self.map_data.end_hub
        if not end_hub:
            return

        self.heuristic = {zone: float('inf') for zone in self.map_data.zones}
        self.heuristic[end_hub] = 0.0

        #priority queue, distance, nom de zone
        pq = [(0.0, end_hub)]

        while pq:
            current_dist, current_zone = heapq.heappop(pq)

            if current_dist > self.heuristic[current_zone]:
                continue

            for neighbor in self.map_data.get_neighbors(current_zone):
                if not self.map_data.zones[neighbor].is_passable():
                    continue

                cost = self.map_data.zones[current_zone].get_movement_cost()
                new_dist = current_dist + cost

                if new_dist < self.heuristic[neighbor]:
                    self.heuristic[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))

    def get_zone_occupancy(self, zone_name: str, time: int) -> int:
        return self.zone_reservations.get((zone_name, time), 0)

    def get_edge_occupancy(self, u: str, v: str, time: int) -> int:
        # sorted pour trier par ordre alpha car bidirectionnels
        edge = tuple(sorted([u, v]))
        return self.edge_reservations.get((edge[0], edge[1], time), 0)

    def reserve_path(self, path: List[Tuple[str, int]]) -> None:
        for i, (zone, t) in enumerate(path):
            # Réserver la zone
            self.zone_reservations[(zone, t)] = self.get_zone_occupancy(zone, t) + 1

            # Réserver la connexion empruntée (si ce n'est pas le premier point)
            if i > 0:
                prev_zone, prev_t = path[i-1]
                if zone != prev_zone:
                    edge = tuple(sorted([prev_zone, zone]))
                    for edge_time in range(prev_t, t):
                        self.edge_reservations[(edge[0], edge[1], edge_time)] = \
                            self.edge_reservations.get((edge[0], edge[1], edge_time), 0) + 1

    def space_time_a_star(self, start_time: int = 0) -> Optional[List[Tuple[str, int]]]:
        start_zone = self.map_data.start_hub
        end_zone = self.map_data.end_hub
        if not start_zone or not end_zone:
            return None

        pq = [(self.heuristic[start_zone], 0, start_time, start_zone, None)]

        # (zone_name, time), fil d'Ariane -> classe du meilleur au moins bon avec f = g + h
        came_from: Dict[Tuple[str, int], Tuple[str, int]] = {}
        # (zone, temps) -> g_score -> temps
        g_scores: Dict[Tuple[str, int], int] = {(start_zone, start_time): 0}

        while pq:
            _, _, current_time, current_zone, parent = heapq.heappop(pq)
            state = (current_zone, current_time)

            if parent is not None and state not in came_from:
                came_from[state] = parent

            if current_zone == end_zone:
                # Reconstruire le chemin
                path = []
                curr = state
                while curr in came_from:
                    path.append(curr)
                    curr = came_from[curr]
                path.append((start_zone, start_time))
                return path[::-1]

            if current_time > 1000:  
                continue

            # Option 1: Attendre sur place (Temps + 1)
            next_time = current_time + 1
            zone_obj = self.map_data.zones[current_zone]
            
            if current_zone in (start_zone, end_zone) or self.get_zone_occupancy(current_zone, next_time) < zone_obj.max_drones:
                wait_state = (current_zone, next_time)
                new_g = g_scores[state] + 1
                if new_g < g_scores.get(wait_state, float('inf')):
                    g_scores[wait_state] = new_g
                    f_score = new_g + self.heuristic[current_zone]
                    heapq.heappush(pq, (f_score, -next_time, next_time, current_zone, state))

            # Option 2: Se déplacer vers un voisin
            for neighbor in self.map_data.get_neighbors(current_zone):
                neighbor_obj = self.map_data.zones[neighbor]
                if not neighbor_obj.is_passable():
                    continue

                cost = neighbor_obj.get_movement_cost()
                arrival_time = current_time + cost
                
                # Vérifier la capacité de la ZONE à l'arrivée
                if neighbor != end_zone and self.get_zone_occupancy(neighbor, arrival_time) >= neighbor_obj.max_drones:
                    continue
                
                # Vérifier la capacité de la CONNEXION pendant le mouvement
                link_cap = self.map_data.get_connection_capacity(current_zone, neighbor)
                edge_blocked = False
                for t in range(current_time, arrival_time):
                    if self.get_edge_occupancy(current_zone, neighbor, t) >= link_cap:
                        edge_blocked = True
                        break
                
                if edge_blocked:
                    continue

                move_state = (neighbor, arrival_time)
                new_g = g_scores[state] + cost

                if new_g < g_scores.get(move_state, float('inf')):
                    g_scores[move_state] = new_g
                    f_score = new_g + self.heuristic.get(neighbor, float('inf'))
                    heapq.heappush(pq, (f_score, -arrival_time, arrival_time, neighbor, state))

        return None # Aucun chemin trouvé
