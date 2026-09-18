"use client";

import { useState, useEffect } from "react";
import { AlertTriangle, CheckCircle } from "lucide-react";
import { motion } from "framer-motion";
import { api, Conflict } from "@/lib/api";

export default function ConflictsPage() {
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [selectedConflict, setSelectedConflict] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "unresolved" | "resolved">("all");

  useEffect(() => {
    api.getConflicts(filter === "all" ? "all" : filter).then(res => {
      if (res.success) setConflicts(res.data.conflicts);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [filter]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
          <span className="text-slate-400 text-sm">Loading conflicts...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Conflicts</h1>
          <p className="text-slate-400">Information that doesn't fully agree</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="px-2.5 py-1 bg-rose-500/10 text-rose-400 rounded-lg border border-rose-500/20">{conflicts.filter(c => !c.resolution).length} unresolved</span>
          <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-lg border border-emerald-500/20">{conflicts.filter(c => c.resolution).length} resolved</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {(["all", "unresolved", "resolved"] as const).map((f) => (
          <button key={f} onClick={() => setFilter(f)} className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${filter === f ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/20" : "bg-[#111827]/60 text-slate-400 border border-white/5 hover:text-slate-200 hover:border-white/10"}`}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {conflicts.length > 0 ? (
        <div className="space-y-4">
          {conflicts.map((conflict, i) => (
            <motion.div key={conflict.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className={`glass-card p-6 cursor-pointer transition-all duration-200 ${selectedConflict === conflict.id ? "border-cyan-500/30" : "hover:border-white/10"}`} onClick={() => setSelectedConflict(conflict.id === selectedConflict ? null : conflict.id)}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle size={16} className="text-amber-500" />
                    <span className="text-sm font-medium text-slate-300">{conflict.subject} → {conflict.predicate}</span>
                  </div>
                  {!conflict.resolution ? (
                    <span className="inline-flex items-center px-2 py-0.5 bg-rose-500/10 text-rose-400 rounded text-xs font-medium border border-rose-500/20 mt-2">Unresolved</span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-xs font-medium border border-emerald-500/20 mt-2">Resolved</span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-rose-500/5 border border-rose-500/20 rounded-xl">
                  <div className="text-2xl font-bold text-rose-400 mb-1">{conflict.fact_a.value}</div>
                  <div className="text-xs text-slate-500">{conflict.fact_a.source}</div>
                  <div className="text-xs text-slate-600 mt-1">{conflict.fact_a.date}</div>
                </div>
                <div className="p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-xl">
                  <div className="text-2xl font-bold text-emerald-400 mb-1">{conflict.fact_b.value}</div>
                  <div className="text-xs text-slate-500">{conflict.fact_b.source}</div>
                  <div className="text-xs text-slate-600 mt-1">{conflict.fact_b.date}</div>
                </div>
              </div>

              {conflict.resolution && (
                <div className="mt-4 p-3 bg-cyan-500/5 border border-cyan-500/20 rounded-lg">
                  <div className="text-xs text-cyan-400 font-medium mb-1">System Interpretation</div>
                  <div className="text-sm text-slate-300">{conflict.resolution}</div>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <CheckCircle size={48} className="mx-auto text-emerald-500 mb-4" />
          <p className="text-slate-400">No conflicts detected</p>
          <p className="text-slate-600 text-sm mt-1">All your memories are consistent</p>
        </div>
      )}
    </div>
  );
}
