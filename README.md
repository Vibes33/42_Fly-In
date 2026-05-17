*This project has been created as part of the 42 curriculum by rydelepi.*

# Fly-In: Drone Routing Simulation

## Description
Fly-In is a drone routing and simulation program. The goal of the project is to compute and simulate collision-free paths for a fleet of drones flying from a departure hub to a destination point across a network of zones (waypoints). The simulation respects strict capacity constraints:
- **Zone Capacity:** The maximum number of drones allowed in a specific zone at a given time.
- **Connection Capacity:** The maximum number of drones that can travel on an edge/path between two zones at a given time.

The project validates structural constraints, plans the fastest safe route for each drone, and visually displays the map infrastructure and flight logs per turn.

## Instructions

### Prerequisites
- Python 3.x
- `make`

### Installation
To install the required Python dependencies (like `matplotlib` for the visualizer), run:
```bash
make install
```

### Execution
To run the simulation on a specific map, use the provided `Makefile`:
```bash
make run maps/easy/01_linear_path.txt
```
Alternatively, you can run the script directly:
```bash
./src/main.py maps/easy/01_linear_path.txt
```

### Options
To display real-time capacity information (drones moving and arriving vs maximum capacity) turn-by-turn:
```bash
make run maps/easy/01_linear_path.txt ARGS="--capacity-info"
# or
./src/main.py --capacity-info maps/easy/01_linear_path.txt
```

### Linting and Checks
To run style checks (`flake8`) and static type checking (`mypy`):
```bash
make lint
```

## Algorithm Choices and Implementation Strategy
The core routing relies on a **Space-Time A\*** (Cooperative A*) algorithm. The implementation strategy guarantees safe paths for multiple agents:
1. **Heuristic Pre-computation:** A backwards Dijkstra (or true-distance A*) is first run from the destination hub to compute exact distance heuristics for every zone.
2. **Time-Expanded Network:** The A* algorithm state is represented not just by physical location `(zone)`, but by `(zone, time)`.
3. **Sequential Routing & Reservations:** Drones are routed one by one. Once a drone finds a path, it reserves the zones and connections it uses at the specific time steps in `zone_reservations` and `edge_reservations`.
4. **Collision Avoidance:** Subsequent drones check these reservation tables. If moving to an adjacent node (or waiting in place) exceeds the `max_drones` of a zone or the capacity of a connection during that turn, the state is deemed invalid, forcing the drone to wait or take an alternate route.

## Visual Representation Features
The project features a graphical representation of the map using `matplotlib`. 
- **Topology Display:** Provides a topological graph of hubs and waypoints, giving an immediate understanding of the map constraints and complexity.
- **Color-Coding:** Zones are intuitively color-coded to enhance the user experience:
  - **Light Green:** Start Hub
  - **Salmon:** Destination Hub
  - **Black:** Blocked Zones
  - **Orange:** Restricted Zones
  - **Light Blue:** Standard Waypoints
- **Visual Feedback:** This UI complements the terminal logs, bridging the gap between abstract routing data and physical spatial awareness.

## Resources
- **Algorithms:** 
  - [A* Search Algorithm (Wikipedia)](https://en.wikipedia.org/wiki/A*_search_algorithm)
  - [Multi-Agent Path Finding (MAPF)](https://en.wikipedia.org/wiki/Multi-agent_path_finding)
- **AI Usage:** 
  - Generative AI was used throughout the development process for specific tasks including:
    - Assisting with the refactoring and optimization of the `reserve_path` and `args` capacity display functions to make them cleaner and more idiomatic.
    - Adding extensive static type hinting (typing) and resolving `mypy` / `flake8` compliance issues.
    - Adjusting the `Makefile` parameters correctly to prevent parameter collision with standard GNU Make arguments.