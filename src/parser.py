import re
from typing import Dict, Tuple
from src.models import MapData, Zone, Connection
from src.exceptions import ParsingError

class MapParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.map_data = MapData()
        self.line_num = 0
        self.meta_pattern = re.compile(r'\[(.*?)\]')
        self.valid_zone_types = {"normal", "blocked", "restricted", "priority"}

    def parse(self) -> MapData:
        # First line
        try:
            with open(self.filepath, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            raise Exception(f"File not found: {self.filepath}")

        first_line_found = False
        while self.line_num < len(lines):
            line = lines[self.line_num].strip()
            self.line_num += 1
            if not line or line.startswith('#'):
                continue

            if not line.startswith('nb_drones:'):
                raise ParsingError("First line must define nb_drones", self.line_num)

            try:
                self.map_data.nb_drones = int(line.split(':')[1].strip())
                if self.map_data.nb_drones <= 0:
                    raise ValueError()
            except:
                raise ParsingError("Invalid number of drones", self.line_num)

            first_line_found = True
            break

        if not first_line_found:
            raise ParsingError("Empty map file", self.line_num)
        # Other Line
        for line in lines[self.line_num:]:
            self.line_num += 1
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if any(line.startswith(prefix) for prefix in ['hub:', 'start_hub:', 'end_hub:']):
                self._parse_zone(line)
            elif line.startswith('connection:'):
                self._parse_connection(line)
            else:
                raise ParsingError(f"Unknown line format: {line}", self.line_num)

        self._validate_global_rules()
        return self.map_data

    def _extract_metadata(self, line: str) -> Tuple[str, Dict[str, str]]:
        match = self.meta_pattern.search(line)
        metadata = {}
        main_line = line

        if match:
            main_line = line[:match.start()].strip()
            meta_str = match.group(1)
            pairs = meta_str.split()
            for pair in pairs:
                if '=' not in pair:
                    raise ParsingError(f"Invalid metadata format: '{pair}'", self.line_num)
                key, val = pair.split('=', 1)
                metadata[key] = val
        return main_line, metadata

    def _parse_zone(self, line: str) -> None:
        # Unpacking and cut
        main_line, metadata = self._extract_metadata(line)
        parts = main_line.split()
        if len(parts) != 4:
            raise ParsingError("Invalid zone format. Expected: type: name x y", self.line_num)

        prefix, name, x_str, y_str = parts[0], parts[1], parts[2], parts[3]

        # Identity control and logic parsing
        if '-' in name:
            raise ParsingError(f"Zone name '{name}' contains forbidden dash.", self.line_num)
        if name in self.map_data.zones:
            raise ParsingError(f"Duplicate zone name: {name}", self.line_num)

        try:
            x, y = int(x_str), int(y_str)
        except ValueError:
            raise ParsingError(f"Coordinates must be integers for zone {name}", self.line_num)

        #Option reading
        zone_type = metadata.get('zone', 'normal')
        if zone_type not in self.valid_zone_types:
            raise ParsingError(f"Invalid zone type: {zone_type}", self.line_num)

        max_drones_str = metadata.get('max_drones', '1')
        try:
            max_drones = int(max_drones_str)
            if max_drones <= 0:
                raise ValueError()
        except ValueError:
            raise ParsingError(f"Invalid max_drones value: {max_drones_str}", self.line_num)

        color = metadata.get('color')

        # Object Création
        new_zone = Zone(name, x, y, zone_type, color, max_drones)
        self.map_data.zones[name] = new_zone

        # Entry and exit point specificity
        if prefix == 'start_hub:':
            if self.map_data.start_hub is not None:
                raise ParsingError("Multiple start_hub defined", self.line_num)
            self.map_data.start_hub = name
        elif prefix == 'end_hub:':
            if self.map_data.end_hub is not None:
                raise ParsingError("Multiple end_hub defined", self.line_num)
            self.map_data.end_hub = name

    def _parse_connection(self, line: str) -> None:
        # Way Cut
        main_line, metadata = self._extract_metadata(line)
        prefix = "connection:"
        if not main_line.startswith(prefix):
            raise ParsingError("Invalid connection prefix", self.line_num)

        nodes_str = main_line[len(prefix):].strip()
        nodes = nodes_str.split('-')
        if len(nodes) != 2:
            raise ParsingError("Invalid connection format. Expected node1-node2", self.line_num)

        # existence of the places
        n1, n2 = nodes[0].strip(), nodes[1].strip()
        if n1 not in self.map_data.zones or n2 not in self.map_data.zones:
            raise ParsingError(f"Unknown zone in connection: {n1}-{n2}", self.line_num)

        # check for duplicate connection
        if n1 in self.map_data.adjacency_list and n2 in self.map_data.adjacency_list[n1]:
            raise ParsingError(f"Duplicate connection: {n1}-{n2}", self.line_num)
            
        # way code
        max_cap_str = metadata.get('max_link_capacity', '1')
        try:
            max_link_cap = int(max_cap_str)
            if max_link_cap <= 0:
                raise ValueError()
        except ValueError:
            raise ParsingError(f"Invalid max_link_capacity: {max_cap_str}", self.line_num)

        # Add to model
        self.map_data.connections.append(Connection(n1, n2, max_link_cap))

        # Add to adjacency list
        if n1 not in self.map_data.adjacency_list:
            self.map_data.adjacency_list[n1] = []
        if n2 not in self.map_data.adjacency_list:
            self.map_data.adjacency_list[n2] = []

        if n2 not in self.map_data.adjacency_list[n1]:
            self.map_data.adjacency_list[n1].append(n2)
        if n1 not in self.map_data.adjacency_list[n2]:
            self.map_data.adjacency_list[n2].append(n1)

    def _validate_global_rules(self) -> None:
        if self.map_data.start_hub is None:
            raise ParsingError("No start_hub defined", self.line_num)
        if self.map_data.end_hub is None:
            raise ParsingError("No end_hub defined", self.line_num)
