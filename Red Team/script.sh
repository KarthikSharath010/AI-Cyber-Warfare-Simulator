#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------
# Load GEMINI_API_KEY safely
# -----------------------------
if [[ -n "${GEMINI_API_KEY:-}" ]]; then
  export GEMINI_API_KEY
elif [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
  : "${GEMINI_API_KEY:?Add GEMINI_API_KEY to .env}"
  export GEMINI_API_KEY
else
  echo "Set GEMINI_API_KEY in your environment or put it in .env (GEMINI_API_KEY=...)" >&2
  exit 1
fi

# -----------------------------
# Target configuration (hardcoded)
# -----------------------------
TARGET_IP="100.67.198.107"
PORT="6000"
PROTO="tcp"

# -----------------------------
# Attack menu (display only)
# -----------------------------
echo "Select Attack:"
echo "1. Phishing"
echo "2. SQL Injection"
echo "3. QUIC Attack"
echo "4. Polymorphic Beacon"
echo "5. Directory Traversal"
echo "6. XSS"
echo "7. Port Scanning"
echo "8. SSH Bruteforce"
echo "9. User-Agent Spoofing"
echo "10. SYN Flood"
echo

read -rp "Enter choice [1-10]: " choice
echo

# -----------------------------
# Execute attack (hardcoded)
# -----------------------------
case "$choice" in
  1)
    python A1_phish.py
    ;;
  2)
    python3 A2_sqli.py "$TARGET_IP" --port "$PORT" --proto "$PROTO"
    ;;
  3)
    python A3_quic.py "$TARGET_IP" --port "$PORT" --proto "$PROTO"
    ;;
  4)
    python A4_poly.py "$TARGET_IP" --port "$PORT" --proto "$PROTO" --mode jitter
    ;;
  5)
    python A5_poly.py "$TARGET_IP" --port "$PORT" --proto "$PROTO"
    ;;
  6)
    python A6_xss.py "$TARGET_IP" --port "$PORT" --proto "$PROTO"
    ;;
  7)
    python A7_portscan.py "$TARGET_IP" --port "$PORT" --proto "$PROTO"
    ;;
  8)
    python A8_sshbf.py "$TARGET_IP" --port "$PORT" --proto "$PROTO"
    ;;
  9)
    python A9_user_spoof.py "$TARGET_IP" --port "$PORT" --proto "$PROTO"
    ;;
  10)
    python A10_syn_flood.py "$TARGET_IP" --port "$PORT" --proto "$PROTO"
    ;;
  *)
    echo "❌ Invalid option"
    exit 1
    ;;
esac
