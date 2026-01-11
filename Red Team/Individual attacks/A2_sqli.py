import os
import json
import time
import socket
import argparse
import random
import sys
import threading
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
    "union": "Union-Based SQL Injection (Data Extraction)",
    "error": "Error-Based SQL Injection (Database Recon)",
    "blind": "Boolean-Based Blind Injection (True/False Tests)",
    "time": "Time-Based Blind Injection (Sleep/Delay Tests)",
    "auth": "Authentication Bypass (Login Flaws)"
}

# --- VISUALS ---

def cyber_sequence():
    """Prints fake SQL-specific hacking logs."""
    logs = [
        "[*] Fingerprinting Database Backend (MySQL/PostgreSQL)...",
        "[*] Fuzzing Input Parameters (?id=)...",
        "[*] Detecting WAF Signatures...",
        "[*] Injecting Heuristic Payloads...",
        "[*] Enumerating Table Schema...",
        "[*] Calculating Column Count...",
        "[*] Attempting Union Select..."
    ]
    print("\n")
    for log in logs:
        time.sleep(random.uniform(0.05, 0.15))
        sys.stdout.write(f"\r{Fore.CYAN}{log}" + " " * 10)
        sys.stdout.flush()
    print(f"\r{Fore.GREEN}[*] VULNERABILITY CONFIRMED. PAYLOAD READY." + " " * 10)
    time.sleep(0.5)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # FULLY SHADED BLOCK BANNER
    banner = r"""
    {0}███████╗ ██████╗ ██╗          ██╗
    {0}██╔════╝██╔═══██╗██║          ██║
    {0}███████╗██║   ██║██║    ██    ██║
    {0}╚════██║██║   ██║██║          ██║
    {0}███████║╚██████╔╝███████╗     ██║
    {0}╚══════╝ ╚═════╝ ╚══════╝     ╚═╝
    """.format(Fore.RED + Style.BRIGHT)
    
    print(banner)
    print("\n")

def display_payload_dramatic(json_data):
    """
    Dramatic reveal for SQL payloads.
    """
    try:
        payload = json_data.get("payload", "")
        target = json_data.get("intel", {}).get("target", "Unknown")
        method = json_data.get("intel", {}).get("method", "Unknown")
        atk_type = json_data.get("type", "UNKNOWN")

        # --- BOX CONFIGURATION ---
        BOX_WIDTH = 80
        INNER_WIDTH = BOX_WIDTH - 4 
        
        def print_border_line(text, color=Fore.YELLOW):
            if len(text) > INNER_WIDTH:
                text = text[:INNER_WIDTH-3] + "..."
            padding = " " * (INNER_WIDTH - len(text))
            print(f"{Fore.RED}██ {color}{text}{padding} {Fore.RED}██") # Used Block for borders too

        # --- DRAW BOX ---
        print("\n" + Fore.RED + "▄" * BOX_WIDTH) # Solid Top Block
        
        # HEADERS
        print_border_line(f"SQL INJECTION PAYLOAD GENERATED", Fore.WHITE + Style.BRIGHT)
        print_border_line("-" * INNER_WIDTH, Fore.RED)
        print_border_line(f"TYPE:     {atk_type}", Fore.CYAN)
        print_border_line(f"TARGET:   {target}", Fore.CYAN)
        print_border_line(f"METHOD:   {method}", Fore.CYAN)
        print_border_line("-" * INNER_WIDTH, Fore.RED)
        
        # PAYLOAD (The Code)
        wrapped_lines = textwrap.wrap(payload, width=INNER_WIDTH)
        
        for line in wrapped_lines:
            sys.stdout.write(f"{Fore.RED}██ {Fore.GREEN}") 
            for char in line:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.005) 
            
            padding_len = INNER_WIDTH - len(line)
            print(" " * padding_len + f" {Fore.RED}██")

        print(Fore.RED + "▀" * BOX_WIDTH) # Solid Bottom Block
        print(Style.RESET_ALL)

    except Exception as e:
        print(f"{Fore.RED}[!] DISPLAY ERROR: {e}")

# --- GENERATION ---
def generate_attack(mode_key):
    mode_desc = MODES.get(mode_key, "Generic SQL Injection")
    
    prompt = f"""
    Generate a JSON object for a Red Team SQL Injection Simulation.
    Mode: {mode_desc}
    
    Strictly follow this JSON schema:
    {{
        "event": "SQL INJECTION",
        "type": "SQL INJECTION",
        "payload": "Generate a realistic raw SQL injection payload string here (e.g. ' UNION SELECT user, password FROM users--). Do not include explanation text.",
        "intel": {{
            "target": "A fake database table or column being targeted (e.g. users, admin_creds, vpn_keys)",
            "method": "The simulated tool or technique (e.g. sqlmap, manual, Havij)"
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
    print(f"\n{Fore.YELLOW}[*] INJECTING PAYLOAD TO {target}...", end="")
    try:
        time.sleep(0.3)
        
        if proto == "http":
            url = f"http://{target}:{port}/ingest"
            requests.post(url, json=data, timeout=3)
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((target, port))
                s.sendall(json.dumps(data).encode('utf-8'))
        
        print(f"\r{Fore.GREEN}{Style.BRIGHT}[✔] INJECTION SUCCESSFUL.\a") 
    except Exception as e:
        print(f"\r{Fore.RED}{Back.WHITE}[✖] CONNECTION REFUSED: {e}")

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Blue Team IP")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--proto", choices=["http", "tcp"], default="tcp")
    parser.add_argument("--mode", choices=MODES.keys(), default="union", help="Injection Type")
    parser.add_argument("--loop", action="store_true", help="Continuous Attack")
    args = parser.parse_args()

    print_header()
    print(f"{Fore.CYAN}[*] TARGET ACQUIRED: {Fore.WHITE}{args.target}:{args.port}")
    print(f"{Fore.CYAN}[*] INJECTION MODE:  {Fore.WHITE}{args.mode.upper()}")
    print("-" * 60)
    
    while True:
        cyber_sequence()
        data = generate_attack(args.mode)
        
        if data:
            display_payload_dramatic(data)
            transmit(args.target, args.port, args.proto, data)
        else:
            print(f"{Fore.RED}[!] GENERATION FAILURE - RETRYING...")

        if not args.loop:
            break
            
        print(f"\n{Fore.BLUE}[zz] Rotating User-Agents & Cooling Down...")
        time.sleep(3)

if __name__ == "__main__":
    main()
