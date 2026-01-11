import socket
import json
import time
import random
import sys
import os
from colorama import Fore, Back, Style, init

# --- 1. DYNAMIC IMPORTS OF YOUR "A" SERIES SCRIPTS ---
try:
    import A1_phish as mod_phish
    import A2_sqli as mod_sql
    import A3_quic as mod_quic
    import A4_poly as mod_c2        
    import A5_poly as mod_path       
    import A6_xss as mod_xss
    import A7_portscan as mod_scan
    import A8_sshbf as mod_brute
    import A9_user_spoof as mod_spoof
    import A10_syn_flood as mod_flood
except ImportError as e:
    print(f"{Fore.RED}[CRITICAL] Missing attack module: {e}")
    print(f"{Fore.YELLOW}Current directory must contain: A1_phish.py ... A10_syn_flood.py")
    sys.exit(1)

# Ensure rl_agent.py is present
try:
    from rl_agent import QLearningAgent
except ImportError:
    print(f"{Fore.RED}[CRITICAL] rl_agent.py not found. Please create it first.")
    sys.exit(1)

# --- CONFIGURATION ---
# IMPORTANT: Ensure this matches the Blue Team Pi's actual IP!
TARGET_IP = "100.67.198.107"   
TARGET_PORT = 6000             
STATE = "ACTIVE_CAMPAIGN" 

# --- ACTION MAPPING ---
ACTION_MAP = {
    0: ("PHISHING", mod_phish, "generate_attack"),
    1: ("SQL INJECTION", mod_sql, "generate_attack"),
    2: ("QUIC FLOOD", mod_quic, "generate_attack"),
    3: ("C2 BEACON", mod_c2, "generate_beacon"),      
    4: ("PATH TRAVERSAL", mod_path, "generate_attack"),
    5: ("XSS ATTACK", mod_xss, "generate_attack"),
    6: ("PORT SCAN", mod_scan, "generate_scan"),      
    7: ("SSH BRUTE FORCE", mod_brute, "generate_attack"),
    8: ("HEADER SPOOFING", mod_spoof, "generate_spoof"), 
    9: ("SYN FLOOD", mod_flood, "generate_attack")
}

ACTIONS = list(ACTION_MAP.keys())

init(autoreset=True)

def get_payload_for_action(action_index):
    """
    Dynamically calls the correct generation function for the selected module.
    """
    name, module, func_name = ACTION_MAP[action_index]
    
    # Check if module has the expected function
    if not hasattr(module, func_name):
        if hasattr(module, "generate_attack"): func_name = "generate_attack"
        elif hasattr(module, "generate_payload"): func_name = "generate_payload"
        else:
            print(f"{Fore.RED}[!] Error: Function {func_name} not found in {module.__name__}")
            return None

    generator = getattr(module, func_name)

    try:
        if name == "PHISHING":
            return generator(random.choice(["finance", "hr", "it", "ceo"]))
        elif name == "SQL INJECTION":
            return generator(random.choice(["union", "error", "blind", "time"]))
        elif name == "QUIC FLOOD":
            return generator(random.choice(["volumetric", "handshake"]))
        elif name == "C2 BEACON":
            return generator(random.choice(["jitter", "dga", "dns"]))
        elif name == "PATH TRAVERSAL":
            return generator(random.choice(["standard", "encoding", "absolute"]))
        elif name == "XSS ATTACK":
            return generator(random.choice(["reflected", "stored", "dom"]))
        elif name == "PORT SCAN":
            return generator(random.choice(["syn", "connect", "version"]))
        elif name == "SSH BRUTE FORCE":
            return generator(random.choice(["dictionary", "spray", "hybrid"]))
        elif name == "HEADER SPOOFING":
            return generator(random.choice(["bot", "mobile", "legacy"]))
        elif name == "SYN FLOOD":
            return generator(random.choice(["standard", "spoof", "distributed"]))
    except Exception as e:
        print(f"{Fore.RED}[!] Payload Gen Error ({name}): {e}")
        return None

    return None

def main():
    agent = QLearningAgent(actions=ACTIONS)
    
    print(f"{Fore.RED}{Style.BRIGHT}" + "="*50)
    print(f"{Fore.RED}{Style.BRIGHT}   RED TEAM AUTONOMOUS AGENT (RL CORE)")
    print(f"{Fore.RED}{Style.BRIGHT}   Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"{Fore.RED}{Style.BRIGHT}" + "="*50 + "\n")
    
    if os.path.exists("q_table.pkl"):
        agent.load_model()
        print(f"{Fore.GREEN}[*] Loaded previous Q-Table brain.")

    episode = 0
    try:
        while True:
            episode += 1
            print(f"\n{Fore.CYAN}{'-'*40}")
            print(f"{Fore.CYAN}EPISODE {episode} | Epsilon: {agent.epsilon:.3f}")

            # 1. AI SELECTS ATTACK
            action_idx = agent.choose_action(STATE)
            attack_name, _, _ = ACTION_MAP[action_idx]
            print(f"{Fore.MAGENTA}[AI DECISION] Vector Selected: {attack_name}")

            # 2. GENERATE PAYLOAD
            payload_data = get_payload_for_action(action_idx)
            if not payload_data:
                print(f"{Fore.RED}[!] Failed to generate payload. Skipping.")
                continue

            # INJECT EPSILON FOR DASHBOARD
            payload_data["epsilon"] = agent.epsilon 

            # Initialize reward to 0 to prevent UnboundLocalError
            reward = 0 

            # 3. ATTACK & LEARN
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # REMOVED: s.settimeout(5) <-- This was causing the Phishing crash
                    s.connect((TARGET_IP, TARGET_PORT))
                    
                    # Transmit
                    s.sendall(json.dumps(payload_data).encode('utf-8'))
                    print(f"{Fore.GREEN}[->] Payload transmitted.")

                    # Wait for Reward (Feedback)
                    # No timeout means it will wait until Blue Team is done thinking
                    response_data = s.recv(4096)
                    
                    if not response_data:
                        print(f"{Fore.RED}[!] Connection closed without feedback.")
                        reward = 0
                    else:
                        response_json = json.loads(response_data.decode('utf-8'))
                        reward = response_json.get("reward", 0)
                        status = response_json.get("status", "UNKNOWN")
                        
                        # Colorize output based on success
                        r_color = Fore.GREEN if reward > 0 else Fore.RED
                        print(f"{Fore.BLUE}[<-] BLUE TEAM FEEDBACK:")
                        print(f"    Status: {Style.BRIGHT}{status}")
                        print(f"    Reward: {r_color}{reward}{Style.RESET_ALL}")

                    # UPDATE BRAIN
                    agent.learn(STATE, action_idx, reward, STATE)

            except ConnectionRefusedError:
                print(f"{Fore.RED}[CRITICAL] Connection Refused. Is the Blue Team (app.py) running?")
                time.sleep(5)
                continue 
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Network error: {e}")

            # Dynamic sleep based on result
            sleep_time = 1.0 if reward > 0 else 2.5
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[*] Training interrupted. Saving Agent Brain...")
        agent.save_model()
        print(f"{Fore.GREEN}[*] Saved to q_table.pkl. Exiting.")

if __name__ == "__main__":
    main()
