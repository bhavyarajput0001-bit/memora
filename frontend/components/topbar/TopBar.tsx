"use client";

import { Bell, Search, RefreshCw, Plus } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";
import CalendarModal from "../calendar/CalendarModal";

export default function TopBar() {
  const [searchFocused, setSearchFocused] = useState(false);
  const [searchValue, setSearchValue] = useState("");
  const [showCalendar, setShowCalendar] = useState(false);

  return (
    <>
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#0a0f1e]/80 backdrop-blur-2xl flex-shrink-0 relative overflow-hidden">
        {/* Ambient glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 right-0 w-64 h-32 bg-cyan-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-1/3 w-48 h-24 bg-violet-500/5 rounded-full blur-2xl" />
        </div>

        <div className="flex items-center gap-4 flex-1 relative z-10">
          <motion.div 
            className="relative max-w-md w-full"
            initial={false}
            animate={{ scale: searchFocused ? 1.02 : 1 }}
          >
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="Search memories, sources, people... (⌘K)"
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
              className={`w-full pl-10 pr-12 py-2 bg-[#111827]/60 border rounded-xl text-sm text-slate-200 placeholder-slate-500 transition-all duration-300 ${
                searchFocused
                  ? "border-cyan-500/50 ring-2 ring-cyan-500/20 shadow-lg shadow-cyan-500/10"
                  : "border-white/5 hover:border-white/10"
              }`}
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 text-[10px] text-slate-500 bg-[#1e293b] rounded border border-white/10">⌘</kbd>
              <kbd className="px-1.5 py-0.5 text-[10px] text-slate-500 bg-[#1e293b] rounded border border-white/10">K</kbd>
            </div>
          </motion.div>
        </div>
        
        <div className="flex items-center gap-3 relative z-10">
          <motion.div 
            className="flex items-center gap-2 text-xs text-slate-500 px-3 py-1.5 rounded-lg bg-[#111827]/60 border border-white/5"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <RefreshCw size={12} className="text-cyan-500" />
            <span className="hidden sm:inline">Synced</span>
          </motion.div>
          
          {/* Plus Button for Calendar */}
          <motion.button 
            onClick={() => setShowCalendar(true)}
            className="relative p-2.5 rounded-xl bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/25 hover:border-cyan-500/30 transition-all duration-200 group"
            whileHover={{ scale: 1.1, boxShadow: "0 0 20px rgba(6, 182, 212, 0.3)" }}
            whileTap={{ scale: 0.9 }}
          >
            <Plus size={18} className="transition-transform group-hover:rotate-90" />
          </motion.button>
          
          <motion.button 
            className="relative p-2.5 rounded-xl hover:bg-[#111827] text-slate-400 hover:text-slate-200 transition-all duration-200 group"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <Bell size={18} />
            <span className="absolute top-2 right-2 w-2 h-2 bg-cyan-500 rounded-full shadow-lg shadow-cyan-500/50 pulse-glow" />
          </motion.button>
          
          <motion.div 
            className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-700 flex items-center justify-center text-white text-sm font-semibold shadow-lg shadow-cyan-500/20 glow-cyan cursor-pointer"
            whileHover={{ scale: 1.1, boxShadow: "0 0 30px rgba(6, 182, 212, 0.6)" }}
            whileTap={{ scale: 0.9 }}
          >
            B
          </motion.div>
        </div>
      </header>

      {/* Calendar Modal */}
      <CalendarModal isOpen={showCalendar} onClose={() => setShowCalendar(false)} />
    </>
  );
}