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
# Using standard flash model for speed
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
    "standard": "Standard High-Velocity SYN Flood (hping3)",
    "spoof": "IP Spoofing Flood (Randomized Source IPs)",
    "distributed": "DDoS Simulation (Botnet Simulation)",
    "low_slow": "Low-and-Slow Resource Exhaustion",
    "ack": "TCP ACK Flood (Bypass Stateful Firewalls)"
}

# --- VISUALS ---

def cyber_sequence():
    """Prints fake DoS hacking logs."""
    logs = [
        "[*] Allocating Raw Sockets...",
        "[*] Setting TCP Flags (SYN=1, ACK=0)...",
        "[*] Randomizing Sequence Numbers...",
        "[*] Spoofing Source IP Headers...",
        "[*] Calculating Bandwidth Saturation...",
        "[*] Igniting Packet Stream...",
        "[*] Flooding Target Interface (eth0)..."
    ]
    print("\n")
    for log in logs:
        time.sleep(random.uniform(0.05, 0.15))
        sys.stdout.write(f"\r{Fore.CYAN}{log}" + " " * 10)
        sys.stdout.flush()
    print(f"\r{Fore.GREEN}[*] FLOOD INITIATED. SENDING TELEMETRY." + " " * 10)
    time.sleep(0.5)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # SHADED 'SYN STORM' BANNER
    banner = r"""
    {0}███████╗██╗   ██╗███╗   ██╗    ███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗
    {0}██╔════╝╚██╗ ██╔╝████╗  ██║    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗ ████║
    {0}███████╗ ╚████╔╝ ██╔██╗ ██║    ███████╗   ██║   ██║   ██║██████╔╝██╔████╔██║
    {0}╚════██║  ╚██╔╝  ██║╚██╗██║    ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╔╝██║
    {0}███████║   ██║   ██║ ╚████║    ███████║   ██║   ╚██████╔╝██║  ██║██║ ╚═╝ ██║
    {0}╚══════╝   ╚═╝   ╚═╝  ╚═══╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝
    """.format(Fore.RED + Style.BRIGHT)
    
    print(banner)
    print(f"{Fore.WHITE + Back.RED}       >> TCP DENIAL OF SERVICE (DoS) SIMULATOR <<       ")
    print("\n")

def display_flood_dramatic(json_data):
    """
    Dramatic reveal for DoS Stats.
    """
    try:
        event = json_data.get("event", "UNKNOWN")
        atk_type = json_data.get("type", "UNKNOWN")
        intel = json_data.get("intel", {})
        tool = intel.get("tool", "N/A")
        protocol = intel.get("protocol", "N/A")
        flags = intel.get("flags", "N/A")
        count = intel.get("count", "N/A")

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
        header_text = f"FLOOD TELEMETRY: {event}"
        pad_head = " " * (INNER_WIDTH - len(header_text))
        print(f"{Fore.RED}██ {Fore.YELLOW + Style.BRIGHT}{header_text}{pad_head} {Fore.RED}██")
        
        print(f"{Fore.RED}██" + " " * INNER_WIDTH + "██") # Spacer
        
        # STATS
        print_border_line("VECTOR", atk_type, Fore.RED + Style.BRIGHT)
        print_border_line("TOOL", tool)
        print_border_line("PROTOCOL", protocol)
        print_border_line("TCP FLAGS", flags, Fore.YELLOW + Style.BRIGHT)
        print_border_line("VOLUME", count, Fore.GREEN + Style.BRIGHT)

        print(Fore.RED + "▀" * BOX_WIDTH) 
        print(Style.RESET_ALL)

    except Exception as e:
        print(f"{Fore.RED}[!] DISPLAY ERROR: {e}")

# --- GENERATION ---
def generate_attack(mode_key):
    mode_desc = MODES.get(mode_key, "Standard Flood")
    
    prompt = f"""
    Generate a JSON object for a Red Team TCP SYN Flood Simulation.
    Mode: {mode_desc}
    
    Strictly follow this JSON schema:
    {{
        "event": "SYN Flood",
        "type": "SYN Flood",
        "intel": {{
            "tool": "Name of a DoS tool (e.g. hping3, LOIC, Tsunami, Bonesi)",
            "protocol": "Transport Protocol (e.g. TCP/IPv4)",
            "flags": "TCP Flags Set (e.g. SYN, SYN-ACK, ACK)",
            "count": "Realistic packet count or rate (e.g. 500,000 PPS, 1.2 Gbps, 15M Packets)"
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
    print(f"\n{Fore.YELLOW}[*] BLASTING PACKETS TO {target}...", end="")
    try:
        # Simulate firing duration
        time.sleep(0.3)
        
        if proto == "http":
            url = f"http://{target}:{port}/ingest"
            requests.post(url, json=data, timeout=3)
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((target, port))
                s.sendall(json.dumps(data).encode('utf-8'))
        
        print(f"\r{Fore.GREEN}{Style.BRIGHT}[✔] PACKETS DELIVERED. TARGET LAGGING.\a") 
    except Exception as e:
        print(f"\r{Fore.RED}{Back.WHITE}[✖] TARGET DOWN / UNREACHABLE: {e}")

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Blue Team IP")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--proto", choices=["http", "tcp"], default="tcp")
    parser.add_argument("--mode", choices=MODES.keys(), default="standard", help="Attack Mode")
    parser.add_argument("--loop", action="store_true", help="Continuous Fire")
    args = parser.parse_args()

    print_header()
    print(f"{Fore.CYAN}[*] TARGET LOCKED: {Fore.WHITE}{args.target}:{args.port}")
    print(f"{Fore.CYAN}[*] ATTACK VECTOR: {Fore.WHITE}{args.mode.upper()}")
    print("-" * 60)
    
    while True:
        cyber_sequence()
        data = generate_attack(args.mode)
        
        if data:
            display_flood_dramatic(data)
            transmit(args.target, args.port, args.proto, data)
        else:
            print(f"{Fore.RED}[!] GENERATION FAILURE - RECALIBRATING...")

        if not args.loop:
            break
            
        print(f"\n{Fore.BLUE}[zz] Cooling Down Canons...")
        time.sleep(2)

if __name__ == "__main__":
    main()
