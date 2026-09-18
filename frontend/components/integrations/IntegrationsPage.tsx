"use client";

import { useState } from "react";
import { 
  Calendar as CalendarIcon, 
  Apple, 
  Chrome, 
  GitBranch, 
  CheckCircle, 
  Plus,
  Settings,
  Key,
  RefreshCw,
  Wifi,
  WifiOff,
  ArrowRight,
} from "lucide-react";
import { motion } from "framer-motion";

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  connected: boolean;
  color: string;
}

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: "google-calendar",
      name: "Google Calendar",
      description: "Sync your Google Calendar events and tasks",
      icon: <CalendarIcon size={20} className="text-blue-500" />,
      connected: false,
      color: "blue",
    },
    {
      id: "apple-calendar",
      name: "Apple Calendar",
      description: "Connect your iOS/macOS calendar events",
      icon: <Apple size={20} className="text-slate-300" />,
      connected: false,
      color: "slate",
    },
    {
      id: "google-notes",
      name: "Google Keep",
      description: "Import notes and reminders from Google Keep",
      icon: <Chrome size={20} className="text-yellow-500" />,
      connected: false,
      color: "yellow",
    },
    {
      id: "gmail",
      name: "Gmail",
      description: "Index your email for context-aware memory",
      icon: <Chrome size={20} className="text-red-500" />,
      connected: false,
      color: "red",
    },
    {
      id: "slack",
      name: "Slack",
      description: "Connect Slack channels and DMs",
      icon: <GitBranch size={20} className="text-purple-500" />,
      connected: false,
      color: "purple",
    },
    {
      id: "notion",
      name: "Notion",
      description: "Sync your Notion workspace pages",
      icon: <Settings size={20} className="text-white" />,
      connected: false,
      color: "white",
    },
    {
      id: "github",
      name: "GitHub",
      description: "Connect repositories and issues",
      icon: <GitBranch size={20} className="text-slate-200" />,
      connected: false,
      color: "slate",
    },
    {
      id: "mcp",
      name: "MCP Connectors",
      description: "Connect to any Model Context Protocol server",
      icon: <Wifi size={20} className="text-cyan-400" />,
      connected: false,
      color: "cyan",
    },
  ]);

  const connectIntegration = async (id: string) => {
    // Simulate connection
    setIntegrations(integrations.map(int => 
      int.id === id ? { ...int, connected: true } : int
    ));
  };

  const disconnectIntegration = (id: string) => {
    setIntegrations(integrations.map(int => 
      int.id === id ? { ...int, connected: false } : int
    ));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Integrations</h1>
        <p className="text-slate-400">Connect your tools to build a comprehensive memory system</p>
      </div>

      {/* Connection Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <Wifi size={18} className="text-emerald-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-white">
                {integrations.filter(i => i.connected).length}
              </div>
              <div className="text-xs text-slate-500">Connected</div>
            </div>
          </div>
        </div>
        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
              <RefreshCw size={18} className="text-cyan-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-white">Auto</div>
              <div className="text-xs text-slate-500">Sync Mode</div>
            </div>
          </div>
        </div>
        <div className="glass-card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
              <Key size={18} className="text-violet-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-white">Secure</div>
              <div className="text-xs text-slate-500">Encrypted</div>
            </div>
          </div>
        </div>
      </div>

      {/* Integrations Grid */}
      <div>
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">Available Integrations</h2>
        <div className="grid grid-cols-2 gap-4">
          {integrations.map((integration, index) => (
            <motion.div
              key={integration.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`glass-card p-5 transition-all duration-200 hover:border-white/20 ${
                integration.connected ? "border-emerald-500/30" : ""
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    integration.connected ? "bg-emerald-500/10 border border-emerald-500/20" : "bg-white/5 border border-white/10"
                  }`}>
                    {integration.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">{integration.name}</h3>
                    <p className="text-xs text-slate-500 mt-0.5">{integration.description}</p>
                  </div>
                </div>
                {integration.connected && (
                  <CheckCircle size={18} className="text-emerald-400 flex-shrink-0" />
                )}
              </div>
              
              <div className="flex items-center gap-2">
                {integration.connected ? (
                  <button
                    onClick={() => disconnectIntegration(integration.id)}
                    className="flex-1 px-3 py-2 bg-white/5 border border-white/10 text-slate-400 rounded-lg text-sm hover:bg-white/10 hover:text-slate-200 transition-all flex items-center justify-center gap-2"
                  >
                    <WifiOff size={14} /> Disconnect
                  </button>
                ) : (
                  <button
                    onClick={() => connectIntegration(integration.id)}
                    className="flex-1 px-3 py-2 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-lg text-sm hover:bg-cyan-500/25 transition-all flex items-center justify-center gap-2"
                  >
                    Connect <ArrowRight size={14} />
                  </button>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* MCP Configuration */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <Wifi size={18} className="text-cyan-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white">MCP Server Configuration</h3>
            <p className="text-xs text-slate-500">Connect custom Model Context Protocol servers</p>
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-slate-500 mb-2">Server URL</label>
            <input
              type="text"
              placeholder="http://localhost:3000"
              className="w-full px-4 py-2.5 bg-[#0a0f1e]/60 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-cyan-500/50 transition-colors"
            />
          </div>
          
          <div className="flex items-center gap-3">
            <button className="px-4 py-2.5 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-all">
              Test Connection
            </button>
            <button className="px-4 py-2.5 bg-white/5 border border-white/10 text-slate-400 rounded-xl text-sm hover:bg-white/10 hover:text-slate-200 transition-all">
              Save Configuration
            </button>
          </div>
        </div>
      </div>

      {/* Sync Status */}
      <div className="glass-card p-6">
        <h3 className="font-semibold text-white mb-4">Sync Status</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-white/5">
            <span className="text-sm text-slate-400">Last sync</span>
            <span className="text-sm text-slate-500">Never</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-white/5">
            <span className="text-sm text-slate-400">Sync interval</span>
            <span className="text-sm text-slate-300">Every 5 minutes</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm text-slate-400">Status</span>
            <span className="flex items-center gap-2 text-sm text-slate-500">
              <WifiOff size={14} /> No connections
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}