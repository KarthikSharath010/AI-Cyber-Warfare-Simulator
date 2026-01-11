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

# --- SCAN MODES ---
MODES = {
    "syn": "TCP SYN Stealth Scan (-sS)",
    "connect": "TCP Connect Full Handshake Scan (-sT)",
    "udp": "UDP Protocol Scan (-sU)",
    "xmas": "Christmas Tree Scan (FIN, PSH, URG flags)",
    "version": "Service Version Detection (-sV)"
}

# --- VISUALS ---

def cyber_sequence():
    """Prints fake network scanning logs."""
    logs = [
        "[*] Initializing Raw Sockets...",
        "[*] Loading MAC OUI Database...",
        "[*] Randomizing Source Ports...",
        "[*] Calculating RTT Timeouts...",
        "[*] Sending ARP Requests...",
        "[*] Fragmenting Packets (MTU 1500)...",
        "[*] Analyzing TTL Responses..."
    ]
    print("\n")
    for log in logs:
        time.sleep(random.uniform(0.05, 0.15))
        sys.stdout.write(f"\r{Fore.CYAN}{log}" + " " * 10)
        sys.stdout.flush()
    print(f"\r{Fore.GREEN}[*] HOST DISCOVERY COMPLETE. SCANNING PORTS." + " " * 5)
    time.sleep(0.5)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # SHADED 'PORT SWEEP' BANNER
    banner = r"""
    {0}██████╗  ██████╗ ██████╗ ████████╗    ███████╗██╗    ██╗███████╗███████╗██████╗ 
    {0}██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔════╝██║    ██║██╔════╝██╔════╝██╔══██╗
    {0}██████╔╝██║   ██║██████╔╝   ██║       ███████╗██║ █╗ ██║█████╗  █████╗  ██████╔╝
    {0}██╔═══╝ ██║   ██║██╔══██╗   ██║       ╚════██║██║███╗██║██╔══╝  ██╔══╝  ██╔═══╝ 
    {0}██║     ╚██████╔╝██║  ██║   ██║       ███████║╚███╔███╔╝███████╗███████╗██║     
    {0}╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚══════╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝     
    """.format(Fore.RED + Style.BRIGHT)
    
    print(banner)
    print(f"{Fore.WHITE + Back.RED}       >> NETWORK RECONNAISSANCE & DISCOVERY MODULE <<       ")
    print("\n")

def display_scan_dramatic(json_data):
    """
    Dramatic reveal for Scan Results.
    """
    try:
        event = json_data.get("event", "UNKNOWN")
        atk_type = json_data.get("type", "UNKNOWN")
        intel = json_data.get("intel", {})
        tool = intel.get("tool", "N/A")
        ports = intel.get("ports", "N/A")

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
        header_text = f"SCAN REPORT: {event}"
        pad_head = " " * (INNER_WIDTH - len(header_text))
        print(f"{Fore.RED}██ {Fore.YELLOW + Style.BRIGHT}{header_text}{pad_head} {Fore.RED}██")
        
        print(f"{Fore.RED}██" + " " * INNER_WIDTH + "██") # Spacer
        
        # STATS
        print_border_line("METHOD", atk_type, Fore.RED + Style.BRIGHT)
        print_border_line("TOOL", tool)
        
        # Handle Port List Wrapping
        port_label = "PORTS"
        wrapped_ports = textwrap.wrap(str(ports), width=INNER_WIDTH - len(port_label) - 2)
        
        for i, line in enumerate(wrapped_ports):
            if i == 0:
                print_border_line(port_label, line, Fore.GREEN + Style.BRIGHT)
            else:
                padding = " " * (INNER_WIDTH - len(line))
                print(f"{Fore.RED}██ {Fore.GREEN + Style.BRIGHT}{line}{padding} {Fore.RED}██")

        print(Fore.RED + "▀" * BOX_WIDTH) 
        print(Style.RESET_ALL)

    except Exception as e:
        print(f"{Fore.RED}[!] DISPLAY ERROR: {e}")

# --- GENERATION ---
def generate_scan(mode_key):
    mode_desc = MODES.get(mode_key, "General Scan")
    
    prompt = f"""
    Generate a JSON object for a Red Team Network Scan Simulation.
    Mode: {mode_desc}
    
    Strictly follow this JSON schema:
    {{
        "event": "Port Scanning",
        "type": "Port Scanning",
        "intel": {{
            "tool": "Name of a network scanner (e.g. Nmap 7.92, Masscan, RustScan, Zmap)",
            "ports": "A realistic list of discovered open ports and services (e.g. '22/tcp (OpenSSH), 80/tcp (Apache), 3306/tcp (MySQL)') or ranges detected."
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
    print(f"\n{Fore.YELLOW}[*] UPLOADING SCAN DATA TO C2 AT {target}...", end="")
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
        
        print(f"\r{Fore.GREEN}{Style.BRIGHT}[✔] RECON DATA EXFILTRATED.\a") 
    except Exception as e:
        print(f"\r{Fore.RED}{Back.WHITE}[✖] C2 CONNECTION FAILED: {e}")

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Blue Team IP")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--proto", choices=["http", "tcp"], default="tcp")
    parser.add_argument("--mode", choices=MODES.keys(), default="syn", help="Scan Type")
    parser.add_argument("--loop", action="store_true", help="Continuous Scanning")
    args = parser.parse_args()

    print_header()
    print(f"{Fore.CYAN}[*] TARGET RANGE: {Fore.WHITE}{args.target}:{args.port}")
    print(f"{Fore.CYAN}[*] SCAN PROFILE: {Fore.WHITE}{args.mode.upper()}")
    print("-" * 60)
    
    while True:
        cyber_sequence()
        data = generate_scan(args.mode)
        
        if data:
            display_scan_dramatic(data)
            transmit(args.target, args.port, args.proto, data)
        else:
            print(f"{Fore.RED}[!] SCANNER ERROR - RE-INITIALIZING...")

        if not args.loop:
            break
            
        print(f"\n{Fore.BLUE}[zz] Changing Source IP & Cooling Down...")
        time.sleep(3)

if __name__ == "__main__":
    main()
