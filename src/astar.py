from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
import heapq
from src.models import MapData

@dataclass
class State:
    zone_name: str
    time: int
    is_in_transit: bool
    g_score: int
    f_score: int
    parent: Optional['State'] = None

    def __lt__(self, other: 'State') -> bool:
        return self.f_score < other.f_score

@dataclass
class Constraint:
    drone_id: str
    time: int
    location: str  # Can be a single zone name or "z1-z2" for an edge
    is_edge: bool = False

class SpaceTimeAStar:
    def __init__(self, map_data: MapData):
        self.map_data = map_data

    def _get_heuristic(self, current_zone: str, goal_zone: str) -> int:
        z1 = self.map_data.zones[current_zone]
        z2 = self.map_data.zones[goal_zone]
        return abs(z1.x - z2.x) + abs(z1.y - z2.y)

    def _is_constrained(self, drone_id: str, u: str, v: str, next_time: int, constraints: List[Constraint], cost: int) -> bool:
        # Check constraints for all steps in the movement
        # If cost is 2, it arrives at next_time, but occupies edge at next_time-1
        for c in constraints:
            if c.drone_id != drone_id:
                continue
            
            # Vertex constraint
            if not c.is_edge:
                if c.location == v and c.time == next_time:
                    return True
                if cost == 2 and c.location == u and c.time == next_time - 1:
                    return True
            # Edge constraint
            else:
                if cost == 2 and c.time == next_time - 1:
                    l1, l2 = c.location.split('-')
                    if (u == l1 and v == l2) or (u == l2 and v == l1):
                        return True
                elif cost == 1 and c.time == next_time:
                    l1, l2 = c.location.split('-')
                    if (u == l1 and v == l2) or (u == l2 and v == l1):
                        return True
        return False

    def find_path(self, drone_id: str, constraints: List[Constraint]) -> Optional[List[State]]:
        start_zone = self.map_data.start_hub
        end_zone = self.map_data.end_hub
        if not start_zone or not end_zone:
            return None

        open_set: List[State] = []
        start_node = State(start_zone, 0, False, 0, self._get_heuristic(start_zone, end_zone))
        heapq.heappush(open_set, start_node)

        # (zone, time, is_in_transit)
        closed_set: Set[Tuple[str, int, bool]] = set()

        # To avoid infinite waiting
        max_time = 200 

        while open_set:
            current = heapq.heappop(open_set)

            if current.zone_name == end_zone and current.time > 0: # Avoid thinking zero is arrived if we haven't moved and it's not the actual end setup but a loop
                # Check if stay at end from now on contradicts anything? Normally end is sink.
                path = []
                temp = current
                while temp:
                    path.append(temp)
                    temp = temp.parent
                return path[::-1]

            state_tuple = (current.zone_name, current.time, current.is_in_transit)
            if state_tuple in closed_set:
                continue
            closed_set.add(state_tuple)

            if current.time > max_time:
                continue

            # Generate neighbors
            # 1. Wait action
            wait_constrained = False
            for c in constraints:
                if not c.is_edge and c.drone_id == drone_id and c.time == current.time + 1 and c.location == current.zone_name:
                    wait_constrained = True
                    break
            
            if not wait_constrained:
                wait_state = State(current.zone_name, current.time + 1, False, current.g_score + 1, current.g_score + 1 + self._get_heuristic(current.zone_name, end_zone), current)
                heapq.heappush(open_set, wait_state)

            # 2. Move actions
            for neighbor in self.map_data.get_neighbors(current.zone_name):
                z = self.map_data.zones[neighbor]
                if not z.is_passable():
                    continue
                
                cost = z.get_movement_cost()
                next_time = current.time + cost
                is_transit = cost > 1

                if not self._is_constrained(drone_id, current.zone_name, neighbor, next_time, constraints, cost):
                    n_state = State(neighbor, next_time, is_transit, current.g_score + cost, current.g_score + cost + self._get_heuristic(neighbor, end_zone), current)
                    heapq.heappush(open_set, n_state)

        return None
