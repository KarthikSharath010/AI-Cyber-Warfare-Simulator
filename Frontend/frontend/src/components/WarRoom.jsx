import React, { useRef, useEffect, useState } from "react";
import { Shield, Network, Activity, RefreshCw } from "lucide-react";

// CONFIGURATION
const BLUE_PI_IP = "100.67.198.107";
const RED_PI_IP = "100.110.66.33";

const BLUE_TTYD_URL = `http://${BLUE_PI_IP}:7681`;
const RED_TTYD_URL = `http://${RED_PI_IP}:7682`; // Port 7682 for Red

export default function WarRoom({ systemData, redOutput, logs, onClearLogs }) {
   const logsEndRef = useRef(null);
   const [iframeKey, setIframeKey] = useState(0);

   useEffect(() => {
      if (logsEndRef.current) {
         logsEndRef.current.scrollIntoView({ behavior: "smooth" });
      }
   }, [logs, redOutput]);

   const refreshTerminal = () => {
      setIframeKey(prev => prev + 1);
   };

   return (
      <div className="flex flex-col gap-6 h-full animate-in fade-in duration-500">
         <div className="flex flex-1 gap-6 min-h-0">

            {/* LEFT COL: NODE STATUS - NOW USING REAL DATA */}
            <div className="w-1/4 panel p-6 flex flex-col gap-6">
               <div className="flex items-center gap-2 mb-2 border-b border-[var(--border-base)] pb-3">
                  <Activity size={18} className="text-brand" />
                  <h3 className="text-sm font-bold tracking-[0.2em] text-main uppercase">Node Status</h3>
               </div>

               {/* CPU METRIC */}
               <div>
                  <div className="flex justify-between text-[10px] font-bold tracking-widest text-muted mb-1">
                     <span>CPU LOAD</span>
                     <span className="text-main">{systemData.cpu || 0}%</span>
                  </div>
                  <div className="h-1 w-full bg-[#111] rounded-full overflow-hidden">
                     <div
                        className="h-full bg-blue-600 shadow-[0_0_10px_#2563eb] transition-all duration-500"
                        style={{ width: `${systemData.cpu || 0}%` }}
                     ></div>
                  </div>
               </div>

               {/* RAM METRIC */}
               <div>
                  <div className="flex justify-between text-[10px] font-bold tracking-widest text-muted mb-1">
                     <span>MEMORY</span>
                     <span className="text-main">{systemData.ram || 0}%</span>
                  </div>
                  <div className="h-1 w-full bg-[#111] rounded-full overflow-hidden">
                     <div
                        className="h-full bg-blue-500 transition-all duration-500"
                        style={{ width: `${systemData.ram || 0}%` }}
                     ></div>
                  </div>
               </div>

               {/* NETWORK I/O - REAL DATA */}
               <div className="mt-auto">
                  <div className="flex items-center gap-2 text-[10px] font-bold tracking-widest text-muted mb-2 uppercase">
                     <Network size={12} /> Network I/O (ETH0)
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                     <div className="bg-[var(--bg-subtle)] border border-[var(--border-base)] p-3 rounded flex flex-col items-center">
                        <span className="text-[9px] text-success uppercase mb-1">↓ RX (In)</span>
                        <span className="text-main font-bold font-mono">
                           {systemData.network ? systemData.network.rx : 0} MB
                        </span>
                     </div>
                     <div className="bg-[var(--bg-subtle)] border border-[var(--border-base)] p-3 rounded flex flex-col items-center">
                        <span className="text-[9px] text-brand uppercase mb-1">↑ TX (Out)</span>
                        <span className="text-main font-bold font-mono">
                           {systemData.network ? systemData.network.tx : 0} MB
                        </span>
                     </div>
                  </div>
               </div>

               <div className="text-[9px] text-dim font-mono mt-2 uppercase tracking-widest">
                  Host: Raspberry Pi (Connected)
               </div>
            </div>

            {/* RIGHT COL: TERMINALS */}
            <div className="flex-1 grid grid-cols-2 gap-6">

               {/* RED TEAM TERMINAL (PORT 7682) */}
               <div className="panel p-0 flex flex-col overflow-hidden relative">
                  <div className="bg-[rgba(20,5,5,0.9)] border-b border-red-900/30 p-2 flex items-center justify-between px-4">
                     <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                        <span className="text-[10px] font-bold text-red-500 tracking-[0.2em]">RED TEAM (PI TTYD)</span>
                     </div>
                     <button onClick={refreshTerminal} className="text-red-500 hover:text-white transition-colors">
                        <RefreshCw size={12} />
                     </button>
                  </div>
                  <div className="flex-1 bg-black relative">
                     <iframe
                        key={`red-${iframeKey}`}
                        src={RED_TTYD_URL}
                        className="w-full h-full border-none"
                        title="Red Team Terminal"
                        allow="clipboard-read; clipboard-write"
                     />
                  </div>
               </div>

               {/* BLUE TEAM TERMINAL (PORT 7681) */}
               <div className="panel p-0 flex flex-col overflow-hidden relative">
                  <div className="bg-[rgba(5,10,20,0.9)] border-b border-blue-900/30 p-2 flex items-center justify-between px-4 z-10">
                     <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                        <span className="text-[10px] font-bold text-blue-500 tracking-[0.2em]">BLUE TEAM (PI TTYD)</span>
                     </div>
                     <button onClick={refreshTerminal} className="text-blue-500 hover:text-white transition-colors">
                        <RefreshCw size={12} />
                     </button>
                  </div>

                  <div className="flex-1 bg-black relative">
                     <iframe
                        key={`blue-${iframeKey}`}
                        src={BLUE_TTYD_URL}
                        className="w-full h-full border-none"
                        title="Blue Team Terminal"
                        allow="clipboard-read; clipboard-write"
                     />
                  </div>
               </div>

            </div>
         </div>

         {/* BOTTOM LOGS */}
         <div className="h-48 panel flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-[var(--border-base)] bg-[var(--bg-subtle)]">
               <div className="flex items-center gap-2">
                  <Shield size={14} className="text-muted" />
                  <span className="text-[10px] font-bold tracking-[0.2em] text-muted uppercase">Security Event Logs</span>
               </div>
               <button onClick={onClearLogs} className="text-[9px] text-muted hover:text-main uppercase tracking-widest border border-[var(--border-base)] px-2 py-1 rounded hover:bg-[var(--border-highlight)] transition-colors">
                  Clear Buffer
               </button>
            </div>
            <div className="flex-1 bg-black/50 p-4 overflow-y-auto custom-scrollbar font-mono text-xs">
               {logs.length === 0 ? (
                  <div className="text-dim italic">No active threats detected in current session buffer.</div>
               ) : (
                  logs.map((log, i) => (
                     <div key={i} className="flex gap-4 mb-1.5 border-b border-[var(--border-base)] pb-1 last:border-0">
                        <span className="text-dim min-w-[80px]">{log.time}</span>
                        <span className={`font-bold min-w-[100px] ${log.status === "BLOCKED" ? "text-success" :
                           log.status === "FLAGGED" ? "text-warning" : "text-danger"
                           }`}>
                           [{log.status}]
                        </span>
                        <span className="text-muted">{log.message}</span>
                     </div>
                  ))
               )}
            </div>
         </div>
      </div>
   );
}