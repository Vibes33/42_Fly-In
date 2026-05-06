class ParsingError(Exception):
    def __init__(self, message: str, line_num: int):
        super().__init__(f"Parsing Error at line {line_num}: {message}")


def args(map_data, all_paths, max_turns, turn_events):
    print(
        "\n\033[96m--- Capacity Information "
        "(Drones en mouvement/arrivés) ---\033[0m"
    )
    arrival_times = [path[-1][1] for path in all_paths.values()]
    for t in range(1, max_turns + 1):
        if t in turn_events and turn_events[t]:
            zone_stats = {}
            for event in turn_events[t]:
                # Extrait la zone ou le chemin (ex: Z1 ou Z1-Z2) depuis "D1-Z1"
                parts = event.split('-')
                if len(parts) == 2:
                    zone = parts[1]
                    zone_stats[zone] = zone_stats.get(zone, 0) + 1
                elif len(parts) >= 3:
                    edge = f"{parts[1]}-{parts[2]}"
                    zone_stats[edge] = zone_stats.get(edge, 0) + 1

            drones_arrived = sum(1 for arr_t in arrival_times if arr_t <= t)
            if drones_arrived > 0:
                zone_stats[map_data.end_hub] = drones_arrived

            stats_list = []
            for loc, count in sorted(zone_stats.items()):
                parts = loc.split('-')
                if len(parts) == 1:
                    if loc == map_data.end_hub:
                        stats_list.append(
                            f"Zone {loc}: {drones_arrived}/"
                            f"{map_data.nb_drones} drones arrivés"
                        )
                    else:
                        max_cap = map_data.zones[loc].max_drones
                        stats_list.append(
                            f"Zone {loc}: {count}/{max_cap} drones"
                        )
                else:
                    max_cap = map_data.get_connection_capacity(
                        parts[0], parts[1]
                    )
                    stats_list.append(
                        f"Connection {loc}: {count}/{max_cap} capacity used"
                    )

            stats_str = " | ".join(stats_list)
            print(f"\033[96mTurn {t:02d} |\033[0m {stats_str}")
    print("\n\033[93m--- Détail des Événements ---\033[0m")
