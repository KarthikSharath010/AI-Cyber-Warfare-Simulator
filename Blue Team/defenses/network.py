import threading
import queue
import time
import datetime as dt
import statistics
import random
from collections import deque, defaultdict

# CONFIGURATION
HONEY_PORT = 6666 
SSH_PORT = 22
SSH_THRESHOLD = 4  # Max new SSH connections per 10s before flagging

try:
    from scapy.all import sniff, UDP, TCP, IP
    SCAPY_AVAILABLE = True
except ImportError:
    print("[WARNING] Scapy not found. Network monitoring will be disabled.")
    SCAPY_AVAILABLE = False

class NetworkMonitor(threading.Thread):
    def __init__(self, alert_queue: queue.Queue, interface='eth0'):
        super().__init__()
        self.alert_queue = alert_queue
        self.interface = interface
        self.stop_event = threading.Event()
        self.daemon = True 
        
        # --- STATE ---
        self.traffic_history = deque(maxlen=20) 
        self.current_second_count = 0
        self.last_check_time = time.time()

        self.beacon_tracker = defaultdict(lambda: deque(maxlen=10))
        self.scanned_ports = defaultdict(set)
        
        # NEW: SSH Connection Tracker (IP -> list of timestamps)
        self.ssh_attempts = defaultdict(lambda: deque(maxlen=10))

    def run(self):
        if not SCAPY_AVAILABLE: return
        print(f"[*] Advanced Network Monitor running on {self.interface}")
        try:
            sniff(prn=self.packet_callback, store=0, iface=self.interface,
                  stop_filter=lambda p: self.stop_event.is_set())
        except Exception as e:
            print(f"[ERROR] Monitor failed: {e}")

    def packet_callback(self, packet):
        if not packet.haslayer(IP): return
        
        src_ip = packet[IP].src
        now = time.time()
        
        # --- A. HONEY PORT TRAP ---
        if packet.haslayer(TCP) and packet[TCP].dport == HONEY_PORT:
            self._emit_alert("Port Scanning", "BLOCKED", 
                             f"Trap Triggered! IP {src_ip} touched honey port.", 
                             {"ip": src_ip, "trap": "Honey Port"})
            return

        # --- B. SSH BRUTE FORCE DETECTION (NEW) ---
        # Look for NEW connection attempts (SYN) to Port 22
        if packet.haslayer(TCP) and packet[TCP].dport == SSH_PORT and packet[TCP].flags == 'S':
            self.ssh_attempts[src_ip].append(now)

        # --- C. STATS COLLECTION ---
        self.current_second_count += 1
        
        if packet.haslayer(TCP) or packet.haslayer(UDP):
            self.beacon_tracker[src_ip].append(now)

        if packet.haslayer(TCP) and packet[TCP].flags == 'S':
            self.scanned_ports[src_ip].add(packet[TCP].dport)

        # --- D. SECONDLY ANALYSIS ---
        if now - self.last_check_time >= 1.0:
            self._analyze_traffic_window()
            self.last_check_time = now
            self.current_second_count = 0 

    def _analyze_traffic_window(self):
        """Runs once per second."""
        now = time.time()

        # 1. SSH BRUTE FORCE CHECK
        for ip, timestamps in list(self.ssh_attempts.items()):
            # Count attempts in the last 10 seconds
            recent_attempts = [t for t in timestamps if now - t < 10]
            if len(recent_attempts) > SSH_THRESHOLD:
                self._emit_alert("SSH Brute Force", "BLOCKED", 
                                 f"Brute Force Detected: {len(recent_attempts)} SSH attempts in 10s from {ip}.", 
                                 {"source_ip": ip, "attempts": len(recent_attempts)})
                # Clear to avoid spamming
                self.ssh_attempts[ip].clear()

        # 2. FLOOD DETECTION (Z-Score)
        self.traffic_history.append(self.current_second_count)
        if len(self.traffic_history) > 5:
            mean = statistics.mean(self.traffic_history)
            std_dev = statistics.stdev(self.traffic_history) if len(self.traffic_history) > 1 else 1
            if std_dev == 0: std_dev = 1 
            z_score = (self.current_second_count - mean) / std_dev
            
            if z_score > 3.0 and self.current_second_count > 20:
                self._emit_alert("QUIC Flood (DoS)", "MITIGATED", 
                                 f"Traffic Anomaly (Z:{z_score:.1f}). Volume: {self.current_second_count}/s",
                                 {"z_score": round(z_score, 2), "rate": self.current_second_count})

        # 3. BEACON DETECTION
        for ip, timestamps in list(self.beacon_tracker.items()):
            if len(timestamps) >= 8:
                deltas = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
                variance = statistics.variance(deltas) if len(deltas) > 1 else 1
                if variance < 0.005:
                    self._emit_alert("Polymorphic Beacon", "DETECTED", 
                                     f"C2 Pattern detected. Variance: {variance:.5f}s", 
                                     {"jitter": f"{variance:.5f}"})
                    self.beacon_tracker[ip].clear()

        # 4. PORT SCANNING
        for ip, ports in list(self.scanned_ports.items()):
            if len(ports) > 5:
                self._emit_alert("Port Scanning", "DETECTED", 
                                 f"Port Sweep detected. {len(ports)} ports targeted.", 
                                 {"ports": len(ports)})
        self.scanned_ports.clear()

    def _emit_alert(self, type, status, human_msg, intel):
        alert = {
            "type": type,
            "status": status,
            "timestamp": dt.datetime.now().strftime("%H:%M:%S"),
            "red_payload_preview": "N/A (L3/L4 Traffic)",
            "red_intel": intel,
            "blue_intel": {
                "defense": "Active Firewall",
                "human_readable": human_msg,
                "action": "DROP/ALERT"
            },
        }
        self.alert_queue.put(alert)
