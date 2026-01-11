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
# Using standard flash model for speed
model = genai.GenerativeModel('gemini-3-pro-preview')

# Disable Safety Blocks
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- C2 BEACON MODES ---
MODES = {
    "jitter": "High Jitter HTTP/S Beaconing (Randomized Sleep)",
    "dga": "Domain Generation Algorithm (Random High-Entropy Domains)",
    "smb": "Lateral Movement via SMB Named Pipes (Peer-to-Peer)",
    "dns": "Low-and-Slow DNS Tunneling (TXT Record Exfiltration)",
    "steg": "Steganography-based C2 (Hidden in JPG/PNG headers)"
}

# --- VISUALS ---

def cyber_sequence():
    """Prints fake C2 beaconing logs."""
    logs = [
        "[*] Rotating Encryption Keys (AES-256)...",
        "[*] Calculating Jitter Offset (±24%)...",
        "[*] Obfuscating Memory Signatures...",
        "[*] Resolving Next-Hop Proxy...",
        "[*] Injecting Malleable C2 Profile...",
        "[*] Awaiting Sleep Cycle Completion...",
        "[*] Heartbeat Sent."
    ]
    print("\n")
    for log in logs:
        time.sleep(random.uniform(0.05, 0.15))
        sys.stdout.write(f"\r{Fore.MAGENTA}{log}" + " " * 15)
        sys.stdout.flush()
    print(f"\r{Fore.GREEN}[*] BEACON CHECK-IN CONFIRMED. PARSING TASK." + " " * 10)
    time.sleep(0.5)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # SHADED 'POLY MORPH' BANNER
    banner = r"""
    {0}██████╗  ██████╗ ██╗  ██╗   ██╗    ███╗   ███╗ ██████╗ ██████╗ ██████╗ ██╗  ██╗
    {0}██╔══██╗██╔═══██╗██║  ╚██╗ ██╔╝    ████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██║  ██║
    {0}██████╔╝██║   ██║██║   ╚████╔╝     ██╔████╔██║██║   ██║██████╔╝██████╔╝███████║
    {0}██╔═══╝ ██║   ██║██║    ╚██╔╝      ██║╚██╔╝██║██║   ██║██╔══██╗██╔═══╝ ██╔══██║
    {0}██║     ╚██████╔╝███████╗██║       ██║ ╚═╝ ██║╚██████╔╝██║  ██║██║     ██║  ██║
    {0}╚═╝      ╚═════╝ ╚══════╝╚═╝       ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝
    """.format(Fore.RED + Style.BRIGHT)
    
    print(banner)
    print("\n")

def display_beacon_dramatic(json_data):
    """
    Dramatic reveal for Beacon Intel.
    """
    try:
        event = json_data.get("event", "UNKNOWN")
        atk_type = json_data.get("type", "UNKNOWN")
        intel = json_data.get("intel", {})
        tool = intel.get("tool", "N/A")
        dest = intel.get("dest_ip", "N/A")
        interval = intel.get("interval", "N/A")

        # --- BOX CONFIGURATION ---
        BOX_WIDTH = 70
        INNER_WIDTH = BOX_WIDTH - 4 
        
        def print_border_line(label, value, color=Fore.CYAN):
            text = f"{label}: {value}"
            if len(text) > INNER_WIDTH: text = text[:INNER_WIDTH-3] + "..."
            padding = " " * (INNER_WIDTH - len(text))
            print(f"{Fore.MAGENTA}██ {Fore.WHITE}{label}: {color}{value}{padding} {Fore.MAGENTA}██")

        # --- DRAW BOX ---
        print("\n" + Fore.MAGENTA + "▄" * BOX_WIDTH) 
        
        # HEADERS
        header_text = f"C2 HEARTBEAT: {event}"
        pad_head = " " * (INNER_WIDTH - len(header_text))
        print(f"{Fore.MAGENTA}██ {Fore.YELLOW + Style.BRIGHT}{header_text}{pad_head} {Fore.MAGENTA}██")
        
        print(f"{Fore.MAGENTA}██" + " " * INNER_WIDTH + "██") # Spacer
        
        # STATS
        print_border_line("MODE", atk_type, Fore.MAGENTA + Style.BRIGHT)
        print_border_line("IMPLANT", tool)
        print_border_line("DESTINATION", dest)
        print_border_line("SLEEP/JITTER", interval, Fore.GREEN + Style.BRIGHT)

        print(Fore.MAGENTA + "▀" * BOX_WIDTH) 
        print(Style.RESET_ALL)

    except Exception as e:
        print(f"{Fore.RED}[!] DISPLAY ERROR: {e}")

# --- GENERATION ---
def generate_beacon(mode_key):
    mode_desc = MODES.get(mode_key, "Generic Beacon")
    
    prompt = f"""
    Generate a JSON object for a Red Team C2 Beaconing Simulation.
    Mode: {mode_desc}
    
    Strictly follow this JSON schema:
    {{
        "event":"Polymorphic Beacon",
        "type": "Polymorphic Beacon",
        "intel": {{
            "tool": "Name of a C2 framework (e.g. Cobalt Strike, Sliver, Mythic, Havoc, Brute Ratel)",
            "dest_ip": "A realistic destination (IP address, domain, or named pipe path depending on mode)",
            "interval": "A sleep time with jitter (e.g. '60s (35% jitter)', '500ms (0% jitter)')"
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
    print(f"\n{Fore.YELLOW}[*] SYNCING WITH CONTROLLER AT {target}...", end="")
    try:
        # Simulate network latency
        time.sleep(0.4)
        
        if proto == "http":
            url = f"http://{target}:{port}/ingest"
            requests.post(url, json=data, timeout=3)
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((target, port))
                s.sendall(json.dumps(data).encode('utf-8'))
        
        print(f"\r{Fore.GREEN}{Style.BRIGHT}[✔] CHECK-IN SUCCESSFUL. TASKS QUEUED.\a") 
    except Exception as e:
        print(f"\r{Fore.RED}{Back.WHITE}[✖] C2 SERVER UNREACHABLE: {e}")

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Blue Team IP")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--proto", choices=["http", "tcp"], default="tcp")
    parser.add_argument("--mode", choices=MODES.keys(), default="jitter", help="Beacon Mode")
    parser.add_argument("--loop", action="store_true", help="Continuous Heartbeat")
    args = parser.parse_args()

    print_header()
    print(f"{Fore.CYAN}[*] C2 SERVER:   {Fore.WHITE}{args.target}:{args.port}")
    print(f"{Fore.CYAN}[*] BEACON MODE: {Fore.WHITE}{args.mode.upper()}")
    print("-" * 60)
    
    while True:
        cyber_sequence()
        data = generate_beacon(args.mode)
        
        if data:
            display_beacon_dramatic(data)
            transmit(args.target, args.port, args.proto, data)
        else:
            print(f"{Fore.RED}[!] CRYPTO HANDSHAKE FAILURE - RE-KEYING...")

        if not args.loop:
            break
            
        # Simulate the "Sleep" time (shortened for demo purposes)
        sleep_demo = random.uniform(2.0, 5.0)
        print(f"\n{Fore.BLUE}[zz] Sleeping for {sleep_demo:.1f}s...")
        time.sleep(sleep_demo)

if __name__ == "__main__":
    main()
