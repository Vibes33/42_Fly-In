from typing import Dict, List
from src.astar import State

class SimulationEngine:
    def __init__(self, paths: Dict[str, List[State]]):
        self.paths = paths

    def generate_output(self) -> int:
        if not self.paths:
            return 0
            
        max_time = max(len(p) for p in self.paths.values())
        total_turns = 0
        
        # On définit des couleurs via des codes ANSI pour le formatage
        C_TURN = "\033[1;36m"   # Cyan bold
        C_DRONE = "\033[1;33m"  # Yellow
        C_ZONE = "\033[0;32m"   # Green
        C_RESET = "\033[0m"
        
        for t in range(1, max_time):
            moves = []
            
            # On trie d'abord pour avoir D1, D2 etc plutôt que dans le désordre du dict
            sorted_drones = sorted(self.paths.keys(), key=lambda x: int(x[1:]))
            
            for d in sorted_drones:
                p = self.paths[d]
                if t < len(p):
                    prev = p[t-1]
                    curr = p[t]
                    
                    if prev.zone_name != curr.zone_name:
                        if prev.time + 1 < curr.time and prev.time + 1 == t:
                            # In transit to restricted (D1-A-B en respectant le sujet pour le parsing officiel, 
                            # mais pour un affichage joli de terminal, on peut colorer l'intérieur).
                            moves.append(f"{C_DRONE}{d}{C_RESET}-{C_ZONE}{prev.zone_name}-{curr.zone_name}{C_RESET}")
                        else:
                            moves.append(f"{C_DRONE}{d}{C_RESET}-{C_ZONE}{curr.zone_name}{C_RESET}")
                            
            if moves:
                total_turns += 1
                # Format plus joli : "Turn X: D1-zone D2-zone ..."
                print(f"{C_TURN}[Turn {total_turns:02d}]{C_RESET} " + " ".join(moves))
                
        print("\n" + "="*50)
        print(f"✅ Simulation Finished in {total_turns} turns!")
        print("="*50 + "\n")
        return total_turns
