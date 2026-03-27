from src.models import MapData

class TerminalVisualizer:
    def __init__(self) -> None:
        self.colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "gray": "\033[90m",
            "reset": "\033[0m"
        }

    def draw_map(self, map_data: MapData) -> None:
        print("🗺  Map Preview:")
        for z_name, zone in map_data.zones.items():
            color_code = self.colors.get(zone.color, self.colors["reset"]) if zone.color else self.colors["reset"]
            cap = zone.max_drones if zone.zone_type != "start_hub" and zone.zone_type != "end_hub" else "inf"
            print(f"{color_code}[{zone.zone_type}] {z_name} ({zone.x}, {zone.y}) Cap: {cap}{self.colors['reset']}")
        print(f"Total Drones: {map_data.nb_drones}")
        
        self._draw_ascii_map(map_data)
        print("\n--- Starting Simulation ---\n")

    def _draw_ascii_map(self, map_data: MapData) -> None:
        if not map_data.zones:
            return

        print("\n🗺  Visual Grid Map:")
        min_x = min(z.x for z in map_data.zones.values())
        max_x = max(z.x for z in map_data.zones.values())
        min_y = min(z.y for z in map_data.zones.values())
        max_y = max(z.y for z in map_data.zones.values())

        # On fait une grille avec des espaces intermédiaires pour les connexions.
        # Donc la coordonnée réelle d'un noeud (x, y) devient la coordonnée de grille (x*2, y*2)
        grid_width = (max_x - min_x) * 2 + 1
        grid_height = (max_y - min_y) * 2 + 1

        if grid_width > 150 or grid_height > 150:
            print("Map too large to display visual grid.")
            return

        grid = [[" " for _ in range(grid_width)] for _ in range(grid_height)]
        
        # 1. Dessiner les connexions
        for conn in map_data.connections:
            z1 = map_data.zones.get(conn.zone1)
            z2 = map_data.zones.get(conn.zone2)
            
            if not z1 or not z2:
                continue
                
            x1, y1 = (z1.x - min_x) * 2, (z1.y - min_y) * 2
            x2, y2 = (z2.x - min_x) * 2, (z2.y - min_y) * 2
            
            # Droite horizontale
            if y1 == y2:
                for i in range(min(x1, x2) + 1, max(x1, x2)):
                    if grid[y1][i] == " ":
                        grid[y1][i] = "-"
            # Droite verticale
            elif x1 == x2:
                for i in range(min(y1, y2) + 1, max(y1, y2)):
                    if grid[i][x1] == " ":
                        grid[i][x1] = "|"
            # Diagonale
            else:
                steps = max(abs(x2 - x1), abs(y2 - y1))
                dx = (x2 - x1) / steps
                dy = (y2 - y1) / steps
                for i in range(1, steps):
                    cx, cy = int(round(x1 + i * dx)), int(round(y1 + i * dy))
                    if grid[cy][cx] == " ":
                        if (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
                            grid[cy][cx] = "/"
                        else:
                            grid[cy][cx] = "\\"

        # 2. Dessiner les noeuds par-dessus
        for z in map_data.zones.values():
            color = self.colors.get(z.color, self.colors["reset"]) if z.color else self.colors["reset"]
            
            char = "O"
            if z.zone_type == "blocked": char = "X"
            elif z.zone_type == "restricted": char = "R"
            elif z.zone_type == "priority": char = "P"
            
            if z.name == map_data.start_hub: char = "S"
            if z.name == map_data.end_hub: char = "E"
            
            gy, gx = (z.y - min_y) * 2, (z.x - min_x) * 2
            grid[gy][gx] = f"{color}{char}{self.colors['reset']}"
        
        # 3. Afficher de haut en bas
        for y in range(grid_height - 1, -1, -1):
            row_str = "".join(grid[y][x] + " " for x in range(grid_width))
            # On n'affiche pas la ligne si elle est totalement vide pour compacter
            if row_str.strip(): 
                print(row_str)
                
        print("\nLegend: S=Start E=End O=Normal R=Restricted P=Priority X=Blocked")
        print("-" * 50)
