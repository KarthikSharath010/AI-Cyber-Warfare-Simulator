# ⚔️ AI Cyber Warfare Simulator

> **A real-time, adversarial simulation between an Reinforcement Learning (RL) Red Team and an AI-enhanced Blue Team.**
> *Experience the future of automated cyber defense.*

![Status](https://img.shields.io/badge/Status-Active-success)
![Defense](https://img.shields.io/badge/Blue%20Team-AI%20Powered-blue)
![Attack](https://img.shields.io/badge/Red%20Team-RL%20Agent-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📖 Overview

The **AI Cyber Warfare Simulator** is a cutting-edge platform designed to demonstrate the battle between automated attackers and defenders. 
*   **🔴 Red Team (Attacker):** An RL agent (Q-Learning) that evolves its strategies based on the defender's response. It learns which attacks bypass the firewall and WAF.
*   **🛡️ Blue Team (Defender):** A defensive suite equipped with signature-based WAF, Network Anomaly Detection, and Threat Intelligence scoring.
*   **🖥️ War Room Dashboard:** A futuristic, "Mission Impossible" style frontend to visualize the warfare in real-time.

## ✨ Features

### 🔴 Red Team (The Attacker)
*   **Reinforcement Learning:** Uses Q-Learning to maximize the "reward" (successful breaches).
*   **Adaptive Strategy:** Shifts from random exploration to exploiting weaknesses (Epsilon-Greedy).
*   **Arsenal:**
    *   SQL Injection, XSS, Directory Traversal
    *   Phishing Simulations (AI Text Generation)
    *   Network Floods (SYN, UDP) & Port Scanning
    *   Polymorphic Payloads

### 🛡️ Blue Team (The Defender)
*   **Web Application Firewall (WAF):** Inspects payloads for known malicious signatures.
*   **Phishing Detection:** NLP-based text analysis to flag social engineering attempts.
*   **Network Monitor:** Real-time packet inspection (simulated/active) for anomaly detection.
*   **Threat Intelligence:** Calculates a "Threat Level" based on breach success rate.

### 🖥️ Frontend (The War Room)
*   **Real-Time Data:** Live WebSocket connection to the battlefield.
*   **Interactive Visuals:**
    *   **Attack Log:** Streaming terminal of events.
    *   **Live Metrics:** CPU/RAM/Network utilization.
    *   **RL Dashboard:** Visualizing the AI's learning curve (Rewards vs. Episodes).
*   **Control Center:** Launch simulated attacks or trigger RL training sessions manually.

---

## 🛠️ Tech Stack

### Frontend
-   **React 19** & **Vite**: Ultra-fast UI framework.
-   **TailwindCSS**: For that sleek, geometric dark theme.
-   **Framer Motion**: Smooth, cinematic animations.
-   **Recharts**: Data visualization for AI metrics.
-   **Socket.IO Client**: Real-time bidirectional communication.

### Backend (Blue Team)
-   **Python 3.10+**
-   **Flask**: Lightweight web server and API provider.
-   **Flask-SocketIO**: Managing real-time events.
-   **Scapy**: For network packet manipulation and sniffing.
-   **Gevent**: Asynchronous worker for high-performance handling.

### Red Team Agent
-   **Python 3.10+**
-   **NumPy**: For Q-Table matrix operations.
-   **Requests**: For payloads transmission.

---

## 🚀 Getting Started

### Prerequisites
*   Node.js (v18+)
*   Python (v3.10+)

### 1. Installation

**Clone the repository:**
```bash
git clone https://github.com/KarthikSharath010/AI-Cyber-Warfare-Simulator.git
cd AI-Cyber-Warfare-Simulator
```

**Setup Blue Team (Backend):**
```bash
cd "Source Code/Blue Team"
pip install -r requirements.txt  # (Create this file if missing based on imports)
# Common libs: flask flask-socketio flask-cors psutil scapy numpy gevent
```

**Setup Frontend:**
```bash
cd "Source Code/Frontend/frontend"
npm install
```

### 2. Running the Simulator

**Step 1: Start the Blue Team (Defender)**
```bash
# In 'Blue Team' directory
python app.py
```
*Server starts on `http://0.0.0.0:5000` (Web) and `:6000` (Raw TCP).*

**Step 2: Start the Frontend**
```bash
# In 'Frontend/frontend' directory
npm run dev
```
*Access the dashboard at the URL provided by Vite (usually `http://localhost:5173`).*

**Step 3: Unleash the Red Team (Attacker)**
```bash
# In 'Source Code/Red Team' directory
python red_rl_loop_temp_1.py
```
*The agent will begin attacking the Blue Team server automatically.*

---
