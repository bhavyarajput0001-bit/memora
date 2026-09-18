"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Send,
  FileText,
  Image as ImageIcon,
  Mail,
  Calendar,
  Clock,
  AlertTriangle,
  Users,
  TrendingUp,
  Database,
  ArrowRight,
  Sparkles,
  Plus,
  CheckCircle,
  RefreshCw,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import DetailModal from "./DetailModal";
import UploadModal from "./UploadModal";

// Animated counter component
function AnimatedNumber({ value, duration = 0.5 }: { value: number; duration?: number }) {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let start = 0;
    const end = parseInt(String(value), 10) || 0;
    if (start === end) return;
    
    let totalDuration = duration * 1000;
    let startTime: number;
    
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / totalDuration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(easeOut * end));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [value, duration]);
  
  return <span>{count}</span>;
}

type Category = "facts" | "people" | "events" | "relationships" | "sources";
type UploadType = "pdf" | "screenshot" | "email" | "calendar" | "notes";

export default function Dashboard() {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [stats, setStats] = useState({
    facts: 0,
    entities: 0,
    events: 0,
    relationships: 0,
    sources: 0,
  });
  const [recentActivities, setRecentActivities] = useState<any[]>([]);
  const [upcomingEvents, setUpcomingEvents] = useState<any[]>([]);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastSynced, setLastSynced] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [uploadType, setUploadType] = useState<UploadType | null>(null);

  // Load real data from backend
  useEffect(() => {
    loadDashboardData();
  }, []);

  const refreshData = () => {
    loadDashboardData();
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load stats
      const statsResponse = await api.getMemoryStats();
      if (statsResponse.success) {
        setStats({
          facts: statsResponse.data.total_facts || 0,
          entities: statsResponse.data.total_entities || 0,
          events: statsResponse.data.recent_facts?.length || 0,
          relationships: 0,
          sources: statsResponse.data.total_documents || 0,
        });
      }

      // Load recent activities
      const activitiesResponse = await api.getTimeline(7);
      if (activitiesResponse.success) {
        setRecentActivities(activitiesResponse.data.events?.slice(0, 5) || []);
        setLastSynced(new Date().toLocaleTimeString());
      }

      // Load upcoming events
      const eventsResponse = await api.getTimeline(30);
      if (eventsResponse.success) {
        setUpcomingEvents(eventsResponse.data.events?.filter((e: any) => new Date(e.date) > new Date()).slice(0, 3) || []);
      }

      // Load conflicts
      const conflictsResponse = await api.getConflicts();
      if (conflictsResponse.success) {
        setConflicts(conflictsResponse.data.conflicts?.slice(0, 3) || []);
      }
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24,
      }
    }
  };

  const handleCategoryClick = (category: Category) => {
    setSelectedCategory(category);
  };

  const categoryCards = [
    { label: "Facts", value: stats.facts, icon: Database, color: "cyan", category: "facts" as Category },
    { label: "People", value: stats.entities, icon: Users, color: "emerald", category: "people" as Category },
    { label: "Events", value: stats.events, icon: Calendar, color: "amber", category: "events" as Category },
    { label: "Relationships", value: stats.relationships, icon: TrendingUp, color: "violet", category: "relationships" as Category },
    { label: "Sources", value: stats.sources, icon: FileText, color: "slate", category: "sources" as Category },
  ];

  return (
    <motion.div 
      className="max-w-6xl mx-auto space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <motion.h1 
          className="text-4xl font-bold text-white mb-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 24 }}
        >
          Good evening.
        </motion.h1>
        <motion.p 
          className="text-slate-400 text-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          Your memory, connected.
        </motion.p>
      </motion.div>

      {/* Ask Bar */}
      <motion.div variants={itemVariants} className="relative">
        <motion.div
          className={`flex items-center gap-4 px-6 py-5 rounded-2xl border transition-all duration-300 ${
            isFocused
              ? "border-cyan-500/50 bg-[#111827]/80 shadow-xl shadow-cyan-500/10"
              : "border-white/10 bg-[#111827]/60 hover:border-white/20"
          }`}
          whileFocus={{ scale: 1.01 }}
        >
          <Send size={22} className="text-cyan-400 flex-shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="What do you need to remember? Ask about a person, project, deadline..."
            className="flex-1 bg-transparent text-slate-200 placeholder-slate-500 text-base outline-none"
          />
          <button className="btn-press px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 text-white rounded-xl text-sm font-semibold transition-all duration-200 shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50">
            Ask
          </button>
        </motion.div>
        <div className="flex items-center gap-3 mt-4 text-xs text-slate-500">
          {[
            { type: "pdf" as UploadType, label: "PDF", icon: FileText },
            { type: "screenshot" as UploadType, label: "Screenshot", icon: ImageIcon },
            { type: "email" as UploadType, label: "Email", icon: Mail },
            { type: "calendar" as UploadType, label: "Calendar", icon: Calendar },
            { type: "notes" as UploadType, label: "Notes", icon: Clock },
          ].map(({ type, label, icon: Icon }) => (
            <motion.span
              key={type}
              onClick={() => setUploadType(type)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#111827]/60 border border-white/5 hover:border-white/10 transition-colors cursor-pointer"
              whileHover={{ scale: 1.05, borderColor: "rgba(6, 182, 212, 0.3)" }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon size={12} />
              {label}
            </motion.span>
          ))}
        </div>
      </motion.div>

      {/* Memory Overview */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Memory Overview
          </h2>
          <Link href="/memory" className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 group">
            View all 
            <ArrowRight size={12} className="transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
        <div className="grid grid-cols-5 gap-4">
          {categoryCards.map((stat, i) => {
            const Icon = stat.icon;
            const colorClasses = {
              cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
              emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
              amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
              violet: "text-violet-400 bg-violet-500/10 border-violet-500/20",
              slate: "text-slate-400 bg-slate-500/10 border-slate-500/20",
            };
            return (
              <motion.div
                key={stat.label}
                className="glass-card p-4 flex items-center gap-3 cursor-pointer group interactive-card"
                whileHover={{ y: -4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleCategoryClick(stat.category)}
              >
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center border transition-all duration-200 group-hover:scale-110 ${colorClasses[stat.color as keyof typeof colorClasses]}`}>
                  <Icon size={20} />
                </div>
                <div>
                  <div className="text-2xl font-bold text-white">
                    {loading ? (
                      <span className="inline-block w-8 h-8 skeleton" />
                    ) : (
                      <AnimatedNumber value={stat.value} />
                    )}
                  </div>
                  <div className="text-xs text-slate-500">{stat.label}</div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Upcoming */}
        <motion.div variants={itemVariants} className="glass-card p-5 interactive-card">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-semibold text-white">Upcoming</h3>
            <Link href="/timeline" className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {upcomingEvents.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <Calendar size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">No upcoming events</p>
                <p className="text-xs mt-1">Add events from your calendar</p>
              </div>
            ) : (
              upcomingEvents.map((item, i) => (
                <motion.div
                  key={i}
                  className="flex items-center justify-between py-3 border-b border-white/5 last:border-0 cursor-pointer hover:bg-white/5 rounded-lg px-2 -mx-2 transition-colors"
                  whileHover={{ x: 4 }}
                >
                  <div>
                    <div className="text-sm text-slate-200 font-medium">{item.title || item.description}</div>
                    <div className="text-xs text-slate-500">{new Date(item.date).toLocaleDateString()}</div>
                  </div>
                  {item.daysUntil && (
                    <span className="text-xs px-2.5 py-1 bg-cyan-500/10 text-cyan-400 rounded-lg font-medium border border-cyan-500/20">
                      {item.daysUntil}d
                    </span>
                  )}
                </motion.div>
              ))
            )}
          </div>
        </motion.div>

        {/* Conflicts */}
        <motion.div variants={itemVariants} className="glass-card p-5 interactive-card">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <AlertTriangle size={16} className="text-amber-500" />
              Conflicts
            </h3>
            <Link href="/conflicts" className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
              Review
            </Link>
          </div>
          <div className="space-y-4">
            {conflicts.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <CheckCircle size={32} className="mx-auto mb-2 opacity-50 text-emerald-500" />
                <p className="text-sm">No conflicts detected</p>
                <p className="text-xs mt-1">Your memories are consistent</p>
              </div>
            ) : (
              conflicts.map((conflict, i) => (
                <motion.div 
                  key={i} 
                  className="text-sm cursor-pointer hover:bg-white/5 rounded-lg p-3 -mx-3 transition-colors"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="text-slate-300 mb-3 font-medium">
                    {conflict.subject} → {conflict.predicate}
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="px-2.5 py-1.5 bg-rose-500/10 text-rose-400 rounded-lg font-medium border border-rose-500/20">
                      {conflict.value_a}
                    </span>
                    <span className="text-slate-500">vs</span>
                    <span className="px-2.5 py-1.5 bg-emerald-500/10 text-emerald-400 rounded-lg font-medium border border-emerald-500/20">
                      {conflict.value_b}
                    </span>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div variants={itemVariants} className="glass-card p-5 interactive-card">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-semibold text-white">Recent Activity</h3>
            <button 
              onClick={loadDashboardData}
              className="p-1.5 hover:bg-white/10 rounded-lg transition-all"
            >
              <RefreshCw size={14} className="text-slate-500 hover:text-cyan-400 transition-colors" />
            </button>
          </div>
          <div className="space-y-0">
            {recentActivities.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <Sparkles size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">No activity yet</p>
                <p className="text-xs mt-1">Start by adding your first source</p>
              </div>
            ) : (
              recentActivities.map((item, i) => (
                <motion.div 
                  key={i} 
                  className="py-3 border-b border-white/5 last:border-0 cursor-pointer hover:bg-white/5 rounded-lg px-2 -mx-2 transition-colors"
                  whileHover={{ x: 4 }}
                >
                  <div className="text-sm text-slate-200 font-medium">{item.description || item.event}</div>
                  <div className="text-xs text-slate-500 mt-1">{item.time || new Date().toLocaleString()}</div>
                </motion.div>
              ))
            )}
          </div>
        </motion.div>

        {/* Memory Activity Timeline */}
        <motion.div variants={itemVariants} className="col-span-3 glass-card p-6 interactive-card">
          <h3 className="font-semibold text-white mb-5">Memory Activity</h3>
          {recentActivities.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Database size={48} className="mx-auto mb-4 opacity-30" />
              <p className="text-base">Your memory is empty</p>
              <p className="text-sm mt-2">Upload PDFs, screenshots, or connect your calendar to start building your memory</p>
              <button className="btn-press mt-6 px-6 py-3 bg-cyan-500/15 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-colors border border-cyan-500/20 flex items-center gap-2 mx-auto">
                <Plus size={16} /> Add Your First Source
              </button>
            </div>
          ) : (
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-px bg-white/10"></div>
              <div className="space-y-5">
                {recentActivities.map((activity, i) => (
                  <motion.div 
                    key={i} 
                    className="flex items-start gap-4"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <div className="w-2 h-2 rounded-full mt-2 flex-shrink-0 relative z-10 bg-cyan-500 shadow-lg shadow-cyan-500/50"></div>
                    <div className="flex-1 pb-5 border-b border-white/5 last:border-0 last:pb-0">
                      <div className="flex items-center gap-2">
                        <div className="text-sm text-slate-200 font-medium">{activity.event || activity.type}</div>
                        <span className="text-xs px-2 py-0.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                          {activity.category}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 mt-1">{activity.description}</div>
                      <div className="text-xs text-slate-600 mt-1">{activity.time || new Date().toLocaleString()}</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-slate-600 pt-4 border-t border-white/5">
        <span className="font-medium">MEMORA v0.1.0</span>
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50 animate-pulse"></span>
          {lastSynced ? `Synced at ${lastSynced}` : "Ready to build your memory"}
        </span>
      </div>

      {/* Detail Modal */}
      <DetailModal 
        isOpen={!!selectedCategory} 
        category={selectedCategory} 
        onClose={() => setSelectedCategory(null)} 
      />

      {/* Upload Modal */}
      <UploadModal
        isOpen={!!uploadType}
        type={uploadType}
        onClose={() => setUploadType(null)}
        onUploadComplete={refreshData}
      />
    </motion.div>
  );
}