import os
import json
import time
import socket
import argparse
import random
import sys
import re
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
    "volumetric": "High-Bandwidth UDP/QUIC Flood (Bandwidth Saturation)",
    "handshake": "QUIC Handshake Exhaustion (CPU Saturation)",
    "reflection": "Amplification Attack via Spoofed UDP Headers",
    "stream": "Stream Multiplexing Abuse (Resource Exhaustion)",
    "malformed": "Fuzzing / Malformed Packet Injection"
}

# --- VISUALS ---

def cyber_sequence():
    """Prints fake QUIC-specific hacking logs."""
    logs = [
        "[*] Initializing UDP Raw Sockets...",
        "[*] Fragmenting QUIC Packets (MTU 1350)...",
        "[*] Spoofing Source IPs (Random CIDR)...",
        "[*] Multiplexing Streams (Bidirectional)...",
        "[*] Injecting 0-RTT Handshake Data...",
        "[*] Saturation Check: 0%",
        "[*] Saturation Check: 45%",
        "[*] Saturation Check: 98%"
    ]
    print("\n")
    for log in logs:
        time.sleep(random.uniform(0.05, 0.15))
        sys.stdout.write(f"\r{Fore.CYAN}{log}" + " " * 15)
        sys.stdout.flush()
    print(f"\r{Fore.GREEN}[*] TARGET SATURATED. SENDING TELEMETRY." + " " * 15)
    time.sleep(0.5)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # SHADED 'QUIC STORM' BANNER
    banner = r"""
    {0} ██████╗ ██╗   ██╗██╗ ██████╗    ███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗
    {0}██╔═══██╗██║   ██║██║██╔════╝    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗ ████║
    {0}██║   ██║██║   ██║██║██║         ███████╗   ██║   ██║   ██║██████╔╝██╔████╔██║
    {0}██║▄▄ ██║██║   ██║██║██║         ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╔╝██║
    {0}╚██████╔╝╚██████╔╝██║╚██████╗    ███████║   ██║   ╚██████╔╝██║  ██║██║ ╚═╝ ██║
    {0} ╚══▀▀═╝  ╚═════╝ ╚═╝ ╚═════╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝
    """.format(Fore.RED + Style.BRIGHT)
    
    print(banner)
    print(f"{Fore.WHITE + Back.RED}         >> UDP/QUIC DENIAL OF SERVICE SIMULATOR <<         ")
    print("\n")

def display_attack_dramatic(json_data):
    """
    Dramatic reveal for DoS Stats.
    """
    try:
        event = json_data.get("event", "UNKNOWN")
        atk_type = json_data.get("type", "UNKNOWN")
        intel = json_data.get("intel", {})
        tool = intel.get("tool", "N/A")
        proto = intel.get("protocol", "N/A")
        rate = intel.get("rate", "N/A")

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
        print_border_line("TOOL", tool)
        print_border_line("PROTOCOL", proto)
        print_border_line("RATE", rate, Fore.GREEN + Style.BRIGHT)

        print(Fore.RED + "▀" * BOX_WIDTH) 
        print(Style.RESET_ALL)

    except Exception as e:
        print(f"{Fore.RED}[!] DISPLAY ERROR: {e}")

# --- GENERATION ---
def generate_attack(mode_key):
    mode_desc = MODES.get(mode_key, "General Flood")
    
    prompt = f"""
    Generate a JSON object for a Red Team QUIC/UDP Flood Simulation.
    Mode: {mode_desc}
    
    Strictly follow this JSON schema:
    {{
        "event": "QUIC Flood (DoS)",
        "type": "QUIC Flood (DoS)",
        "intel": {{
            "tool": "Name of a fake DoS tool (e.g. QUIC-Hammer, UDP-Reaper, Tsunami)",
            "protocol": "Technical details (e.g. UDP/443 QUIC v1, UDP/8080)",
            "rate": "A realistic attack rate (e.g. 1.2M PPS, 45 Gbps, 8000 Req/sec)"
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
    print(f"\n{Fore.YELLOW}[*] FIRING PACKET STREAM TO {target}...", end="")
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
        
        print(f"\r{Fore.GREEN}{Style.BRIGHT}[✔] PACKETS DELIVERED. TARGET IMPACTED.\a") 
    except Exception as e:
        print(f"\r{Fore.RED}{Back.WHITE}[✖] TARGET UNREACHABLE: {e}")

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Blue Team IP")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--proto", choices=["http", "tcp"], default="http")
    parser.add_argument("--mode", choices=MODES.keys(), default="volumetric", help="Attack Mode")
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
            display_attack_dramatic(data)
            transmit(args.target, args.port, args.proto, data)
        else:
            print(f"{Fore.RED}[!] GENERATION FAILURE - RECALIBRATING...")

        if not args.loop:
            break
            
        print(f"\n{Fore.BLUE}[zz] Cooling Down Canons...")
        time.sleep(2)

if __name__ == "__main__":
    main()
