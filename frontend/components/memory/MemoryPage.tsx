"use client";

import { useState, useEffect } from "react";
import { Database, Users, Calendar, FileText, Search } from "lucide-react";
import { motion } from "framer-motion";
import { api, MemoryFact } from "@/lib/api";

const typeIcons = { fact: Database, event: Calendar, relationship: Users, document: FileText };
const typeColors = { fact: "text-cyan-400", event: "text-emerald-400", relationship: "text-violet-400", document: "text-amber-400" };

export default function MemoryPage() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [facts, setFacts] = useState<MemoryFact[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getFacts().then(res => {
      if (res.success) setFacts(res.data.facts);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const filtered = facts.filter((m) => {
    const statement = `${m.subject} ${m.predicate} ${m.object}`;
    return statement.toLowerCase().includes(search.toLowerCase());
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
          <span className="text-slate-400 text-sm">Loading memories...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Memory</h1>
          <p className="text-slate-400">Everything MEMORA remembers, organized and connected</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input type="text" placeholder="Search everything MEMORA remembers..." value={search} onChange={(e) => setSearch(e.target.value)} className="w-full pl-10 pr-4 py-2.5 bg-[#111827]/60 border border-white/5 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all" />
        </div>
      </div>

      {filtered.length > 0 ? (
        <div className="space-y-2">
          {filtered.map((memory, i) => {
            const statement = `${memory.subject} ${memory.predicate} ${memory.object}`;
            const type = memory.predicate.includes('has_member') || memory.predicate.includes('assigned_to') ? 'relationship' :
                        memory.predicate.includes('has_demo_date') || memory.predicate.includes('created_at') ? 'event' : 'fact';
            const Icon = typeIcons[type as keyof typeof typeIcons] || Database;
            
            return (
              <motion.div key={memory.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="glass-card p-4 flex items-center gap-4 cursor-pointer hover:border-white/10 transition-all group">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${typeColors[type as keyof typeof typeColors]}`}>
                  <Icon size={20} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs px-2 py-0.5 rounded-lg ${memory.status === "confirmed" ? "bg-emerald-500/10 text-emerald-400" : memory.status === "likely_current" ? "bg-cyan-500/10 text-cyan-400" : "bg-amber-500/10 text-amber-400"}`}>{memory.status}</span>
                    <span className="text-xs text-slate-500">{new Date(memory.observed_at).toLocaleDateString()}</span>
                  </div>
                  <div className="text-sm text-slate-200 font-medium">{statement}</div>
                </div>
                <div className="text-xs text-slate-500">{(memory.confidence * 100).toFixed(0)}%</div>
              </motion.div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12">
          <Database size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400">No memories found</p>
          <p className="text-slate-600 text-sm mt-1">Upload documents to start building your memory</p>
        </div>
      )}
    </div>
  );
}
