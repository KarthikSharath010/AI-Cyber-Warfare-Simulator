import sys
import time
import random
import json

# 1. Get the attack type from Node.js (passed as an argument)
attack_type = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

def run_simulation():
    # --- RED TEAM PHASE ---
    # We print these so Node.js can capture them as "logs"
    print(f"[RED] Initializing {attack_type} sequence...")
    time.sleep(1) # Simulate processing
    print(f"[RED] Target locked. Injecting payload...")
    time.sleep(1)

    # --- BLUE TEAM PHASE (The Logic from your notes) ---
    # 70% chance of detection (Higher difficulty attacks could lower this)
    # In a real app, this would check firewall logs. Here, we simulate the logic.
    blue_team_detected = random.random() > 0.3 

    result = {}

    if blue_team_detected:
        # --- BLOCKED SCENARIO ---
        print(f"[BLUE] Anomaly detected in traffic pattern.")
        time.sleep(0.5)
        print(f"[BLUE] Signature match found for {attack_type}.")
        
        result = {
            "status": "BLOCKED",
            "red_log": f"[-] Connection Reset. Payload rejected by WAF.",
            "blue_log": f"[SUCCESS] Threat mitigated. Source IP shunted."
        }
    else:
        # --- BREACH SCENARIO ---
        print(f"[BLUE] Traffic analysis nominal. No threats found.")
        
        result = {
            "status": "BREACH",
            "red_log": f"[+] Access Granted. Shell established.",
            "blue_log": f"[CRITICAL] Unknown process started with ROOT privileges."
        }

    # Print the final result as JSON so Node can read it easily
    print(json.dumps(result))

if __name__ == "__main__":
    run_simulation()