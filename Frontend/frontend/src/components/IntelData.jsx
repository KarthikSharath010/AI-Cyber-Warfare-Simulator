import React, { useState } from 'react';
import { Shield, Globe, AlertTriangle, BookOpen, Lock, Server, Users } from 'lucide-react';

// --- DATA: PROJECT SPECIFIC ATTACKS ---
const PROJECT_ATTACKS = [
    // --- CATEGORY 1: INJECTION ---
    {
        id: 'sqli',
        title: 'SQL Injection (SQLi)',
        category: 'Injection',
        desc: 'Attackers inject malicious SQL commands into input fields to trick the database into revealing hidden data.',
        impact: '2015 TalkTalk Breach (£400k+ damages, 150k customers exposed).',
        defense: 'OWASP WAF Engine: Uses Regex signatures to detect SQL patterns. RL Agent bans IP on repeat offense.'
    },
    {
        id: 'xss',
        title: 'Cross-Site Scripting (XSS)',
        category: 'Injection',
        desc: 'Injecting malicious scripts into webpages to hijack user sessions or steal cookies.',
        impact: 'British Airways (2018): 380k transactions hijacked via Magecart script injection.',
        defense: 'Input Sanitization: WAF detects <script> tags and blocks request before backend processing.'
    },
    {
        id: 'cmd_inj',
        title: 'OS Command Injection',
        category: 'Injection',
        desc: 'Executing operating system commands on the server via vulnerable inputs.',
        impact: 'Equifax Breach (2017): 147 million people exposed due to Apache Struts vulnerability.',
        defense: 'Strict Allow-listing: Blocks system operators (;, |, &&) and triggers High-Threat Alert.'
    },

    // --- CATEGORY 2: NETWORK ---
    {
        id: 'ddos',
        title: 'DDoS (SYN Flood)',
        category: 'Network',
        desc: 'Exhausting server memory by sending thousands of incomplete connection requests.',
        impact: 'GitHub (2018): 1.35 Tbps attack took the platform offline.',
        defense: 'Adaptive Rate Limiting: PPO Agent dynamically creates IPTables rules to drop traffic >50 req/sec.'
    },
    {
        id: 'udp_flood',
        title: 'UDP / QUIC Flood',
        category: 'Network',
        desc: 'Flooding random ports with garbage packets to saturate bandwidth.',
        impact: 'Common tactic used to disrupt gaming servers and VoIP services.',
        defense: 'Anomaly Detection: Network Monitor (Scapy) identifies bandwidth spikes on non-standard ports.'
    },

    // --- CATEGORY 3: ACCESS CONTROL ---
    {
        id: 'ssh',
        title: 'SSH Brute Force',
        category: 'Access',
        desc: 'Automated bots guessing millions of password combinations to gain root access.',
        impact: 'Mirai Botnet: Compromised thousands of IoT devices using default credentials.',
        defense: 'Behavioral Analysis: IP "Jailed" for 10 minutes after 5 failed login attempts.'
    },
    {
        id: 'path_trav',
        title: 'Directory Traversal',
        category: 'Access',
        desc: 'Manipulating file paths (../) to access restricted server files.',
        impact: 'Often used to steal /etc/passwd or config files.',
        defense: 'Pattern Matching: WAF blocks path manipulation sequences (../, ..%2f).'
    },

    // --- CATEGORY 4: SOPHISTICATED ---
    {
        id: 'phishing',
        title: 'AI-Generated Phishing',
        category: 'Social Eng',
        desc: 'Using LLMs to generate convincing, urgent emails requesting credentials.',
        impact: 'Business Email Compromise (BEC) costs companies billions annually.',
        defense: 'DarkBERT-Lite: NLP model analyzes sentiment and urgency. High urgency + links = Blocked.'
    },
    {
        id: 'spoofing',
        title: 'User-Agent Spoofing',
        category: 'Evasion',
        desc: 'Scripts pretending to be legitimate browsers (Chrome/Firefox) to bypass filters.',
        impact: 'Used by scrapers and scalper bots to blend in with normal traffic.',
        defense: 'Header Analysis: AI compares request frequency with declared browser behavior.'
    },
    {
        id: 'c2',
        title: 'C2 Beaconing',
        category: 'Malware',
        desc: 'Malware checking in with a hacker\'s server for instructions.',
        impact: 'SolarWinds Hack: Malware lay dormant and beaconed out silently.',
        defense: 'Traffic Pattern Analysis: RL Agent identifies and severs rhythmic, periodic outbound connections.'
    }
];

// --- DATA: OWASP TOP 10 (New) ---
const OWASP_DATA = [
    { id: 'A01', title: 'Broken Access Control', desc: 'Users acting outside of their intended permissions.' },
    { id: 'A02', title: 'Cryptographic Failures', desc: 'Failures related to cryptography which often lead to sensitive data exposure.' },
    { id: 'A03', title: 'Injection', desc: 'SQL, NoSQL, OS, and LDAP injection flaws (This project simulates this heavily).' },
    { id: 'A04', title: 'Insecure Design', desc: 'Risks related to design flaws and lack of threat modeling.' },
    { id: 'A05', title: 'Security Misconfiguration', desc: 'Missing security hardening across the application stack.' },
    { id: 'A06', title: 'Vulnerable Components', desc: 'Using libraries and frameworks with known vulnerabilities.' },
    { id: 'A07', title: 'Identification Failures', desc: 'Failures in authentication and session management.' },
    { id: 'A08', title: 'Software & Data Integrity', desc: 'Code and infrastructure that does not protect against integrity violations.' },
    { id: 'A09', title: 'Logging Failures', desc: 'Insufficient logging and monitoring allowing attackers to hide.' },
    { id: 'A10', title: 'SSRF', desc: 'Server-Side Request Forgery flaws.' },
];

// --- DATA: GENERAL CONCEPTS (New) ---
const FUNDAMENTALS = [
    {
        title: 'The CIA Triad',
        icon: <Shield size={24} className="text-[#3b82f6]" />,
        content: 'The core model of information security: Confidentiality (Privacy), Integrity (Data accuracy), and Availability (Uptime). Our DDoS attacks target Availability, while SQLi targets Confidentiality.'
    },
    {
        title: 'Red Team vs. Blue Team',
        icon: <Users size={24} className="text-[#ef4444]" />,
        content: 'A military simulation concept. Red Team (Offensive) simulates real-world attacks to test defenses. Blue Team (Defensive) protects the infrastructure and responds to incidents. Our project automates both.'
    },
    {
        title: 'Zero Trust Architecture',
        icon: <Lock size={24} className="text-[#10b981]" />,
        content: 'A security framework requiring all users, whether in or outside the organization’s network, to be authenticated, authorized, and continuously validated. "Never trust, always verify."'
    }
];

const IntelData = () => {
    const [activeTab, setActiveTab] = useState('simulation');

    return (
        <div className="h-full flex flex-col p-6 text-white overflow-hidden">

            {/* HEADER */}
            <div className="mb-6 border-b border-[#2d3646] pb-4 flex-shrink-0">
                <h1 className="text-2xl font-bold flex items-center gap-2 mb-1">
                    <BookOpen className="text-[#3b82f6]" /> Intelligence Knowledge Base
                </h1>
                <p className="text-[#94a3b8] text-sm">Encyclopedia of active threats, industry standards, and core concepts.</p>
            </div>

            {/* TABS */}
            <div className="flex gap-4 mb-6 flex-shrink-0">
                {[
                    { id: 'simulation', label: 'Active Simulation Profile', icon: <AlertTriangle size={18} /> },
                    { id: 'owasp', label: 'OWASP Top 10 Standards', icon: <Globe size={18} /> },
                    { id: 'general', label: 'Cyber Fundamentals', icon: <Shield size={18} /> },
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`
              flex items-center gap-2 px-6 py-3 rounded-lg border font-medium transition-all
              ${activeTab === tab.id
                                ? 'bg-[#3b82f6] text-white border-[#3b82f6]'
                                : 'bg-[#1a1f2b] text-[#94a3b8] border-[#2d3646] hover:text-white hover:border-[#3b82f6]'
                            }
            `}
                    >
                        {tab.icon} {tab.label}
                    </button>
                ))}
            </div>

            {/* CONTENT AREA */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">

                {/* TAB 1: SIMULATION ATTACKS */}
                {activeTab === 'simulation' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                        {PROJECT_ATTACKS.map((item, idx) => (
                            <div key={idx} className="bg-[#1a1f2b] p-5 rounded-xl border border-[#2d3646] hover:border-[#3b82f6] transition-colors">
                                <div className="text-xs text-[#8b5cf6] font-bold uppercase tracking-widest mb-2">{item.category}</div>
                                <h3 className="text-lg font-bold mb-2">{item.title}</h3>
                                <p className="text-[#94a3b8] text-sm mb-4 leading-relaxed">{item.desc}</p>
                                <div className="bg-[#242a38] p-3 rounded-lg text-xs border border-[#2d3646]">
                                    <strong className="text-[#ef4444] uppercase tracking-wide">Real World:</strong> <span className="text-[#cbd5e1]">{item.impact}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* TAB 2: OWASP TOP 10 */}
                {activeTab === 'owasp' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                        {OWASP_DATA.map((item, idx) => (
                            <div key={idx} className="flex gap-4 bg-[#1a1f2b] p-6 rounded-xl border border-[#2d3646]">
                                <div className="text-3xl font-bold text-[#3b82f6] min-w-[60px]">{item.id}</div>
                                <div>
                                    <h3 className="text-lg font-bold mb-2">{item.title}</h3>
                                    <p className="text-[#94a3b8] text-sm leading-relaxed">{item.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* TAB 3: FUNDAMENTALS */}
                {activeTab === 'general' && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full content-center">
                        {FUNDAMENTALS.map((item, idx) => (
                            <div key={idx} className="bg-[#1a1f2b] p-8 rounded-xl border border-[#2d3646] flex flex-col items-center text-center hover:border-[#3b82f6] transition-all">
                                <div className="mb-4 p-4 bg-[#0f1218] rounded-full border border-[#2d3646]">{item.icon}</div>
                                <h3 className="text-xl font-bold mb-4">{item.title}</h3>
                                <p className="text-[#94a3b8] text-sm leading-7">{item.content}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>

        </div>
    );
};

export default IntelData;
