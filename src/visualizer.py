import importlib
import sys
from src.models import MapData

class Visual:
    def __init__(self, map_data: MapData):
        self.map_data = map_data
        self.positions = {}
        self.node_colors = []
        self.node_sizes = []
        self.labels = {}


    @staticmethod
    def check_dependencies() -> dict:
        status = {}
        try:
            import matplotlib
            status["matplotlib"] = {"ok": True, "version": matplotlib.__version__, "desc": "Visualization"}
        except ImportError:
            status["matplotlib"] = {"ok": False, "version": "N/A", "desc": "Visualization"}
        return status

    @staticmethod
    def show_status(status: dict) -> bool:
        REQUIRED = { "matplotlib": "Visualization" }
        all_ok = True
        for pkg, info in status.items():
            if info["ok"]:
                pass
            else:
                print(f"  [MISSING] {pkg} - {info['desc']} NOT available")
                all_ok = False
        return all_ok

    def extract_rendering_data(self):        
        start_hub = self.map_data.start_hub
        end_hub = self.map_data.end_hub

        for zone_name, zone_obj in self.map_data.zones.items():
            self.positions[zone_name] = (zone_obj.x, zone_obj.y)
            
            self.labels[zone_name] = zone_name

            if zone_name == start_hub:
                self.node_colors.append('lightgreen')
            elif zone_name == end_hub:
                self.node_colors.append('salmon')
            elif zone_obj.zone_type == "blocked":
                self.node_colors.append('black')
            elif zone_obj.zone_type == "restricted":
                self.node_colors.append('orange')
            else:
                self.node_colors.append('lightblue')

            self.node_sizes.append(1000 if zone_name in (start_hub, end_hub) else 500)

    def visualizer(self):
        self.extract_rendering_data() 
        
        import matplotlib.pyplot as plt
        plt.rcParams['toolbar'] = 'None'

        fig, ax = plt.subplots(figsize=(10, 8))
        fig.canvas.manager.set_window_title('Fly-In - Visualisateur de Carte')
        ax.set_title(f"Fly-In Map : {self.map_data.nb_drones} Drones prévus", fontsize=14, fontweight='bold', pad=20)

        for conn in self.map_data.connections:
            if conn.zone1 in self.positions and conn.zone2 in self.positions:
                x1, y1 = self.positions[conn.zone1]
                x2, y2 = self.positions[conn.zone2]

                ax.plot([x1, x2], [y1, y2], color='gray', linestyle='dashed', linewidth=2, zorder=1)

        x_coords = [self.positions[zone][0] for zone in self.map_data.zones.keys()]
        y_coords = [self.positions[zone][1] for zone in self.map_data.zones.keys()]
        
        ax.scatter(x_coords, y_coords, s=self.node_sizes, c=self.node_colors, 
                   edgecolors='black', linewidths=1.5, zorder=2)

        for zone_name, (x, y) in self.positions.items():
            ax.text(x, y, zone_name, fontsize=9, ha='center', va='center', fontweight='bold', zorder=3)

        ax.axis('off')

        plt.tight_layout()
        plt.show()