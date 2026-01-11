# defenses/waf.py
import re
import time

# --- CONFIGURATION ---
BRUTE_FORCE_THRESHOLD = 3
BRUTE_FORCE_WINDOW = 60 # seconds

# --- GLOBAL STATE ---
# Stores { "IP_ADDRESS": [timestamp1, timestamp2, ...] }
IP_TRACKER = {}

def inspect_request(payload: str, headers: dict, client_ip: str) -> dict:
    """
    Analyzes HTTP payloads for SQLi, XSS, and tracks Brute Force attempts.
    """
    global IP_TRACKER
    payload_upper = payload.upper()
    
    # 1. SQL Injection Rules
    if re.search(r"('|\")\s*OR\s*('|\")?\d+('|\")?\s*(=|LIKE)\s*('|\")?\d+", payload_upper):
        return {"blocked": True, "rule_id": "942", "details": "SQL Logic Tautology (e.g., OR 1=1)"}
    
    if "UNION SELECT" in payload_upper or "DROP TABLE" in payload_upper:
        return {"blocked": True, "rule_id": "942", "details": "SQL Injection Command Detected"}

    # 2. XSS Rules
    if "<SCRIPT>" in payload_upper or "ONERROR=" in payload_upper or "JAVASCRIPT:" in payload_upper:
        return {"blocked": True, "rule_id": "941", "details": "XSS Detected: HTML Tags or Script code found."}

    # 3. Directory Traversal
    if "../" in payload or "..\\" in payload:
        return {"blocked": True, "rule_id": "930", "details": "Path Traversal Attempt"}

    # 4. User-Agent Check
    ua = headers.get("User-Agent", "")
    if "Evil" in ua or "Scanner" in ua or "sqlmap" in ua:
        return {"blocked": True, "rule_id": "701", "details": f"Malicious User-Agent: {ua}"}

    # 5. BRUTE FORCE LOGIC (The Fix)
    # We treat any request with "LOGIN" or "PASSWORD" in the payload as a login attempt
    if "LOGIN" in payload_upper or "PASSWORD" in payload_upper or "ADMIN" in payload_upper:
        current_time = time.time()
        
        # Initialize list for this IP if not exists
        if client_ip not in IP_TRACKER:
            IP_TRACKER[client_ip] = []
            
        # Clean up old attempts (older than window)
        IP_TRACKER[client_ip] = [t for t in IP_TRACKER[client_ip] if current_time - t < BRUTE_FORCE_WINDOW]
        
        # Add current attempt
        IP_TRACKER[client_ip].append(current_time)
        
        count = len(IP_TRACKER[client_ip])
        
        if count > BRUTE_FORCE_THRESHOLD:
            return {
                "blocked": True, 
                "rule_id": "402", 
                "details": f"Brute Force Detected: {count} attempts in {BRUTE_FORCE_WINDOW}s from {client_ip}"
            }

    return {"blocked": False, "rule_id": "0", "details": "Traffic Clean"}
