"use client";

import { useState, useEffect } from "react";
import { 
  FileText, Image as ImageIcon, Mail, Calendar as CalendarIcon, 
  FileCode, Search, FolderOpen, Upload, ChevronDown, ChevronUp,
  BarChart3, AlertCircle, CheckCircle2, Clock, Tag, Eye, Trash2
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api, Source } from "@/lib/api";

type SourceType = "pdf" | "image" | "email" | "calendar" | "note" | "all";

interface TypePanel {
  type: SourceType;
  label: string;
  icon: any;
  color: string;
  bgColor: string;
  borderColor: string;
}

const TYPE_PANELS: TypePanel[] = [
  { type: "all", label: "All Sources", icon: FolderOpen, color: "text-slate-300", bgColor: "bg-slate-800/50", borderColor: "border-slate-700" },
  { type: "pdf", label: "PDF Documents", icon: FileText, color: "text-blue-400", bgColor: "bg-blue-950/30", borderColor: "border-blue-800/50" },
  { type: "image", label: "Screenshots", icon: ImageIcon, color: "text-emerald-400", bgColor: "bg-emerald-950/30", borderColor: "border-emerald-800/50" },
  { type: "email", label: "Emails", icon: Mail, color: "text-violet-400", bgColor: "bg-violet-950/30", borderColor: "border-violet-800/50" },
  { type: "calendar", label: "Calendar Events", icon: CalendarIcon, color: "text-amber-400", bgColor: "bg-amber-950/30", borderColor: "border-amber-800/50" },
  { type: "note", label: "Notes", icon: FileCode, color: "text-rose-400", bgColor: "bg-rose-950/30", borderColor: "border-rose-800/50" },
];

const TYPE_COLORS: Record<string, string> = {
  pdf: "text-blue-400",
  image: "text-emerald-400",
  email: "text-violet-400",
  calendar: "text-amber-400",
  note: "text-rose-400",
};

const TYPE_BG: Record<string, string> = {
  pdf: "bg-blue-500/10",
  image: "bg-emerald-500/10",
  email: "bg-violet-500/10",
  calendar: "bg-amber-500/10",
  note: "bg-rose-500/10",
};

const TYPE_ICONS: Record<string, any> = {
  pdf: FileText,
  image: ImageIcon,
  email: Mail,
  calendar: CalendarIcon,
  note: FileCode,
};

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [search, setSearch] = useState("");
  const [activePanel, setActivePanel] = useState<SourceType>("all");
  const [loading, setLoading] = useState(true);
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const [sourceStats, setSourceStats] = useState({ total: 0, byType: {} as Record<string, number> });

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    setLoading(true);
    try {
      const res = await api.getSources();
      if (res.success) {
        setSources(res.data.sources);
        
        // Calculate stats
        const stats: Record<string, number> = {};
        res.data.sources.forEach(s => {
          stats[s.source_type] = (stats[s.source_type] || 0) + 1;
        });
        setSourceStats({ total: res.data.sources.length, byType: stats });
      }
    } catch (e) {
      console.error("Failed to load sources:", e);
    } finally {
      setLoading(false);
    }
  };

  const filteredSources = sources.filter((s) => {
    const matchesSearch = s.filename.toLowerCase().includes(search.toLowerCase()) || 
                         s.title.toLowerCase().includes(search.toLowerCase());
    const matchesPanel = activePanel === "all" || s.source_type === activePanel;
    return matchesSearch && matchesPanel;
  });

  const toggleExpand = (id: string) => {
    setExpandedSource(expandedSource === id ? null : id);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
          <span className="text-slate-400 text-sm">Loading sources...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Sources</h1>
          <p className="text-slate-400 text-sm">Manage and explore your connected information</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
          <BarChart3 size={16} className="text-cyan-400" />
          <span className="text-cyan-400 font-medium">{sourceStats.total}</span>
          <span className="text-slate-500 text-sm">total</span>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          placeholder="Search by filename or title..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-[#0a0f1e]/60 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-all"
        />
      </div>

      {/* Type Panels */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {TYPE_PANELS.map((panel) => {
          const Icon = panel.icon;
          const count = panel.type === "all" ? sourceStats.total : (sourceStats.byType[panel.type] || 0);
          const isActive = activePanel === panel.type;
          
          return (
            <motion.button
              key={panel.type}
              onClick={() => setActivePanel(panel.type)}
              className={`relative p-4 rounded-xl border transition-all duration-300 ${
                isActive 
                  ? `${panel.bgColor} ${panel.borderColor} shadow-lg` 
                  : "bg-[#0a0f1e]/40 border-white/5 hover:border-white/10"
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isActive ? "bg-white/10" : "bg-white/5"}`}>
                  <Icon size={20} className={isActive ? panel.color : "text-slate-500"} />
                </div>
                <div className="text-left">
                  <p className={`text-xs font-medium ${isActive ? "text-white" : "text-slate-400"}`}>
                    {panel.label}
                  </p>
                  <p className={`text-lg font-bold ${isActive ? panel.color : "text-slate-300"}`}>
                    {count}
                  </p>
                </div>
              </div>
              
              {isActive && (
                <motion.div
                  layoutId="activePanel"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-b-xl"
                />
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Sources List */}
      {filteredSources.length > 0 ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span>Showing {filteredSources.length} of {sources.length} sources</span>
            {search && <span>Filtered by: "{search}"</span>}
          </div>
          
          <AnimatePresence mode="popLayout">
            {filteredSources.map((source, i) => {
              const Icon = TYPE_ICONS[source.source_type] || FileText;
              const isExpanded = expandedSource === source.id;
              const typeColor = TYPE_COLORS[source.source_type] || "text-slate-400";
              const typeBg = TYPE_BG[source.source_type] || "bg-slate-500/10";
              
              return (
                <motion.div
                  key={source.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: i * 0.03 }}
                  className="glass-card overflow-hidden"
                >
                  {/* Main Row */}
                  <div 
                    className="p-4 flex items-center gap-4 cursor-pointer hover:bg-white/5 transition-colors"
                    onClick={() => toggleExpand(source.id)}
                  >
                    {/* Icon */}
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${typeBg}`}>
                      <Icon size={24} className={typeColor} />
                    </div>
                    
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-sm font-medium text-white truncate">
                          {source.title || source.filename}
                        </span>
                        <span className={`text-xs px-2.5 py-1 rounded-lg ${typeBg} ${typeColor} font-medium`}>
                          {source.source_type.toUpperCase()}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          {new Date(source.upload_time).toLocaleDateString()}
                        </span>
                        {source.page_count && (
                          <span>{source.page_count} pages</span>
                        )}
                      </div>
                    </div>
                    
                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <Eye size={16} className="text-slate-400" />
                      </button>
                      <button className="p-2 hover:bg-rose-500/10 rounded-lg transition-colors">
                        <Trash2 size={16} className="text-rose-400" />
                      </button>
                      <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        {isExpanded ? <ChevronUp size={18} className="text-slate-400" /> : <ChevronDown size={18} className="text-slate-400" />}
                      </button>
                    </div>
                  </div>
                  
                  {/* Expanded Content */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="border-t border-white/5"
                      >
                        <div className="p-4 space-y-4">
                          {/* Document Stats */}
                          <div className="grid grid-cols-3 gap-4">
                            <div className="p-3 bg-[#0a0f1e]/60 rounded-lg border border-white/5">
                              <div className="text-2xl font-bold text-white">0</div>
                              <div className="text-xs text-slate-500">Facts Extracted</div>
                            </div>
                            <div className="p-3 bg-[#0a0f1e]/60 rounded-lg border border-white/5">
                              <div className="text-2xl font-bold text-white">0</div>
                              <div className="text-xs text-slate-500">Entities Found</div>
                            </div>
                            <div className="p-3 bg-[#0a0f1e]/60 rounded-lg border border-white/5">
                              <div className="text-2xl font-bold text-white">0</div>
                              <div className="text-xs text-slate-500">Events Detected</div>
                            </div>
                          </div>
                          
                          {/* Status */}
                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                              <CheckCircle2 size={14} className="text-emerald-400" />
                              <span className="text-xs text-emerald-300">Processed Successfully</span>
                            </div>
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-500/10 border border-slate-500/20 rounded-lg">
                              <AlertCircle size={14} className="text-slate-400" />
                              <span className="text-xs text-slate-400">No Conflicts</span>
                            </div>
                          </div>
                          
                          {/* Actions */}
                          <div className="flex items-center gap-2">
                            <button className="px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-lg text-sm font-medium hover:bg-cyan-500/20 transition-colors">
                              View in Graph
                            </button>
                            <button className="px-4 py-2 bg-white/5 border border-white/10 text-slate-400 rounded-lg text-sm font-medium hover:bg-white/10 transition-colors">
                              View Source
                            </button>
                            <button className="px-4 py-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg text-sm font-medium hover:bg-rose-500/20 transition-colors">
                              Delete
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-4">
            <FolderOpen size={32} className="text-slate-600" />
          </div>
          <p className="text-slate-400 font-medium mb-1">No sources found</p>
          <p className="text-slate-600 text-sm mb-4">
            {search ? "Try adjusting your search" : "Upload documents to start building your memory"}
          </p>
          {!search && (
            <button className="px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/20 transition-colors">
              <span className="flex items-center gap-2">
                <Upload size={16} />
                Upload Your First Source
              </span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
