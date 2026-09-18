"use client";

import { useState, useEffect } from "react";
import { X, Search, Database, Users, Calendar, TrendingUp, FileText, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";

type Category = "facts" | "people" | "events" | "relationships" | "sources";

interface ModalProps {
  isOpen: boolean;
  category: Category | null;
  onClose: () => void;
}

const categoryConfig: Record<Category, { label: string; icon: any; color: string }> = {
  facts: { label: "Facts", icon: Database, color: "cyan" },
  people: { label: "People", icon: Users, color: "emerald" },
  events: { label: "Events", icon: Calendar, color: "amber" },
  relationships: { label: "Relationships", icon: TrendingUp, color: "violet" },
  sources: { label: "Sources", icon: FileText, color: "slate" },
};

const colorClasses: Record<string, { text: string; bg: string; border: string }> = {
  cyan: { text: "text-cyan-400", bg: "bg-cyan-500/10", border: "border-cyan-500/20" },
  emerald: { text: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
  amber: { text: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20" },
  violet: { text: "text-violet-400", bg: "bg-violet-500/10", border: "border-violet-500/20" },
  slate: { text: "text-slate-400", bg: "bg-slate-500/10", border: "border-slate-500/20" },
};

export default function DetailModal({ isOpen, category, onClose }: ModalProps) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  useEffect(() => {
    if (!isOpen || !category) return;
    
    loadCategoryData(category);
  }, [isOpen, category]);

  const loadCategoryData = async (cat: Category) => {
    setLoading(true);
    try {
      let response;
      
      switch (cat) {
        case "facts":
          response = await api.getFacts();
          if (response.success) {
            setItems(response.data.facts || []);
          }
          break;
        case "people":
          response = await api.getEntities();
          if (response.success) {
            setItems(response.data.entities || []);
          }
          break;
        case "events":
          response = await api.getTimeline(30);
          if (response.success) {
            setItems(response.data.events || []);
          }
          break;
        case "sources":
          response = await api.getSources();
          if (response.success) {
            setItems(response.data.sources || []);
          }
          break;
        case "relationships":
          // Get relationships from facts
          const factsResp = await api.getFacts();
          if (factsResp.success) {
            const relationships = factsResp.data.facts?.filter((f: any) => 
              f.predicate?.includes("works_on") || 
              f.predicate?.includes("assigned_to") ||
              f.predicate?.includes("has_member") ||
              f.predicate?.includes("leads")
            ) || [];
            setItems(relationships);
          }
          break;
      }
    } catch (error) {
      console.error(`Failed to load ${cat}:`, error);
    } finally {
      setLoading(false);
    }
  };

  const filteredItems = items.filter(item => {
    const searchStr = JSON.stringify(item).toLowerCase();
    return searchStr.includes(searchQuery.toLowerCase());
  });

  const config = category ? categoryConfig[category] : null;
  const colors = config ? colorClasses[config.color] : null;
  const Icon = config?.icon || Database;

  if (!mounted) return null;

  return (
    <AnimatePresence>
      {isOpen && category && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/70 backdrop-blur-md z-[60]"
          />

          {/* Modal Panel */}
          <motion.div
            initial={{ opacity: 0, x: 300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 300 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed top-0 right-0 h-full w-96 glass-card modal z-[70] flex flex-col border-l border-white/10"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/5 flex-shrink-0">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors?.bg} border ${colors?.border}`}>
                  <Icon size={22} className={colors?.text} />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">{config?.label}</h2>
                  <p className="text-sm text-slate-500">
                    {filteredItems.length} {filteredItems.length === 1 ? "item" : "items"}
                  </p>
                </div>
              </div>
              
              <button
                onClick={onClose}
                className="p-2.5 hover:bg-white/10 rounded-xl transition-all"
              >
                <X size={20} className="text-slate-400" />
              </button>
            </div>

            {/* Search Bar */}
            <div className="px-6 py-4 border-b border-white/5 flex-shrink-0">
              <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={`Search ${config?.label.toLowerCase()}...`}
                  className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
                />
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
              {loading ? (
                <div className="flex flex-col items-center justify-center h-full gap-4">
                  <Loader2 size={32} className="text-cyan-500 animate-spin" />
                  <p className="text-slate-500 text-sm">Loading {config?.label.toLowerCase()}...</p>
                </div>
              ) : filteredItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4">
                    <Icon size={28} className="text-slate-600" />
                  </div>
                  <p className="text-slate-400 font-medium mb-1">No {config?.label.toLowerCase()} found</p>
                  <p className="text-xs text-slate-600">
                    {searchQuery 
                      ? "Try adjusting your search" 
                      : `Upload documents or connect your calendar to add ${config?.label.toLowerCase()}`
                    }
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredItems.map((item, i) => (
                    <motion.div
                      key={item.id || i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                      className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-all cursor-pointer group"
                    >
                      {category === "facts" && (
                        <div className="space-y-2">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                {item.status || "confirmed"}
                              </span>
                              <span className="text-xs text-slate-500">
                                {new Date(item.observed_at).toLocaleDateString()}
                              </span>
                            </div>
                            <span className="text-xs text-slate-600">
                              {(item.confidence * 100).toFixed(0)}% confident
                            </span>
                          </div>
                          <p className="text-sm text-slate-200 font-medium">
                            {item.subject} <span className="text-cyan-400">{item.predicate}</span> {item.object}
                          </p>
                          <p className="text-xs text-slate-500">Source: {item.source_id}</p>
                        </div>
                      )}

                      {category === "people" && (
                        <div className="space-y-2">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-emerald-500/15 border border-emerald-500/20 flex items-center justify-center">
                              <Users size={18} className="text-emerald-400" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-slate-200">{item.canonical_name}</p>
                              <p className="text-xs text-slate-500">{item.entity_type}</p>
                            </div>
                          </div>
                          {item.aliases && item.aliases.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {item.aliases.map((alias: string, idx: number) => (
                                <span key={idx} className="text-xs px-2 py-0.5 bg-white/5 text-slate-400 rounded-full">
                                  {alias}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {category === "events" && (
                        <div className="space-y-2">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="text-sm font-medium text-slate-200">{item.title}</p>
                              <p className="text-xs text-slate-500 mt-1">{item.description}</p>
                            </div>
                            <span className="text-xs px-2 py-1 bg-amber-500/10 text-amber-400 rounded-lg border border-amber-500/20">
                              {new Date(item.start_at).toLocaleDateString()}
                            </span>
                          </div>
                          {item.location && (
                            <p className="text-xs text-slate-500 flex items-center gap-1">
                              📍 {item.location}
                            </p>
                          )}
                        </div>
                      )}

                      {category === "relationships" && (
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-slate-200">{item.subject}</span>
                            <span className="text-cyan-400 text-sm">→</span>
                            <span className="text-sm text-slate-200">{item.object}</span>
                          </div>
                          <p className="text-xs text-slate-500">{item.predicate}</p>
                        </div>
                      )}

                      {category === "sources" && (
                        <div className="space-y-2">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-violet-500/15 border border-violet-500/20 flex items-center justify-center">
                              <FileText size={18} className="text-violet-400" />
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-medium text-slate-200">{item.title || item.filename}</p>
                              <p className="text-xs text-slate-500">{item.source_type}</p>
                            </div>
                            <span className="text-xs text-slate-500">
                              {new Date(item.upload_time).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="flex gap-3 text-xs text-slate-500">
                            {item.facts && <span>{item.facts} facts</span>}
                            {item.entities && <span>{item.entities} entities</span>}
                            {item.events && <span>{item.events} events</span>}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-white/5 flex items-center justify-between flex-shrink-0">
              <p className="text-xs text-slate-500">
                Click any item to view details
              </p>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-white/5 border border-white/10 text-slate-400 rounded-xl text-sm hover:bg-white/10 hover:text-slate-200 transition-all"
              >
                Close
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}