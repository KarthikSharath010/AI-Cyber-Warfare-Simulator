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

# --- SPOOF MODES ---
MODES = {
    "bot": "Search Engine Crawler (Googlebot/Bingbot)",
    "mobile": "Mobile Device Masquerade (iPhone/Android)",
    "legacy": "Legacy Browser Emulation (IE6/Netscape)",
    "console": "Game Console / IoT Device (PS5/SmartTV)",
    "custom": "Malicious Tool Signature (Sqlmap/Nikto)"
}

# --- VISUALS ---

def cyber_sequence():
    """Prints fake header manipulation logs."""
    logs = [
        "[*] Intercepting HTTP Request Stream...",
        "[*] Stripping Default Headers...",
        "[*] Injecting Custom User-Agent Token...",
        "[*] Recalculating Request Checksum...",
        "[*] Bypassing Device Fingerprinting...",
        "[*] Rotating Client Hints...",
        "[*] Spoofing OS Signature..."
    ]
    print("\n")
    for log in logs:
        time.sleep(random.uniform(0.05, 0.15))
        sys.stdout.write(f"\r{Fore.CYAN}{log}" + " " * 10)
        sys.stdout.flush()
    print(f"\r{Fore.GREEN}[*] IDENTITY MASKED. SENDING REQUEST." + " " * 10)
    time.sleep(0.5)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # SHADED 'AGENT MASK' BANNER
    banner = r"""
    {0} █████╗  ██████╗ ███████╗███╗   ██╗████████╗    ███╗   ███╗ █████╗ ███████╗██╗  ██╗
    {0}██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝    ████╗ ████║██╔══██╗██╔════╝██║ ██╔╝
    {0}███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║       ██╔████╔██║███████║███████╗█████╔╝ 
    {0}██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║       ██║╚██╔╝██║██╔══██║╚════██║██╔═██╗ 
    {0}██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║       ██║ ╚═╝ ██║██║  ██║███████║██║  ██╗
    {0}╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """.format(Fore.RED + Style.BRIGHT)
    
    print(banner)
    print(f"{Fore.WHITE + Back.RED}      >> HTTP HEADER SPOOFING & EVASION MODULE <<      ")
    print("\n")

def display_spoof_dramatic(json_data):
    """
    Dramatic reveal for UA strings.
    """
    try:
        event = json_data.get("event", "UNKNOWN")
        atk_type = json_data.get("type", "UNKNOWN")
        intel = json_data.get("intel", {})
        agent = intel.get("agent", "N/A")

        # --- BOX CONFIGURATION ---
        BOX_WIDTH = 80
        INNER_WIDTH = BOX_WIDTH - 4 
        
        def print_border_line(label, value, color=Fore.CYAN):
            text = f"{label}: {value}"
            # Check length to prevent overflow
            if len(text) > INNER_WIDTH: 
                 # If value is long (like a UA string), wrap it specially
                 pass 
            else:
                padding = " " * (INNER_WIDTH - len(text))
                print(f"{Fore.RED}██ {Fore.WHITE}{label}: {color}{value}{padding} {Fore.RED}██")

        # --- DRAW BOX ---
        print("\n" + Fore.RED + "▄" * BOX_WIDTH) 
        
        # HEADERS
        header_text = f"SPOOF TELEMETRY: {event}"
        pad_head = " " * (INNER_WIDTH - len(header_text))
        print(f"{Fore.RED}██ {Fore.YELLOW + Style.BRIGHT}{header_text}{pad_head} {Fore.RED}██")
        
        print(f"{Fore.RED}██" + " " * INNER_WIDTH + "██") # Spacer
        
        # STATS
        print_border_line("MODE", atk_type, Fore.RED + Style.BRIGHT)
        
        # Handle Long User-Agent String Wrapping
        label = "UA STRING"
        print(f"{Fore.RED}██ {Fore.WHITE}{label}:{ ' ' * (INNER_WIDTH - len(label) - 1)} {Fore.RED}██")
        
        wrapped_agent = textwrap.wrap(agent, width=INNER_WIDTH)
        for line in wrapped_agent:
            padding = " " * (INNER_WIDTH - len(line))
            print(f"{Fore.RED}██ {Fore.GREEN}{line}{padding} {Fore.RED}██")

        print(Fore.RED + "▀" * BOX_WIDTH) 
        print(Style.RESET_ALL)

    except Exception as e:
        print(f"{Fore.RED}[!] DISPLAY ERROR: {e}")

# --- GENERATION ---
def generate_spoof(mode_key):
    mode_desc = MODES.get(mode_key, "Standard Browser")
    
    prompt = f"""
    Generate a JSON object for a Red Team User-Agent Spoofing Simulation.
    Mode: {mode_desc}
    
    Strictly follow this JSON schema:
    {{
        "event": "User-Agent Spoofing",
        "type": "User-Agent Spoofing",
        "intel": {{
            "agent": "A realistic User-Agent string corresponding to the mode (e.g. 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' for bot mode)"
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
    print(f"\n{Fore.YELLOW}[*] SENDING REQUEST WITH SPOOFED HEADER TO {target}...", end="")
    try:
        time.sleep(0.3)
        
        if proto == "http":
            url = f"http://{target}:{port}/ingest"
            # Actually spoof the header in the real request too for realism
            headers = {'User-Agent': data['intel']['agent']}
            requests.post(url, json=data, headers=headers, timeout=3)
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((target, port))
                s.sendall(json.dumps(data).encode('utf-8'))
        
        print(f"\r{Fore.GREEN}{Style.BRIGHT}[✔] SERVER ACCEPTED FINGERPRINT.\a") 
    except Exception as e:
        print(f"\r{Fore.RED}{Back.WHITE}[✖] CONNECTION FAILED: {e}")

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Blue Team IP")
    parser.add_argument("--port", type=int, default=6000)
    parser.add_argument("--proto", choices=["http", "tcp"], default="tcp")
    parser.add_argument("--mode", choices=MODES.keys(), default="bot", help="Spoof Mode")
    parser.add_argument("--loop", action="store_true", help="Continuous Rotation")
    args = parser.parse_args()

    print_header()
    print(f"{Fore.CYAN}[*] TARGET ACQUIRED: {Fore.WHITE}{args.target}:{args.port}")
    print(f"{Fore.CYAN}[*] IDENTITY MASK:   {Fore.WHITE}{args.mode.upper()}")
    print("-" * 60)
    
    while True:
        cyber_sequence()
        data = generate_spoof(args.mode)
        
        if data:
            display_spoof_dramatic(data)
            transmit(args.target, args.port, args.proto, data)
        else:
            print(f"{Fore.RED}[!] SPOOFING ENGINE FAILURE - RE-INITIALIZING...")

        if not args.loop:
            break
            
        print(f"\n{Fore.BLUE}[zz] Rotating Identity & Cooling Down...")
        time.sleep(2)

if __name__ == "__main__":
    main()
