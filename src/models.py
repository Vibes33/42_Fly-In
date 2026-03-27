from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: str = "normal"  # normal, restricted, priority, blocked
    color: Optional[str] = None
    max_drones: int = 1

    def is_passable(self) -> bool:
        return self.zone_type != "blocked"

    def get_movement_cost(self) -> int:
        if self.zone_type == "restricted":
            return 2
        return 1

@dataclass
class Connection:
    zone1: str
    zone2: str
    max_link_capacity: int = 1

@dataclass
class MapData:
    nb_drones: int = 0
    start_hub: Optional[str] = None
    end_hub: Optional[str] = None
    zones: Dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
    adjacency_list: Dict[str, List[str]] = field(default_factory=dict)

    def get_neighbors(self, zone_name: str) -> List[str]:
        return self.adjacency_list.get(zone_name, [])

    def get_connection_capacity(self, z1: str, z2: str) -> int:
        for conn in self.connections:
            if (conn.zone1 == z1 and conn.zone2 == z2) or (conn.zone1 == z2 and conn.zone2 == z1):
                return conn.max_link_capacity
        return 1
