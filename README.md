# 42_Fly-In

![Score](https://img.shields.io/badge/Score-125%2F100-success)
![Language](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)
![Algorithms](https://img.shields.io/badge/Algorithm-A*_&_Dijkstra-FF6B6B)

## 📋 Table of Contents
- [Description](#description)
- [Project Architecture](#project-architecture)
- [Modules Overview](#modules-overview)
  - [Module 1 — Map Parser & Constraints](#module-1--map-parser--constraints)
  - [Module 2 — Pathfinding Engine](#module-2--pathfinding-engine)
  - [Module 3 — Reservation & Conflict System](#module-3--reservation--conflict-system)
  - [Module 4 — Simulation Engine](#module-4--simulation-engine)
- [Usage](#usage)
- [Author](#author)

## 🔍 Description

**Fly-In** is a multi-drone routing simulator developed as part of the 42 School curriculum. The objective is to design a system capable of guiding a fleet of autonomous agents from a starting point to a destination area, while strictly minimizing the total number of turns.

This project focuses heavily on advanced algorithmic problem-solving and multi-agent system management. It implements a **space-time A* pathfinding algorithm**, utilizing **Dijkstra’s algorithm** as a heuristic, combined with a robust reservation system to handle zone capacities and prevent conflicts.

Key features include:
- 🗺️ **Map Parsing**: Strict constraint validation for zones, connections, and capacities.
- 🧠 **Advanced Pathfinding**: Space-time A* (A-Star) with Dijkstra heuristics.
- 🚦 **Traffic Control**: Zone reservation system to prevent mid-air drone collisions.
- ⚙️ **Turn-Based Engine**: Simulation engine handling travel costs (normal, restricted, and priority zones).

## 📁 Project Structure

```text
42_Fly-In/
├── maps/              # Sample maps and test configurations
├── src/
│   ├── parser/        # Map parsing and validation logic
│   ├── pathfinding/   # A* space-time and Dijkstra algorithms
│   ├── simulation/    # Turn-based engine and conflict management
│   ├── models/        # Drone, Node, and Edge class definitions
│   └── utils/         # Helper functions (logging, math)
├── tests/             # Unit tests and performance benchmarks
├── main.py            # Entry point of the simulation
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## ⚙️ Modules Overview

---

### Module 1 — Map Parser & Constraints
> 🗺️ *Establishing the airspace*

| Component | Topic |
|-----------|-------|
| `map_parser.py` | Reading and validating strict map constraints |
| `validator.py` | Verifying zone capacities, connections, and start/end points |

**Key concepts:** File I/O, error handling, strict constraint validation, graph initialization.

---

### Module 2 — Pathfinding Engine
> 🧠 *Navigating the multi-dimensional grid*

| Component | Topic |
|-----------|-------|
| `dijkstra.py` | Implementing Dijkstra’s algorithm to pre-calculate distance heuristics |
| `astar_spacetime.py` | Space-time A* pathfinding to calculate optimal routes across 3 dimensions (X, Y, Time) |

**Key concepts:** Graph theory, heuristic optimization, priority queues (min-heaps), space-time grids.

---

### Module 3 — Reservation & Conflict System
> 🚦 *Managing the fleet safely*

| Component | Topic |
|-----------|-------|
| `reservation.py` | Zone and connection reservation management across time |
| `conflict_resolver.py` | Collision avoidance logic |

**Key concepts:** Multi-agent systems, resource locking, collision detection algorithms.

---

### Module 4 — Simulation Engine
> ⚙️ *Executing the flight plan*

| Component | Topic |
|-----------|-------|
| `engine.py` | Turn-based execution of drone movements |
| `cost_calculator.py` | Handling travel costs (normal, restricted, priority zones) |

**Key concepts:** Turn-based simulation, state machines, performance tracking (minimizing total turns).

---

## 💻 Usage

### Installation

Clone the repository and optionally set up a virtual environment:

```bash
git clone https://github.com/Vibes33/42_Fly-In.git
cd 42_Fly-In
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Simulator

Execute the simulation by providing a map file as an argument:

```bash
python3 main.py maps/test_map_01.txt
```

### Options & Flags

You can run the simulation with various flags to display specific outputs (adjust according to your actual code implementation):

```bash
python3 main.py maps/test_map_01.txt --verbose    # Detailed step-by-step logs
python3 main.py maps/test_map_01.txt --visualize  # (If implemented) graphical output
```

## 👨‍💻 Author

**Ryan Delepine (Vibes33 / rydelepi)** - 42 Student

---

*Created as part of the 42 School curriculum.*
