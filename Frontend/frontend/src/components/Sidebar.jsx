import React, { useState, useEffect } from "react";
import { LayoutGrid, Disc, ShieldAlert, Terminal, Sun, Moon, ChevronLeft, ChevronRight, Shield } from "lucide-react";

export default function Sidebar({ view, setView }) {
  const [time, setTime] = useState(new Date());

  // 1. Theme State (Default to dark)
  const [theme, setTheme] = useState('dark');

  // 2. Collapse State
  const [isCollapsed, setIsCollapsed] = useState(false);

  // 3. Timer Logic
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // 4. Theme Toggle Logic
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    // This updates the HTML tag to trigger the CSS [data-theme="light"] overrides
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  // Initialize theme on load
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, []);

  const timeString = time.toLocaleTimeString('en-US', { hour12: false });

  const menuItems = [
    { id: "OVERVIEW", label: "Dashboard", icon: LayoutGrid },
    { id: "WAR_ROOM", label: "War Room", icon: Disc },
    { id: "RL_LAB", label: "RL Learning Lab", icon: ShieldAlert },
    { id: "INTEL", label: "Intel Data", icon: Terminal },
  ];

  return (
    <aside
      className={`
        h-full sidebar-container flex flex-col flex-shrink-0 z-20 transition-all duration-300
        ${isCollapsed ? "w-20" : "w-72"}
      `}
    >

      {/* BRAND */}
      <div className={`h-20 flex items-center mb-4 transition-all duration-300 ${isCollapsed ? "justify-center px-0" : "px-6 justify-between"}`}>
        <div className="flex items-center gap-3 overflow-hidden">
          {/* Grey-White Shield Logo */}
          <Shield className="w-8 h-8 text-gray-300 flex-shrink-0" strokeWidth={1.5} />
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-white tracking-widest text-sm whitespace-nowrap uppercase">
                Cyber Command
              </span>
              <span className="text-[9px] text-gray-400 tracking-wide uppercase leading-tight">
                Autonomous Edge Warfare System
              </span>
            </div>
          )}
        </div>

        {/* Collapse Toggle Button */}
        {!isCollapsed && (
          <button
            onClick={() => setIsCollapsed(true)}
            className="text-muted hover:text-main p-1 rounded hover:bg-[var(--bg-subtle)] transition-colors"
          >
            <ChevronLeft size={16} />
          </button>
        )}
      </div>

      {/* Collapsed Expand Button (Centered if collapsed) */}
      {isCollapsed && (
        <div className="flex justify-center mb-6">
          <button
            onClick={() => setIsCollapsed(false)}
            className="text-muted hover:text-main p-1.5 rounded hover:bg-[var(--bg-subtle)] transition-colors"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}

      {/* MENU */}
      <div className="flex-1 px-4 flex flex-col gap-1">
        {!isCollapsed && (
          <div className="text-dim text-[10px] font-bold tracking-widest mb-4 px-2 uppercase transition-opacity duration-300">
            Platform
          </div>
        )}

        {menuItems.map((item) => {
          const isActive = view === item.id;
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              onClick={() => setView(item.id)}
              className={`
                relative flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-md transition-all duration-200 
                ${isCollapsed ? "justify-center" : "w-full text-left"}
                ${isActive
                  ? "sidebar-item-active"
                  : "text-muted hover:text-main hover:bg-[var(--bg-subtle)]"
                }
              `}
              title={isCollapsed ? item.label : ""}
            >
              <Icon size={18} className={`${isActive ? "text-main" : "text-dim"}`} />
              {!isCollapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </div>

      {/* BOTTOM ACTIONS (Time Only) */}
      <div className={`p-4 border-t border-[var(--border-base)] flex flex-col gap-4 ${isCollapsed ? "items-center" : ""}`}>

        {/* SESSION TIME */}
        {!isCollapsed && (
          <div className="flex flex-col items-center">
            <span className="text-dim text-[10px] uppercase tracking-widest mb-1">Session Time</span>
            <span className="text-main font-mono text-sm tracking-widest">{timeString}</span>
          </div>
        )}
      </div>
    </aside>
  );
}