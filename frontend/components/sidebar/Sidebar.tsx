"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  MessageSquare,
  Database,
  Calendar,
  AlertTriangle,
  FileText,
  GitGraph,
  CheckCircle,
  Settings,
  User,
  ChevronLeft,
  Sparkles,
  CalendarDays,
  Plug,
  Plus,
} from "lucide-react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/ask", label: "Ask", icon: MessageSquare },
  { href: "/memory", label: "Memory", icon: Database },
  { href: "/timeline", label: "Timeline", icon: Calendar },
  { href: "/conflicts", label: "Conflicts", icon: AlertTriangle },
  { href: "/sources", label: "Sources", icon: FileText },
  { href: "/graph", label: "Graph", icon: GitGraph },
  { href: "/actions", label: "Actions", icon: CheckCircle },
];

const quickTasks = [
  { id: "1", title: "Upload PDF", time: "Now", due: "today" },
  { id: "2", title: "Connect Google Calendar", time: "5 min", due: "today" },
  { id: "3", title: "Add screenshot", time: "Later", due: "week" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [showTasks, setShowTasks] = useState(false);
  const [tasks, setTasks] = useState(quickTasks);
  const [newTask, setNewTask] = useState("");

  useEffect(() => {
    setMounted(true);
  }, []);

  const addTask = () => {
    if (!newTask.trim()) return;
    const task = {
      id: Date.now().toString(),
      title: newTask,
      time: "Just now",
      due: "today",
    };
    setTasks([task, ...tasks]);
    setNewTask("");
  };

  const completeTask = (id: string) => {
    setTasks(tasks.filter(t => t.id !== id));
  };

  if (!mounted) return null;

  return (
    <aside
      className="flex flex-col bg-[#0a0f1e]/95 backdrop-blur-2xl border-r border-white/5 transition-all duration-300 ease-in-out relative"
      style={{ width: collapsed ? "4rem" : "16rem" }}
    >
      {/* Ambient Glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-24 h-24 bg-violet-500/5 rounded-full blur-2xl" />
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-[#111827] border border-white/10 flex items-center justify-center text-slate-400 hover:text-cyan-400 transition-all z-10 hover:shadow-lg hover:shadow-cyan-500/20"
      >
        <ChevronLeft size={12} className={collapsed ? "" : "rotate-180"} />
      </button>

      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-white/5 relative">
        <div className="flex items-center gap-3">
          <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 via-cyan-500 to-cyan-700 flex items-center justify-center flex-shrink-0 shadow-lg shadow-cyan-500/30 glow-cyan">
            <Sparkles size={18} className="text-white" />
            <div className="absolute inset-0 rounded-xl bg-gradient-to-t from-transparent to-white/20" />
            <div className="absolute inset-0 rounded-xl bg-cyan-400/20 animate-pulse" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <h1 className="text-white font-bold text-sm tracking-[0.2em] uppercase">MEMORA</h1>
              <p className="text-slate-500 text-[10px] tracking-wider">Connected Memory</p>
            </div>
          )}
        </div>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group flex items-center gap-3 px-3 py-3 rounded-xl text-sm transition-all duration-200 relative overflow-hidden ${
                isActive
                  ? "bg-cyan-500/15 text-cyan-400 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              }`}
            >
              {isActive && <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-transparent" />}
              <Icon
                size={18}
                className={`transition-all duration-200 flex-shrink-0 relative z-10 ${
                  isActive
                    ? "text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]"
                    : "text-slate-500 group-hover:text-slate-300"
                }`}
              />
              {!collapsed && (
                <span className={`font-medium truncate relative z-10 ${isActive ? "text-cyan-400" : ""}`}>
                  {item.label}
                </span>
              )}
              {isActive && !collapsed && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-lg shadow-cyan-500/50 animate-pulse relative z-10" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Quick Tasks Section */}
      {!collapsed && (
        <div className="px-2 mb-2">
          <button
            onClick={() => setShowTasks(!showTasks)}
            className="flex items-center gap-2 px-3 py-2 w-full rounded-xl text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-all"
          >
            <CalendarDays size={16} />
            <span className="flex-1 text-left">Quick Tasks</span>
            <span className="text-xs bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full">{tasks.length}</span>
            <ChevronLeft size={14} className={`transition-transform ${showTasks ? "rotate-90" : ""}`} />
          </button>
          
          <AnimatePresence>
            {showTasks && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="px-3 py-2 space-y-1">
                  {tasks.map((task) => (
                    <div key={task.id} className="flex items-center gap-2 py-1.5 group">
                      <button
                        onClick={() => completeTask(task.id)}
                        className="w-4 h-4 rounded border border-slate-600 hover:border-cyan-500 hover:bg-cyan-500/10 transition-all flex items-center justify-center"
                      >
                        <CheckCircle size={10} className="text-cyan-400 opacity-0 group-hover:opacity-100" />
                      </button>
                      <span className="flex-1 text-xs text-slate-400 group-hover:text-slate-200">{task.title}</span>
                      <span className="text-[10px] text-slate-600">{task.time}</span>
                    </div>
                  ))}
                  <div className="flex items-center gap-2 mt-2">
                    <input
                      type="text"
                      value={newTask}
                      onChange={(e) => setNewTask(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && addTask()}
                      placeholder="Add task..."
                      className="flex-1 bg-transparent text-xs text-slate-300 placeholder-slate-600 outline-none"
                    />
                    <button
                      onClick={addTask}
                      className="text-slate-500 hover:text-cyan-400 transition-colors"
                    >
                      <Plus size={14} />
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Bottom Section */}
      <div className="py-4 px-2 border-t border-white/5 space-y-1">
        <Link
          href="/integrations"
          className="flex items-center gap-3 px-3 py-3 rounded-xl text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 w-full transition-all duration-200"
        >
          <Plug size={18} className="text-slate-500 flex-shrink-0" />
          {!collapsed && <span>Integrations</span>}
        </Link>
        <button className="flex items-center gap-3 px-3 py-3 rounded-xl text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 w-full transition-all duration-200">
          <Settings size={18} className="text-slate-500 flex-shrink-0" />
          {!collapsed && <span>Settings</span>}
        </button>
        <button className="flex items-center gap-3 px-3 py-3 rounded-xl text-sm text-slate-400 hover:text-slate-200 hover:bg-white/5 w-full transition-all duration-200">
          <User size={18} className="text-slate-500 flex-shrink-0" />
          {!collapsed && <span className="font-medium">bhavyarajput</span>}
        </button>
      </div>
    </aside>
  );
}