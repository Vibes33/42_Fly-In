import sys
from src.parser import MapParser
from src.visualizer import TerminalVisualizer
# On utilise PrioritizedPlanner en mode ultra rapide. 
# On peut laisser ICBS en import si jamais on souhaite faire un hybrid.
from src.pp import PrioritizedPlanner
from src.simulator import SimulationEngine

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m src.main <path_to_map>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        parser = MapParser(filepath)
        map_data = parser.parse()

        visualizer = TerminalVisualizer()
        visualizer.draw_map(map_data)

        # Utilisation de la planification priorisée (très rapide)
        solver = PrioritizedPlanner(map_data)
        final_paths = solver.solve()

        simulator = SimulationEngine(final_paths)
        simulator.generate_output()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
