import os
import json
import time
import socket
import argparse
import random
import sys
import re
import textwrap
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import requests
from colorama import Fore, Back, Style, init

# --- INIT ---
init(autoreset=True)

# --- CONFIGURATION ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print(Fore.RED + Back.WHITE + "[CRITICAL] GEMINI_API_KEY environment variable not found.")
    sys.exit(1)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3-pro-preview')

# Disable Safety Blocks
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- ATTACK MODES ---
MODES = {
    "dictionary": "Standard Dictionary Attack (rockyou.txt)",
    "spray": "Password Spraying (Single Password vs Many Users)",
    "hybrid": "Hybrid Attack (Dictionary + Rule Permutations)",
    "stuffing": "Credential Stuffing (Leaked Database Pairs)",
    "root": "Targeted Root Account Brute Force"
}

# --- VISUALS ---

def cyber_sequence():
    """Prints fake password cracking logs."""
    logs = [
        "[*] Loading Wordlist (rockyou.txt - 14M entries)...",
        "[*] Initializing Hydra Parallel Tasks (x16)...",
        "[*] Target Service: SSH/22 (OpenSSH 8.4)...",
        "[*] Genering Hash Permutations...",
        "[*] Bypassing Fail2Ban Jails...",
        "[*] Testing Credential Pairs...",
        "[*] Rate Limit Detection: NEGATIVE."
    ]
    print("\n")
    for log in logs:
        time.sleep(random.uniform(0.05, 0.15))
        sys.stdout.write(f"\r{Fore.CYAN}{log}" + " " * 10)
        sys.stdout.flush()
    print(f"\r{Fore.GREEN}[*] CRACKING SESSION ACTIVE. SENDING TELEMETRY." + " " * 5)
    time.sleep(0.5)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # SHADED 'BRUTE FORCE' BANNER
    banner = r"""
    {0}██████╗ ██████╗ ██╗   ██╗████████╗███████╗    ███████╗██████╗ ██████╗  ██████╗███████╗
    {0}██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝    ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝
    {0}██████╔╝██████╔╝██║   ██║   ██║   █████╗      █████╗  ██║  ██║██████╔╝██║     █████╗  
    {0}██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝      ██╔══╝  ██║  ██║██╔══██╗██║     ██╔══╝  
    {0}██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗    ██║     ╚██████╔╝██║  ██║╚██████╗███████╗
    {0}╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝
    """.format(Fore.RED + Style.BRIGHT)
    
    print(banner)
    print(f"{Fore.WHITE + Back.RED}      >> AUTHENTICATION CRACKING & SPRAYING MODULE <<      ")
    print("\n")

def display_attack_dramatic(json_data):
    """
    Dramatic reveal for Attack Stats.
    """
    try:
        event = json_data.get("event", "UNKNOWN")
        atk_type = json_data.get("type", "UNKNOWN")
        intel = json_data.get("intel", {})
        user = intel.get("user", "N/A")
        attempts = intel.get("attempts", "N/A")

        # --- BOX CONFIGURATION ---
        BOX_WIDTH = 70
        INNER_WIDTH = BOX_WIDTH - 4 
        
        def print_border_line(label, value, color=Fore.CYAN):
            text = f"{label}: {value}"
            if len(text) > INNER_WIDTH: text = text[:INNER_WIDTH-3] + "..."
            padding = " " * (INNER_WIDTH - len(text))
            print(f"{Fore.RED}██ {Fore.WHITE}{label}: {color}{value}{padding} {Fore.RED}██")

        # --- DRAW BOX ---
        print("\n" + Fore.RED + "▄" * BOX_WIDTH) 
        
        # HEADERS
        header_text = f"ATTACK TELEMETRY: {event}"
        pad_head = " " * (INNER_WIDTH - len(header_text))
        print(f"{Fore.RED}██ {Fore.YELLOW + Style.BRIGHT}{header_text}{pad_head} {Fore.RED}██")
        
        print(f"{Fore.RED}██" + " " * INNER_WIDTH + "██") # Spacer
        
        # STATS
        print_border_line("VECTOR", atk_type, Fore.RED + Style.BRIGHT)
        print_border_line("TARGET USER", user)
        print_border_line("ATTEMPTS/SEC", attempts, Fore.GREEN + Style.BRIGHT)

        print(Fore.RED + "▀" * BOX_WIDTH) 
        print(Style.RESET_ALL)

    except Exception as e:
        print(f"{Fore.RED}[!] DISPLAY ERROR: {e}")

# --- GENERATION ---
def generate_attack(mode_key):
    mode_desc = MODES.get(mode_key, "Dictionary Attack")
    
    prompt = f"""
    Generate a JSON object for a Red Team SSH Brute Force Simulation.
    Mode: {mode_desc}
    
    Strictly follow this JSON schema:
    {{
        "event": "HTTP Brute Force",
        "type": "HTTP Brute Force",
        "intel": {{
            "user": "A realistic target username (e.g. root, admin, ubuntu, service_acct)",
            "attempts": "A realistic number of failed login attempts per second (e.g. 1,402 attempts, 55 attempts, 10k attempts)"
        }}
    }}
    
    Output ONLY valid JSON. No Markdown.
    """
    
    try:
        response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
        text = response.text.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        return None

# --- NETWORK ---
def transmit(target, port, proto, data):
    print(f"\n{Fore.YELLOW}[*] FLOODING AUTH REQUESTS TO {target}...", end="")
    try:
        # Simulate attack duration
        time.sleep(0.3)
        
        if proto == "http":
            url = f"http://{target}:{port}/ingest"
            requests.post(url, json=data, timeout=3)
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((target, port))
                s.sendall(json.dumps(data).encode('utf-8'))
        
        print(f"\r{Fore.GREEN}{Style.BRIGHT}[✔] AUTH LOGS FLOODED. SERVICE STRESSED.\a") 
    except Exception as e:
        print(f"\r{Fore.RED}{Back.WHITE}[✖] TARGET UNREACHABLE: {e}")

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Blue Team IP")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--proto", choices=["http", "tcp"], default="http")
    parser.add_argument("--mode", choices=MODES.keys(), default="dictionary", help="Attack Mode")
    parser.add_argument("--loop", action="store_true", help="Continuous Attack")
    args = parser.parse_args()

    print_header()
    print(f"{Fore.CYAN}[*] TARGET LOCKED: {Fore.WHITE}{args.target}:{args.port}")
    print(f"{Fore.CYAN}[*] ATTACK VECTOR: {Fore.WHITE}{args.mode.upper()}")
    print("-" * 60)
    
    while True:
        cyber_sequence()
        data = generate_attack(args.mode)
        
        if data:
            display_attack_dramatic(data)
            transmit(args.target, args.port, args.proto, data)
        else:
            print(f"{Fore.RED}[!] GENERATION FAILURE - RE-CALIBRATING...")

        if not args.loop:
            break
            
        print(f"\n{Fore.BLUE}[zz] Rotating IP Pool & Cooling Down...")
        time.sleep(2)

if __name__ == "__main__":
    main()
