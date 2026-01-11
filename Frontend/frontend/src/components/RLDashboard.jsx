import React, { useState, useEffect, useRef } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  PieChart, Pie, Cell
} from 'recharts';
import { Activity, Brain, ShieldAlert, Sliders, Shield } from 'lucide-react';

export default function RLDashboard({ socket, systemData, logs, epsilon }) {
  // --- STATE ---
  const [learningHistory, setLearningHistory] = useState([]);
  const [threatLevel, setThreatLevel] = useState(0);
  // epsilon is now a prop
  const [isPaused, setIsPaused] = useState(false);
  const [lastReward, setLastReward] = useState(0); // FIXED: Tracking instant reward separately

  const logsEndRef = useRef(null);

  // Auto-scroll logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  // Attack Vector Stats (Accumulative)
  const [attackStats, setAttackStats] = useState([
    { subject: 'SQL INJECTION', A: 20, fullMark: 100 },
    { subject: 'XSS ATTACK', A: 20, fullMark: 100 },
    { subject: 'PHISHING', A: 20, fullMark: 100 },
    { subject: 'BRUTE FORCE', A: 20, fullMark: 100 },
    { subject: 'FLOOD/DDOS', A: 20, fullMark: 100 },
  ]);

  // --- SOCKET LISTENERS ---
  useEffect(() => {
    if (!socket) return;

    const handleDashboardUpdate = (data) => {
      // console.log("[RLDashboard] Stream Data:", data);

      if (isPaused) return;

      // 1. Update Graph
      setLearningHistory(prev => [...prev, {
        time: data.timestamp,
        value: data.total_score,
      }].slice(-50));

      // 2. Update Gauge
      setThreatLevel(data.threat_level);

      // 3. Update Radar
      const type = data.attack_type ? data.attack_type.toUpperCase() : "UNKNOWN";
      setAttackStats(prev => prev.map(stat => {
        if (type.includes(stat.subject) || stat.subject.includes(type)) {
          return { ...stat, A: Math.min(stat.A + 5, 100) };
        }
        return stat;
      }));

      // 4. Update Epsilon (Handled via props now)
      // if (data.epsilon) setEpsilon...

      // 5. Update Last Reward (FIXED: Use exact reward from packet, or delta if not present)
      if (data.reward !== undefined) {
        setLastReward(data.reward);
      }
    };

    socket.on("dashboard_update", handleDashboardUpdate);
    return () => socket.off("dashboard_update");
  }, [socket, isPaused]);

  // --- VIZ DATA PREP ---
  const gaugeData = [
    { name: 'Threat', value: threatLevel },
    { name: 'Safe', value: 100 - threatLevel }
  ];
  const threatColor = threatLevel > 50 ? '#ef4444' : '#22c55e';

  // --- RENDER ---
  return (
    <div className="grid grid-cols-3 grid-rows-[350px_250px] gap-6 animate-in fade-in duration-500 h-full text-xs">

      {/* 1. CUMULATIVE REWARD (AREA CHART) - Pushed to span 2 cols */}
      <div className="panel p-6 flex flex-col relative col-span-2">
        <div className="flex items-center gap-2 mb-4 border-b border-[var(--border-base)] pb-2">
          <Activity className="w-4 h-4 text-brand" />
          <span className="text-sm font-bold tracking-[0.2em] text-muted uppercase">Cumulative Reward</span>
          <span className="text-[10px] text-dim font-bold tracking-widest uppercase ml-auto">(Live Performance)</span>
        </div>
        <div className="flex-1 min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={learningHistory}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-base)" vertical={false} />
              <XAxis dataKey="time" stroke="var(--text-tertiary)" fontSize={10} tick={false} axisLine={{ stroke: 'var(--border-base)' }} />
              <YAxis stroke="var(--text-tertiary)" fontSize={10} axisLine={{ stroke: 'var(--border-base)' }} tickLine={{ stroke: 'var(--border-base)' }} />
              <Tooltip
                contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-base)', color: 'var(--text-primary)' }}
                itemStyle={{ color: 'var(--brand-primary)' }}
              />
              <Area type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} fill="url(#colorValue)" isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. LOGS PANEL (NEW REQUEST) - Takes the 3rd column space on top row */}
      <div className="panel flex flex-col overflow-hidden col-span-1">
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-base)] bg-[var(--bg-subtle)]">
          <div className="flex items-center gap-2">
            <Shield size={14} className="text-muted" />
            <span className="text-[10px] font-bold tracking-[0.2em] text-muted uppercase">Live Events</span>
          </div>
        </div>
        <div className="flex-1 bg-black/50 p-4 overflow-y-auto custom-scrollbar font-mono text-[10px]">
          {logs && logs.length > 0 ? logs.map((log, i) => (
            <div key={i} className="flex gap-2 mb-2 border-b border-[var(--border-base)] pb-1 last:border-0">
              <span className="text-dim min-w-[50px]">{log.time.split(' ')[0]}</span>
              <span className={`font-bold ${log.status === "BLOCKED" ? "text-success" :
                log.status === "FLAGGED" ? "text-warning" : "text-danger"
                }`}>
                [{log.status}]
              </span>
              <span className="text-muted truncate">{log.message}</span>
            </div>
          )) : <div className="text-dim italic text-center mt-10">Stream Idle...</div>}
          <div ref={logsEndRef} />
        </div>
      </div>


      {/* 3. ATTACK VECTOR BIAS (RADAR CHART) */}
      <div className="panel p-6 flex flex-col relative col-span-1">
        <div className="flex items-center gap-2 mb-4 border-b border-[var(--border-base)] pb-2">
          <Brain className="w-4 h-4 text-purple-500" />
          <span className="text-sm font-bold tracking-[0.2em] text-muted uppercase">AI Focus Area</span>
        </div>
        <div className="flex-1 min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={attackStats}>
              <PolarGrid stroke="var(--border-base)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-secondary)', fontSize: 9, fontWeight: 'bold' }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar name="Frequency" dataKey="A" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.5} isAnimationActive={false} />
              <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-base)', color: 'var(--text-primary)' }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. THREAT GAUGE (PIE CHART) */}
      <div className="col-span-1 panel p-6 relative flex flex-col items-center justify-center">
        <div className="absolute top-4 left-4 flex items-center gap-2 border-b border-[var(--border-base)] pb-2 w-[90%]">
          <ShieldAlert className="w-4 h-4 text-danger" />
          <span className="text-sm font-bold tracking-[0.2em] text-muted uppercase">Threat Level</span>
        </div>
        <div className="w-full h-full relative mt-4">
          <ResponsiveContainer>
            <PieChart>
              <Pie data={gaugeData} cx="50%" cy="70%" startAngle={180} endAngle={0} innerRadius={60} outerRadius={80} dataKey="value" stroke="none" isAnimationActive={false}>
                <Cell fill={threatColor} />
                <Cell fill="var(--bg-subtle)" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-center">
            <div className="text-5xl font-bold tracking-tighter" style={{ color: threatColor }}>{threatLevel}%</div>
            <div className="text-[10px] text-muted tracking-[0.3em] uppercase mt-1">Defcon Status</div>
          </div>
        </div>
      </div>

      {/* 5. CONTROL PANEL (WITHOUT BUTTON) */}
      <div className="col-span-1 panel p-6 flex flex-col justify-center gap-6">
        <div className="flex items-center gap-2 border-b border-[var(--border-base)] pb-2">
          <Sliders className="w-4 h-4 text-success" />
          <h3 className="text-sm font-bold tracking-[0.2em] text-muted uppercase">RL Parameters</h3>
        </div>

        <div className="grid gap-4">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-[9px] text-muted font-bold uppercase tracking-[0.2em] mb-1">Epsilon (Exploration)</div>
              <div className={`text-lg font-mono tracking-tight font-bold ${epsilon >= 0.1 ? 'text-yellow-500' : 'text-blue-500'}`}>
                {typeof epsilon === 'number' ? epsilon.toFixed(3) : epsilon}
              </div>
            </div>
            <div>
              <div className="text-[9px] text-muted font-bold uppercase tracking-[0.2em] mb-1">Last Reward</div>
              {/* FIXED: Showing Instant Reward */}
              <div className={`text-lg font-mono font-bold ${lastReward >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {lastReward > 0 ? "+" : ""}{typeof lastReward === 'number' ? lastReward.toFixed(1) : lastReward}
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setIsPaused(!isPaused)}
              className={`flex-1 py-3 flex items-center justify-center gap-2 uppercase font-bold tracking-widest text-[10px] transition-all border rounded
                  ${isPaused
                  ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500 hover:bg-yellow-500/20'
                  : 'bg-green-500/10 text-green-500 border-green-500 hover:bg-green-500/20'
                }`}
            >
              {isPaused ? "RESUME STREAM" : "PAUSE STREAM"}
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}