import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import Sidebar from "./components/Sidebar";
import RLDashboard from "./components/RLDashboard";
import WarRoom from "./components/WarRoom";
import IntelData from "./components/IntelData";
import CRTOverlay from "./components/CRTOverlay";
import { Activity, ShieldCheck, Users, Cpu, Server, Wifi, WifiOff } from "lucide-react";

// UPDATE THIS IF YOUR FLASK APP IS ON A DIFFERENT IP
const BACKEND_URL = "http://100.67.198.107:5000";

export default function App() {
   const [view, setView] = useState("OVERVIEW");
   const [socket, setSocket] = useState(null);
   const [isConnected, setIsConnected] = useState(false); // Connection State

   // State for System Data
   const [systemData, setSystemData] = useState({
      cpu: 0,
      ram: 0,
      ram_total: 0,
      network: { rx: 0, tx: 0 },
      processes: []
   });

   // State for Logs & Attacks
   const [logs, setLogs] = useState([]);
   const [redOutput, setRedOutput] = useState([]); // Attacks
   const [blueOutput, setBlueOutput] = useState([]); // Defense Logs

   // Dashboard Metrics
   const [metrics, setMetrics] = useState({
      requests: 0,
      mitigated: 0,
      adversaries: 0,
      score: 0
   });

   const [epsilon, setEpsilon] = useState(1.0); // Lifted State

   useEffect(() => {
      console.log(`[App] Attempting connection to ${BACKEND_URL}...`);

      const newSocket = io(BACKEND_URL, {
         transports: ["websocket", "polling"],
         cors: { origin: "*" },
         reconnectionAttempts: 5,
         timeout: 5000
      });
      setSocket(newSocket);

      // --- CONNECTION HANDLERS ---
      newSocket.on("connect", () => {
         console.log("[App] Socket CONNECTED to Backend!");
         setIsConnected(true);
      });

      newSocket.on("disconnect", (reason) => {
         console.warn("[App] Socket DISCONNECTED:", reason);
         setIsConnected(false);
      });

      newSocket.on("connect_error", (err) => {
         console.error("[App] Socket CONNECTION ERROR:", err.message);
         setIsConnected(false);
      });

      // 1. LISTEN FOR SYSTEM STATS
      newSocket.on("system_stats", (data) => {
         setSystemData(data);
      });

      // 2. LISTEN FOR LOGS/ATTACKS
      newSocket.on("log_update", (data) => {
         const timestamp = new Date().toLocaleTimeString();

         setLogs(prev => [{ time: timestamp, status: data.status, message: `${data.type} detected` }, ...prev].slice(0, 50));

         if (data.status === "BLOCKED" || data.status === "MITIGATED") {
            setBlueOutput(prev => [{ text: `[${timestamp}] DEFENSE: ${data.type} blocked.`, type: "success" }, ...prev].slice(0, 50));
            setMetrics(m => ({ ...m, mitigated: m.mitigated + 1, requests: m.requests + 1 }));
         } else {
            setRedOutput(prev => [{ text: `[${timestamp}] ATTACK: ${data.type} payload sent.`, type: "error" }, ...prev].slice(0, 50));
            setMetrics(m => ({ ...m, adversaries: 1, requests: m.requests + 1 }));
         }
      });

      // 3. LISTEN FOR RL DASHBOARD UPDATES
      newSocket.on("dashboard_update", (data) => {
         setMetrics(m => ({ ...m, score: data.total_score }));
         if (data.epsilon) setEpsilon(Number(data.epsilon));
      });

      return () => newSocket.disconnect();
   }, []);

   return (
      <div className="flex h-screen overflow-hidden relative">
         <CRTOverlay />

         <Sidebar view={view} setView={setView} />

         <main className="flex-1 flex flex-col min-w-0 bg-transparent relative z-10">

            {/* HEADER */}
            <header className="h-20 flex flex-col justify-end px-10 pb-4">
               <div className="flex items-end justify-between w-full">
                  <div>
                     <div className="text-dim text-[10px] tracking-widest font-bold uppercase mb-1">Current View</div>
                     <h1 className="text-3xl font-bold tracking-tight text-main leading-none">
                        {{
                           OVERVIEW: "Overview",
                           WAR_ROOM: "War Room",
                           RL_LAB: "RL Lab",
                           INTEL: "Intel Data",
                        }[view]}
                     </h1>
                  </div>

                  {/* CONNECTION STATUS BADGE */}
                  <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all duration-500
                     ${isConnected
                        ? "border-green-500/30 bg-green-500/10 text-green-500"
                        : "border-red-500/30 bg-red-500/10 text-red-500 animate-pulse"
                     }`}
                  >
                     {isConnected ? (
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                     ) : (
                        <WifiOff size={12} />
                     )}
                     <span className="text-xs font-semibold">
                        {isConnected ? "System Operational" : "Backend Offline"}
                     </span>
                  </div>
               </div>
            </header>

            {/* CONTENT */}
            {/* CONTENT */}
            <div className="flex-1 overflow-y-auto custom-scrollbar px-10 pb-10 pt-6">
               {/* OVERVIEW WRAPPER */}
               <div className={view === "OVERVIEW" ? "flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out" : "hidden"}>

                  {/* BANNER */}
                  <div className="w-full panel p-8 relative overflow-hidden">
                     <div className={`absolute top-0 left-0 w-1 h-full transition-colors duration-500 ${isConnected ? "bg-[var(--brand-primary)]" : "bg-red-500"}`}></div>
                     <div className="flex items-center gap-3 mb-2">
                        <Server size={20} className={isConnected ? "text-brand" : "text-red-500"} />
                        <h2 className="text-lg font-bold tracking-wide text-main uppercase">Command Center // Overview</h2>
                     </div>
                     <div className={`text-xs font-bold tracking-widest mb-4 ${isConnected ? "text-success" : "text-danger"}`}>
                        {isConnected ? "SYSTEM_READY" : "CONNECTION_REFUSED"}
                     </div>
                     <p className="text-muted max-w-2xl text-sm leading-relaxed">
                        Target Node: {BACKEND_URL}. {isConnected ? "Optimized telemetry stream active." : "Unable to establish handshake. Check network route."}
                     </p>
                  </div>

                  {/* 2. SYSTEM INTEGRITY GRID (NEW REQUESTED CARDS) */}
                  <div className="grid grid-cols-4 gap-6">
                     {/* Network Interface */}
                     <div className="panel p-5 flex flex-col justify-center border-l-4 border-l-blue-500">
                        <div className="flex items-center gap-2 text-[10px] font-bold tracking-widest text-muted uppercase mb-1">
                           <Activity size={14} /> Network Interface
                        </div>
                        <div className="text-lg font-mono font-bold text-main">ONLINE <span className="text-dim text-xs">- {(systemData.network.rx + systemData.network.tx).toFixed(1)}MB</span></div>
                        <div className="text-[10px] text-blue-500 mt-1">eth0</div>
                     </div>

                     {/* Neural Engine */}
                     <div className="panel p-5 flex flex-col justify-center border-l-4 border-l-purple-500">
                        <div className="flex items-center gap-2 text-[10px] font-bold tracking-widest text-muted uppercase mb-1">
                           <Cpu size={14} /> Neural Engine
                        </div>
                        <div className="text-lg font-mono font-bold text-main">ACTIVE <span className="text-dim text-xs">- v2.4</span></div>
                        <div className="text-[10px] text-purple-500 mt-1">TinyBERT Model</div>
                     </div>

                     {/* RL Agent */}
                     <div className="panel p-5 flex flex-col justify-center border-l-4 border-l-yellow-500">
                        <div className="flex items-center gap-2 text-[10px] font-bold tracking-widest text-muted uppercase mb-1">
                           <Users size={14} /> RL Agent
                        </div>
                        <div className="text-lg font-mono font-bold text-main">STANDBY <span className="text-dim text-xs">- PPO</span></div>
                        <div className="text-[10px] text-yellow-500 mt-1">Epsilon {epsilon.toFixed(3)}</div>
                     </div>

                     {/* Firewall */}
                     <div className="panel p-5 flex flex-col justify-center border-l-4 border-l-green-500">
                        <div className="flex items-center gap-2 text-[10px] font-bold tracking-widest text-muted uppercase mb-1">
                           <ShieldCheck size={14} /> Firewall
                        </div>
                        <div className="text-lg font-mono font-bold text-main">ENFORCING <span className="text-dim text-xs">- 12 Rules</span></div>
                        <div className="text-[10px] text-green-500 mt-1">IPTables Active</div>
                     </div>
                  </div>

                  {/* STATS GRID */}
                  <div className="grid grid-cols-4 gap-6">
                     {/* Status Card 1 */}
                     <div className="panel p-6 flex flex-col justify-between h-36">
                        <div className="flex justify-between items-start">
                           <span className="text-dim text-xs font-bold uppercase tracking-wide">Total Requests</span>
                           <Activity className="text-dim" size={20} />
                        </div>
                        <div>
                           <div className="text-3xl font-bold text-main mb-1">{metrics.requests}</div>
                           <div className="text-brand text-xs font-medium">LIVE</div>
                        </div>
                     </div>

                     {/* Status Card 2 */}
                     <div className="panel p-6 flex flex-col justify-between h-36">
                        <div className="flex justify-between items-start">
                           <span className="text-dim text-xs font-bold uppercase tracking-wide">Mitigated</span>
                           <ShieldCheck className="text-dim" size={20} />
                        </div>
                        <div>
                           <div className="text-3xl font-bold text-success mb-1">{metrics.mitigated}</div>
                           <div className="text-muted text-xs font-medium">ACTIVE DEFENSE</div>
                        </div>
                     </div>

                     {/* Status Card 3 */}
                     <div className="panel p-6 flex flex-col justify-between h-36">
                        <div className="flex justify-between items-start">
                           <span className="text-dim text-xs font-bold uppercase tracking-wide">System Load</span>
                           <Cpu className="text-dim" size={20} />
                        </div>
                        <div>
                           <div className="text-3xl font-bold text-main mb-1">{systemData.cpu}%</div>
                           <div className="text-muted text-xs font-medium">
                              RAM: {((systemData.ram / 100) * systemData.ram_total).toFixed(1)}GB / {systemData.ram_total}GB
                           </div>
                        </div>
                     </div>

                     {/* Status Card 4 */}
                     <div className="panel p-6 flex flex-col justify-between h-36">
                        <div className="flex justify-between items-start">
                           <span className="text-dim text-xs font-bold uppercase tracking-wide">RL Score</span>
                           <Users className="text-dim" size={20} />
                        </div>
                        <div>
                           <div className="text-3xl font-bold text-main mb-1">{metrics.score}</div>
                           <div className="text-warning text-xs font-medium">CUMULATIVE REWARD</div>
                        </div>
                     </div>
                  </div>
               </div>


               {/* PERSISTENT WAR ROOM */}
               <div className={view === "WAR_ROOM" ? "h-full animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out" : "hidden"}>
                  <WarRoom
                     systemData={systemData}
                     redOutput={redOutput}
                     logs={logs}
                     onClearLogs={() => setLogs([])}
                  />
               </div>

               {/* PASSING LOGS TO RL DASHBOARD NOW */}
               <div className={view === "RL_LAB" ? "h-full animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out" : "hidden"}>
                  <RLDashboard socket={socket} systemData={systemData} logs={logs} epsilon={epsilon} />
               </div>

               <div className={view === "INTEL" ? "h-full animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out" : "hidden"}>
                  <IntelData />
               </div>

            </div>
         </main >
      </div >
   );
}