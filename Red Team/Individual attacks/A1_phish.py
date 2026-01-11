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

# --- THEMES ---
THEMES = {
    "finance": "Urgent Wire Transfer / Overdue Invoice",
    "hr": "Mandatory Policy Update / Bonus Scheme",
    "it": "Password Expiry / Suspicious Login",
    "ceo": "CEO Gift Card Request (Whaling)",
    "shipping": "Missed Package / Customs Fee",
    "service": "Netflix/Amazon Account Locked"
}

# --- VISUALS ---

def cyber_sequence():
    logs = [
        "[*] Bypassing Firewall Rules...",
        "[*] Rotating Proxy Chains (Node 142 -> Node 89)...",
        "[*] Injecting Custom Headers...",
        "[*] Spoofing Sender Identity...",
        "[*] Encrypting Payload Stream...",
        "[*] Establishing Handshake with Gemini Core...",
        "[*] Awaiting Neural Response..."
    ]
    print("\n")
    for log in logs:
        time.sleep(random.uniform(0.05, 0.15))
        sys.stdout.write(f"\r{Fore.CYAN}{log}" + " " * 10)
        sys.stdout.flush()
    print(f"\r{Fore.GREEN}[*] ACCESS GRANTED. SYNTHESIZING ATTACK." + " " * 10)
    time.sleep(0.5)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = r"""
    {0}██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗██████╗ 
    {0}██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝██╔══██╗
    {0}██████╔╝███████║██║███████╗███████║█████╗  ██████╔╝
    {0}██╔═══╝ ██╔══██║██║╚════██║██╔══██║██╔══╝  ██╔══██╗
    {0}██║     ██║  ██║██║███████║██║  ██║███████╗██║  ██║
    {0}╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """.format(Fore.RED + Style.BRIGHT)
    print(banner)
    print("\n")

def display_email_dramatic(json_data):
    try:
        payload = json_data.get("payload", "")
        persona = json_data.get("intel", {}).get("persona", "Unknown")
        tool = json_data.get("intel", {}).get("tool", "Unknown")
        atk_type = json_data.get("type", "UNKNOWN")

        BOX_WIDTH = 80
        INNER_WIDTH = BOX_WIDTH - 4 
        
        def print_border_line(text, color=Fore.YELLOW):
            if len(text) > INNER_WIDTH:
                text = text[:INNER_WIDTH-3] + "..."
            padding = " " * (INNER_WIDTH - len(text))
            print(f"{Fore.RED}║ {color}{text}{padding} {Fore.RED}║")

        print("\n" + Fore.RED + "╔" + "═" * (BOX_WIDTH - 2) + "╗")
        
        print_border_line("PHISHER INTERCEPTED DATA", Fore.WHITE + Style.BRIGHT)
        print(f"{Fore.RED}╠" + "═" * (BOX_WIDTH - 2) + "╣")
        print_border_line(f"VECTOR:   {atk_type}", Fore.CYAN)
        print_border_line(f"ACTOR:    {persona}", Fore.CYAN)
        print_border_line(f"TOOLKIT:  {tool}", Fore.CYAN)
        print(f"{Fore.RED}╠" + "═" * (BOX_WIDTH - 2) + "╣")

        paragraphs = payload.split('\n')
        
        for p in paragraphs:
            if not p.strip():
                print_border_line("", Fore.GREEN)
                continue
            
            wrapped_lines = textwrap.wrap(p, width=INNER_WIDTH)
            
            for line in wrapped_lines:
                sys.stdout.write(f"{Fore.RED}║ {Fore.GREEN}")
                for char in line:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(0.003) 
                
                padding_len = INNER_WIDTH - len(line)
                print(" " * padding_len + f" {Fore.RED}║")

        print(Fore.RED + "╚" + "═" * (BOX_WIDTH - 2) + "╝")
        print(Style.RESET_ALL)

    except Exception as e:
        print(f"{Fore.RED}[!] DISPLAY ERROR: {e}")

# --- GENERATION ---
def generate_attack(theme_key):
    theme_desc = THEMES.get(theme_key, "General Spam")
    
    prompt = f"""
    Generate a JSON object for a Red Team Phishing Simulation.
    Theme: {theme_desc}
    
    Strictly follow this JSON schema:
    {{
        "event": "AI PHISHING CAMPAIGN",
        "type": "AI PHISHING CAMPAIGN",
        "payload": "Construct a FULL email here (From, To, Subject, Body). The Body MUST start with '[SIMULATION - DEMO ONLY]'. Make it look realistic.",
        "intel": {{
            "tool": "Name of a fake phishing tool (e.g. GoPhish, EvilGinx)",
            "persona": "Name of a fake threat actor group (e.g. APT29, Lazarus)",
            "tokens": "Generate a random integer confidence score (0-100)"
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
    except:
        return None

# --- NETWORK ---
def transmit(target, port, proto, data):
    try:
        time.sleep(0.5)
        
        if proto == "http":
            url = f"http://{target}:{port}/ingest"
            requests.post(url, json=data, timeout=3)
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((target, port))
                s.sendall(json.dumps(data).encode('utf-8'))
        
        print(f"\r{Fore.GREEN}{Style.BRIGHT}[✔] MAIL DELIVERED.\a") 
    except Exception as e:
        print(f"\r{Fore.RED}{Back.WHITE}[✖] TRANSMISSION FAILURE: {e}")

# --- INTERACTIVE MAIN ---
def main():
    print_header()
    print(f"{Fore.CYAN}[ INTERACTIVE MODE ENABLED ]{Fore.WHITE}")
    print("-" * 60)

    target = input(f"{Fore.YELLOW}Enter Blue Team Target IP: {Fore.WHITE}").strip()
    if not target:
        print(Fore.RED + "Target IP cannot be empty.")
        sys.exit(1)

    try:
        port = int(input(f"{Fore.YELLOW}Enter Port (default 5000): {Fore.WHITE}").strip() or "6000")
    except ValueError:
        print(Fore.RED + "Invalid port.")
        sys.exit(1)

    print(f"{Fore.CYAN}\nChoose Protocol:{Fore.WHITE}")
    print("  1) HTTP")
    print("  2) TCP")
    proto_choice = input(f"{Fore.YELLOW}Select (1/2): {Fore.WHITE}").strip()
    proto = "tcp" if proto_choice == "1" else "tcp"

    print(f"\n{Fore.CYAN}Choose Theme:{Fore.WHITE}")
    for i, key in enumerate(THEMES.keys(), start=1):
        print(f"  {i}) {key.title()}")

    theme_choice = input(f"{Fore.YELLOW}Select (1-{len(THEMES)}): {Fore.WHITE}").strip()
    try:
        theme = list(THEMES.keys())[int(theme_choice) - 1]
    except:
        print(Fore.RED + "Invalid theme.")
        sys.exit(1)

    loop_mode = input(f"{Fore.YELLOW}Enable loop mode? (y/n): {Fore.WHITE}").strip().lower() == "y"

    print("\n" + "-" * 60)
    print(f"{Fore.CYAN}[*] TARGET ACQUIRED: {Fore.WHITE}{target}:{port}")
    print(f"{Fore.CYAN}[*] PROTOCOL:       {Fore.WHITE}{proto.upper()}")
    print(f"{Fore.CYAN}[*] THEME:          {Fore.WHITE}{theme.upper()}")
    print(f"{Fore.CYAN}[*] LOOP MODE:      {Fore.WHITE}{'ENABLED' if loop_mode else 'DISABLED'}")
    print("-" * 60)

    while True:
        cyber_sequence()
        
        data = generate_attack(theme)
        if data:
            display_email_dramatic(data)
            transmit(target, port, proto, data)
        else:
            print(Fore.RED + "[!] Payload Generation Failed.")

        if not loop_mode:
            break

        print(f"\n{Fore.BLUE}[zz] Cooling down neural links...")
        time.sleep(3)

if __name__ == "__main__":
    main()
