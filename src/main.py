import sys
import argparse
from src.parser import MapParser
from src.algorithm import Router
from src.exceptions import ParsingError
from src.Visualizer import Visual
from typing import Dict, List, Tuple


def main() -> None:

    parser = argparse.ArgumentParser(description="Fly-in Drone Routing")
    parser.add_argument("map_file", type=str, help="Path to the map file")
    parser.add_argument("--capacity-info", action="store_true",
                        help="Displays capacity info")
    args = parser.parse_args()

    try:
        # 1. Parsing
        map_parser = MapParser(args.map_file)
        map_data = map_parser.parse()

        status = Visual.check_dependencies()
        if not Visual.show_status(status):
            print(
                "Warning: Dependencies for GUI visualization are missing.",
                file=sys.stderr
            )

        # Héristique et Routage
        router = Router(map_data)
        router.compute_true_distance_heuristic()
        max_turns = 0

        # Drones successifs astar
        all_paths: Dict[int, List[Tuple[str, int]]] = {}
        for drone_id in range(1, map_data.nb_drones + 1):
            path = router.space_time_a_star(start_time=0)

            if not path:
                print(
                    f"Error: Could not find path for Drone {drone_id}",
                    file=sys.stderr
                )
                sys.exit(1)

            router.reserve_path(path)
            all_paths[drone_id] = path

            drone_finish_time = path[-1][1]
            if drone_finish_time > max_turns:
                max_turns = drone_finish_time

        # affichage terminal
        turn_events: Dict[int, List[str]] = {}
        for drone_id, path in all_paths.items():
            for i in range(1, len(path)):
                prev_zone, prev_t = path[i - 1]
                curr_zone, curr_t = path[i]

                if prev_zone != curr_zone:
                    for t in range(prev_t + 1, curr_t):
                        if t not in turn_events:
                            turn_events[t] = []
                        c_info = f" ({router.get_edge_occupancy(prev_zone, curr_zone, t)}/{router.map_data.get_connection_capacity(prev_zone, curr_zone)})" if args.capacity_info else ""
                        turn_events[t].append(f"D{drone_id}-{prev_zone}-{curr_zone}{c_info}")

                    if curr_t not in turn_events:
                        turn_events[curr_t] = []
                    z_info = f" ({router.get_zone_occupancy(curr_zone, curr_t)}/{router.map_data.zones[curr_zone].max_drones})" if args.capacity_info else ""
                    turn_events[curr_t].append(f"D{drone_id}-{curr_zone}{z_info}")

        for t in range(1, max_turns + 1):
            if t in turn_events and turn_events[t]:
                print(
                    f"\033[94mTurn {t:02d} |\033[0m "
                    + " ".join(turn_events[t])
                )

        print(
            f"\n\033[92mSimulation completed in {max_turns} turns.\033[0m"
        )

        # Affichage graphique direct
        try:
            visual = Visual(map_data)
            visual.visualizer()
        except ImportError:
            print("Import Error : Map not generated", file=sys.stderr)
            pass

    except ParsingError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user (Ctrl+C).", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
