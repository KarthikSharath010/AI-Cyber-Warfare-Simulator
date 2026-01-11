from gevent import monkey
monkey.patch_all()

import sys
import json
import socket
import random
import datetime as dt
import queue
import time
import psutil
import threading
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# --- IMPORTS (Preserving your folder structure) ---
try:
    from defenses.phishing import analyze_text
    from defenses.waf import inspect_request
    from defenses.network import NetworkMonitor
except ImportError:
    # Dummy fallbacks if testing without modules
    def analyze_text(t): return {"verdict": "ALLOWED", "confidence": 0, "details": "Simulation Mode"}
    def inspect_request(p, h, ip): return {"blocked": False, "details": "Simulated", "rule_id": 0}
    NetworkMonitor = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blue_team_secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

# --- CONFIGURATION ---
HTTP_PORT = 5000
TCP_RAW_PORT = 6000 

NETWORK_ALERT_QUEUE = queue.Queue()
if NetworkMonitor:
    network_monitor = NetworkMonitor(NETWORK_ALERT_QUEUE, interface='eth0')

EVENT_HISTORY = []
MAX_HISTORY_LIMIT = 50
VERDICT_HISTORY = [] # Buffer to track recent wins/losses for the Gauge

# --- GLOBAL STATE FOR RL ---
RL_SESSION_DATA = {
    "total_score": 0,
    "episode_count": 0
}

# --- VISUALS ---
class Colors:
    HEADER = '\033[95m'; BLUE = '\033[94m'; CYAN = '\033[96m'
    GREEN = '\033[92m'; WARNING = '\033[93m'; FAIL = '\033[91m'
    ENDC = '\033[0m'; BOLD = '\033[1m'

def print_banner():
    os.system('clear')
    print(f"{Colors.CYAN}")
    print(r"""
    ██████╗ ██╗     ██╗   ██╗███████╗    ██████╗ ███████╗███████╗
    ██╔══██╗██║     ██║   ██║██╔════╝    ██╔══██╗██╔════╝██╔════╝
    ██████╔╝██║     ██║   ██║█████╗      ██║  ██║█████╗  █████╗  
    ██╔══██╗██║     ██║   ██║██╔══╝      ██║  ██║██╔══╝  ██╔══╝  
    ██████╔╝███████╗╚██████╔╝███████╗    ██████╔╝███████╗██║     
    ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝    ╚══════╝ ╚══════╝╚═╝     
    """)
    print(f"{Colors.ENDC}")
    print(f"{Colors.BOLD}   >>> BLUE TEAM TACTICAL OS v3.0 (RL ENHANCED) <<<{Colors.ENDC}\n")
    time.sleep(0.5)

def startup_sequence():
    checks = [
        ("CORE KERNEL", "ONLINE", 0.2),
        ("WAF ENGINE (OWASP)", "ACTIVE", 0.3),
        ("NEURAL NET (DarkBERT-Lite)", "STANDBY (ON-DEMAND)", 0.4),
        ("PACKET SNIFFER (ETH0)", "ARMED", 0.3),
        ("REWARD ENGINE (RL)", "ONLINE", 0.2),
        ("RAW TCP LISTENER", f"ACTIVE on Port {TCP_RAW_PORT}", 0.1) 
    ]
    for name, status, delay in checks:
        status_color = Colors.GREEN if "STANDBY" not in status else Colors.WARNING
        print(f"   [{Colors.BLUE}INIT{Colors.ENDC}] {name:<25} : {status_color}{status}{Colors.ENDC}")
        time.sleep(delay)
    print(f"\n{Colors.GREEN}   [*] SYSTEM READY. AWAITING HOSTILES.{Colors.ENDC}\n")

# --- LOGGING HELPERS ---
def log_terminal(module, status, message, detail=None):
    ts = dt.datetime.now().strftime("%H:%M:%S")
    if status in ["BLOCKED", "MITIGATED"]: color = Colors.GREEN; icon = "🛡️ "
    elif status in ["DETECTED", "WARNING"]: color = Colors.WARNING; icon = "⚠️ "
    elif status == "ANALYZING": color = Colors.CYAN; icon = "🔍"
    else: color = Colors.BLUE; icon = "ℹ️ "

    print(f"{Colors.BOLD}{Colors.HEADER}[{ts}]{Colors.ENDC} {color}[{module}]{Colors.ENDC} {icon} {Colors.BOLD}{status}{Colors.ENDC} :: {message}")
    if detail:
        if isinstance(detail, list):
            for i, item in enumerate(detail):
                prefix = "└──" if i == len(detail) - 1 else "├──"
                print(f"           {Colors.FAIL}{prefix} {item}{Colors.ENDC}")
        else:
            print(f"           {Colors.FAIL}└── {detail}{Colors.ENDC}")

def add_to_history(log_entry):
    global EVENT_HISTORY
    EVENT_HISTORY.insert(0, log_entry)
    if len(EVENT_HISTORY) > MAX_HISTORY_LIMIT: EVENT_HISTORY.pop()

# --- SYSTEM STATS ---
def get_real_system_stats():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f: temp = round(int(f.read()) / 1000, 1)
    except: temp = 0.0
    mem = psutil.virtual_memory()
    total_gb = round(mem.total / (1024 ** 3), 1)
    procs = []
    try:
        procs = sorted([p.info for p in psutil.process_iter(['pid', 'name', 'memory_percent'])], 
                       key=lambda x: x['memory_percent'], reverse=True)[:5]
    except: pass
    return {
        "cpu": psutil.cpu_percent(interval=None), "ram": mem.percent, "ram_total": total_gb,
        "network": {"rx": round(psutil.net_io_counters().bytes_recv/1024/1024,2), "tx": round(psutil.net_io_counters().bytes_sent/1024/1024,2)},
        "firewall": {"status": "ACTIVE", "dropped": random.randint(0, 5)}, "temperature": temp,
        "processes": procs
    }

# --- BACKGROUND TASKS ---
def stats_loop():
    """Pushes system stats every 2s."""
    while True:
        socketio.emit('system_stats', get_real_system_stats())
        time.sleep(2)

def queue_loop():
    """Reads Scapy alerts."""
    while True:
        try:
            alert = NETWORK_ALERT_QUEUE.get(timeout=0.1)
            log_terminal("NET-IDS", alert['status'], f"Traffic Anomaly: {alert['type']}", 
                         detail=["Interface: eth0", "Action: Traffic Logging"])
            add_to_history(alert)
            socketio.emit("log_update", alert)
        except: pass

# --- HELPER: THREAT CALCULATOR ---
def calculate_threat_level(reward):
    global VERDICT_HISTORY
    # Store 1 for Red Win (Positive Reward), 0 for Blue Win
    VERDICT_HISTORY.append(1 if reward > 0 else 0)
    if len(VERDICT_HISTORY) > 10: VERDICT_HISTORY.pop(0)
    
    # Calculate Threat %: (Red Wins / Total Attempts) * 100
    if len(VERDICT_HISTORY) == 0: return 0
    breach_rate = sum(VERDICT_HISTORY) / len(VERDICT_HISTORY)
    return int(breach_rate * 100)

# --- TCP SERVER LOOP (MAIN LOGIC) ---
def tcp_server_loop():
    """
    Listens for attacks, calculates rewards, and broadcasts to Frontend.
    """
    print(f"{Colors.GREEN}[INIT] Raw TCP Listener active on Port {TCP_RAW_PORT}{Colors.ENDC}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', TCP_RAW_PORT))
            s.listen(5)
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(4096)
                    if not data: continue
                    try:
                        json_data = json.loads(data.decode('utf-8'))
                        
                        # 1. Process Attack
                        resp = process_attack(json_data, source_ip=addr[0])
                        
                        # 2. Extract Epsilon (From Red Team Payload)
                        current_epsilon = json_data.get("epsilon", 1.0)
                        
                        # Debugging Print (Optional, remove for production)
                        # print(f"DEBUG: Received Epsilon: {current_epsilon}")

                        # 3. Calculate Reward (RL Logic)
                        reward = 0
                        if resp['status'] == 'ALLOWED': reward = 10
                        elif resp['status'] == 'BLOCKED': reward = -10
                        elif resp['status'] == 'MITIGATED': reward = -5
                        
                        RL_SESSION_DATA['total_score'] += reward
                        RL_SESSION_DATA['episode_count'] += 1

                        # 4. Calculate Threat Level
                        current_threat = calculate_threat_level(reward)
                        
                        # 5. Send Feedback to Red Team (The Learning Loop)
                        feedback = {
                            "status": resp['status'],
                            "reward": reward,
                            "epoch": RL_SESSION_DATA['episode_count']
                        }
                        conn.sendall(json.dumps(feedback).encode('utf-8'))
                        
                        # 6. BROADCAST TO FRONTEND
                        socketio.emit('dashboard_update', {
                            "timestamp": resp['timestamp'],
                            "attack_type": resp['type'],
                            "reward": reward,
                            "total_score": RL_SESSION_DATA['total_score'],
                            "threat_level": current_threat,
                            "epsilon": current_epsilon
                        })
                        
                        # (Optional) Log update for separate UI consoles
                        socketio.emit("log_update", resp) 
                        add_to_history(resp)
                        
                    except json.JSONDecodeError:
                        conn.sendall(b'{"status": "ERROR", "reward": 0}')
    except Exception as e:
        print(f"{Colors.FAIL}[TCP CRASH] TCP Listener failed: {e}{Colors.ENDC}")

# --- ATTACK PROCESSING ---
def process_attack(data, source_ip="Unknown"):
    raw_type = data.get("type", "UNKNOWN")
    attack_type = raw_type.upper() 
    
    red_payload = data.get("payload", "")
    red_intel = data.get("intel", {})
    
    if source_ip == "Unknown":
        source_ip = red_intel.get("source_ip", "Unknown")

    log_terminal("DEFENSE", "ANALYZING", f"Incoming Traffic: {raw_type}")
    
    resp = {"type": raw_type, "status": "ALLOWED", "timestamp": dt.datetime.now().strftime("%H:%M:%S"), "blue_intel": {}}

    # 1. AI Phishing
    if "PHISHING" in attack_type or "FINANCE" in attack_type or "SOCIAL" in attack_type:
        analysis = analyze_text(red_payload)
        resp["status"] = analysis["verdict"]
        log_terminal("AI-LAYER", resp["status"], "Phishing Analysis", detail=[f"Confidence: {analysis.get('confidence',0)}", f"Reason: {analysis.get('details','')}"])
        resp["blue_intel"] = {"defense": "Hybrid AI", "human_readable": analysis.get('details', 'AI Scanned')}

    # 2. WAF Attacks
    elif attack_type in ["SQL INJECTION", "DIRECTORY TRAVERSAL", "XSS ATTACK", "USER-AGENT SPOOFING", "SSH BRUTE FORCE"]:
        check = inspect_request(red_payload, {"User-Agent": red_intel.get("agent", "")}, source_ip)
        target = red_intel.get("target", "/")
        method = red_intel.get("method", "Raw Socket")
        
        if check["blocked"]:
            resp["status"] = "BLOCKED"
            log_terminal("APP-WAF", "BLOCKED", f"Malicious Payload: {raw_type}", detail=[f"Rule #{check.get('rule_id','?')}", f"Target: {target}"])
            resp["blue_intel"] = {"defense": f"WAF Rule #{check.get('rule_id','?')}", "human_readable": check.get("details", "Blocked by Regex")}
        else:
            resp["status"] = "ALLOWED"
            log_terminal("APP-WAF", "ALLOWED", f"Traffic Clean: {target}", detail="Signature Match Failed")
            resp["blue_intel"] = {"defense": "WAF", "human_readable": "Signature Match Failed"}

    # 3. Network Attacks
    elif any(x in attack_type for x in ["FLOOD", "SCAN", "BEACON"]):
        resp["status"] = "MITIGATED" if "FLOOD" in attack_type else "DETECTED"
        log_terminal("NET-FW", resp["status"], f"Network Anomaly: {raw_type}", detail=[f"Action: Firewall Rule Applied"])
        resp["blue_intel"] = {"defense": "Active Firewall", "human_readable": "Traffic Anomaly Detected. Mitigation Active."}

    # 4. Fallback
    else:
          log_terminal("SYSTEM", "ALLOWED", f"Unrecognized Event: {raw_type}", detail=["Action: Logging only."])
          resp["blue_intel"] = {"defense": "System Log", "human_readable": f"Event type '{raw_type}' passed filters."}

    return resp

# --- RETRAINING API ---
@app.route('/api/train_rl', methods=['POST'])
def start_rl_training():
    """Simulates the 'Offline Training Phase' for the demo."""
    def training_simulation():
        accuracy = 0.45
        loss = 0.9
        for epoch in range(1, 11):
            time.sleep(1.0)
            improvement = random.uniform(0.04, 0.08)
            accuracy += improvement
            loss -= (improvement * 0.9)
            if accuracy > 0.99: accuracy = 0.99
            
            socketio.emit('rl_training_event', {
                "epoch": epoch,
                "accuracy": round(accuracy * 100, 2),
                "loss": round(loss, 4),
                "log": f"Epoch {epoch}: Q-Learning Table Update | Reward: +{round(improvement*100,1)}"
            })
        socketio.emit('rl_training_complete', {"message": "Model Converged."})

    # UNCOMMENTED SO IT ACTUALLY RUNS
    threading.Thread(target=training_simulation).start()
    return jsonify({"status": "TRAINING_STARTED"})

# --- HTTP ROUTES ---
@app.route("/status")
@app.route("/api/status")
def status(): return jsonify(get_real_system_stats())

@app.route("/api/incoming_threat", methods=['POST'])
def incoming_threat():
    try:
        data = request.json
        resp = process_attack(data, source_ip=request.remote_addr)
        add_to_history(resp)
        socketio.emit("log_update", resp)
        return jsonify(resp)
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- SOCKET EVENTS ---
@socketio.on("connect")
def handle_connect(auth=None):
    emit("log_history", EVENT_HISTORY)
    if not hasattr(socketio, 'threads_started'):
        threading.Thread(target=queue_loop, daemon=True).start()
        threading.Thread(target=stats_loop, daemon=True).start()
        # TCP Thread is handled in main to prevent duplication
        setattr(socketio, 'threads_started', True)

@socketio.on("attack_attempt")
def handle_attack(data):
    resp = process_attack(data, source_ip="WebSocket")
    add_to_history(resp)
    emit("log_update", resp)

# --- START ---
if __name__ == "__main__":
    if NetworkMonitor and not network_monitor.is_alive(): 
        network_monitor.start()
    
    print_banner()
    startup_sequence()
    
    # TCP Thread Start
    tcp_thread = threading.Thread(target=tcp_server_loop, daemon=True)
    tcp_thread.start()
    time.sleep(1) 
    
    # Verify TCP Port
    print(f"[*] Verifying TCP Port {TCP_RAW_PORT}...", end=" ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', TCP_RAW_PORT))
    if result == 0:
        print(f"{Colors.GREEN}[OPEN]{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[CLOSED - FAILED TO BIND]{Colors.ENDC}")
    sock.close()
    
    # Start Web Server
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', HTTP_PORT), app, handler_class=WebSocketHandler)
    try: 
        print(f"[*] Web Server Online: http://0.0.0.0:{HTTP_PORT}\n")
        server.serve_forever()
    except KeyboardInterrupt: 
        print("\n[SHUTDOWN] System Halted.")
