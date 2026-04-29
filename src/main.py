import sys
import argparse
from src.parser import MapParser
from src.algorithm import Router
from src.exceptions import ParsingError
from src.Visualizer import Visual


def main() -> None:

    parser = argparse.ArgumentParser(description="Fly-in Drone Routing")
    parser.add_argument("map_file", type=str, help="Path to the map file")

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
        all_paths = {}
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
        turn_events = {}
        for drone_id, path in all_paths.items():
            for i in range(1, len(path)):
                prev_zone, prev_t = path[i - 1]
                curr_zone, curr_t = path[i]

                if prev_zone != curr_zone:
                    for t in range(prev_t + 1, curr_t):
                        if t not in turn_events:
                            turn_events[t] = []
                        turn_events[t].append(
                            f"D{drone_id}-{prev_zone}-{curr_zone}"
                        )

                    if curr_t not in turn_events:
                        turn_events[curr_t] = []
                    turn_events[curr_t].append(f"D{drone_id}-{curr_zone}")
        for t in range(1, max_turns + 1):
            if t in turn_events and turn_events[t]:
                # \033[94m = Light Blue, \033[0m = Reset
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
