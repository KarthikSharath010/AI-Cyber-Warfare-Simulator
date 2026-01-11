const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const http = require('http');           // <--- REQUIRED for Sockets
const { Server } = require("socket.io"); // <--- REQUIRED for Sockets

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

// --- 1. SETUP SOCKET.IO ---
// We wrap Express in an HTTP server
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*", // Allow React to connect
    methods: ["GET", "POST"]
  }
});

io.on('connection', (socket) => {
  console.log('[SERVER] Frontend connected via Socket:', socket.id);
});

// --- 2. SYSTEM MONITOR ROUTE (Local Simulation) ---
app.get('/api/status', (req, res) => {

  // FIXED: Simulate a Raspberry Pi (4GB Total)
  const totalRam = 4;

  // Random usage between 1.0 GB and 3.5 GB (Always less than 4)
  const randomUsage = Math.random() * 2.5 + 1.0;
  const ramUsage = parseFloat(randomUsage.toFixed(2));

  // Random CPU
  const cpuLoad = Math.floor(Math.random() * 40) + 10;

  res.json({
    cpu: cpuLoad,
    ram: ramUsage,       // Send realistic usage (e.g., 2.4 GB)
    ram_total: totalRam, // Send fixed Total (4 GB)
    network: {
      rx: Math.floor(Math.random() * 3000) + 500,
      tx: Math.floor(Math.random() * 800) + 100
    },
    firewall: {
      status: "OK",
      dropped: Math.floor(Math.random() * 5)
    },
    processes: [
      { pid: 1092, name: "/usr/sbin/sshd" },
      { pid: 3392, name: "node server.js" },
      { pid: 4401, name: "/usr/bin/dockerd" },
      { pid: 5102, name: "kworker/u12:0" },
      { pid: 6621, name: "python3 waf_agent.py" }
    ]
  });
});

// --- 3. ATTACK ROUTE (With Socket Trigger) ---
app.post('/api/attack', (req, res) => {
  const { name } = req.body;
  console.log(`[SERVER] Launching attack: ${name}`);

  // 1. Spawn Python Script (Optional, if you have engine.py)
  // const pythonProcess = spawn('python', ['engine.py', name]);

  // 2. SIMULATE RESPONSE (So the UI updates immediately)
  setTimeout(() => {

    // A. Send Socket Event (Updates Blue Terminal Logs)
    io.emit("log_update", {
      status: "BREACH",
      type: name,
      blue_intel: {
        human_readable: `Traffic anomaly detected matching ${name} signature.`
      }
    });

    // B. Send HTTP Response (Updates Red Terminal)
    res.json({
      status: "BREACH",
      red_log: `[+] ${name} executed successfully.`,
      blue_log: `[!] ALERT: Signature match for ${name}`
    });

    // C. SEND RL DASHBOARD UPDATE (Event Driven now!)
    io.emit("dashboard_update", {
      timestamp: new Date().toLocaleTimeString(),
      total_score: Math.floor(Math.random() * 20) + 10, // Small positive reward
      threat_level: 95, // High threat during attack
      attack_type: name
    });

  }, 2000); // 2 second delay for realism
});

// --- 4. MODEL HOT-SWAP (Simulate Loading) ---
app.post('/api/load_pretrained', (req, res) => {
  console.log("[SERVER] Loading Pre-Trained Policy...");

  // Simulate a delay for "loading" the heavy model
  setTimeout(() => {
    io.emit("rl_training_complete", {
      epsilon: 0.05,
      accuracy: 0.98
    });
    console.log("[SERVER] Model Loaded. Epsilon set to 0.05");
  }, 3000); // 3-second delay

  res.json({ status: "LOADING_STARTED" });
});

// --- 5. PERIODIC DATA EMISSION (ONLY SYSTEM STATS) ---
// This keeps the system stats alive, but REMOVES the fake RL dashboard updates
setInterval(() => {
  const totalRam = 4;
  const cpuLoad = Math.floor(Math.random() * 40) + 10;
  const ramUsage = parseFloat((Math.random() * 2.5 + 1.0).toFixed(2));

  const systemStats = {
    cpu: cpuLoad,
    ram: ramUsage,
    ram_total: totalRam,
    network: {
      rx: Math.floor(Math.random() * 3000) + 500,
      tx: Math.floor(Math.random() * 800) + 100
    },
    firewall: {
      status: "OK",
      dropped: Math.floor(Math.random() * 5)
    },
    processes: [
      { pid: 1092, name: "/usr/sbin/sshd" },
      { pid: 3392, name: "node server.js" },
    ]
  };

  io.emit("system_stats", systemStats);
  // NOTE: We do NOT emit "dashboard_update" here anymore.
  // Updates only happen on actual attacks.

}, 2000);

// --- 6. START SERVER ---
// IMPORTANT: Use 'server.listen', NOT 'app.listen'
server.listen(PORT, '0.0.0.0', () => {
  console.log(`[SERVER v2 (Manual Mode)] Backend (HTTP + Socket) running on http://localhost:${PORT}`);
});
