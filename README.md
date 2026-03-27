*This project has been created as part of the 42 curriculum by ryan*

# Fly-in
Design an efficient drone routing system that navigates multiple drones through connected zones while minimizing simulation turns and handling movement constraints.

## Goal
Moving a fleet of drones from a start zone to an end zone in the fewest possible turns without breaking zone capacities and constraints.

## Instructions
1. Run `make install` to install basic python stuff natively (if there were any). No external graph libs.
2. Run `make run` to launch on default map.
3. Run `python3 -m src.main <path_to_map>` manually to run a specific map.
4. Run `make lint` to type check and lint.

## Algorithms
- **CBS (Conflict-Based Search)**: Used to solve path finding for multip-agents in a global optimal choregraphy.
  - A low-level Space-Time A* is searching path for standard drones ignoring each others.
  - A high-level searches for vertex and edges conflicts per frames, and branches constraint-trees to solve constraints smoothly.
  
## Visualizer
Colorized output is placed on top of simulation for more understandable node maps visualization showing drone capacities and zones.

## AI using
AI was mostly used for generating boilerplate structures like typing variables, checking flake8 and mypy structures and preparing the AST node trees and regex templates.
