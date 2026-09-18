"use client";

import { useState } from "react";
import { CheckCircle, Clock, AlertCircle, Trash2, Download } from "lucide-react";
import { motion } from "framer-motion";

const mockActions = [
  { id: "1", type: "reminder", title: "Create reminder for Project Atlas demo", description: "Set a reminder 3 days before the demo", basedOn: "Project Atlas → September 26", scheduledFor: "September 23, 9:00 AM", status: "proposed", evidence: "Rahul Message — Sep 22" },
  { id: "2", type: "summary", title: "Generate project summary", description: "Create a summary of Project Atlas status", basedOn: "Project Atlas", scheduledFor: "Immediately", status: "pending", evidence: "5 sources, 18 facts" },
  { id: "3", type: "email", title: "Draft email to stakeholders", description: "Notify about deadline change", basedOn: "Project Atlas demo date moved", scheduledFor: "Immediately", status: "approved", evidence: "Rahul Message — Sep 22" },
];

export default function ActionsPage() {
  const [selectedTab, setSelectedTab] = useState<"suggested" | "pending" | "completed">("suggested");
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  const filtered = mockActions.filter((a) => {
    if (selectedTab === "suggested") return a.status === "proposed";
    if (selectedTab === "pending") return a.status === "pending";
    return a.status === "approved" || a.status === "executed";
  });

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Actions</h1>
        <p className="text-slate-400">Turn memory into action</p>
      </div>

      <div className="flex items-center gap-1 p-1 bg-[#111827]/60 rounded-xl w-fit border border-white/5">
        {[{ key: "suggested", label: "Suggested", icon: AlertCircle }, { key: "pending", label: "Pending", icon: Clock }, { key: "completed", label: "Completed", icon: CheckCircle }].map((tab) => {
          const Icon = tab.icon;
          return (
            <button key={tab.key} onClick={() => setSelectedTab(tab.key as any)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedTab === tab.key ? "bg-cyan-500/15 text-cyan-400" : "text-slate-400 hover:text-slate-200"}`}>
              <Icon size={14} />{tab.label}
            </button>
          );
        })}
      </div>

      <div className="space-y-3">
        {filtered.map((action, i) => (
          <motion.div key={action.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className={`glass-card p-5 cursor-pointer transition-all ${selectedAction === action.id ? "border-cyan-500/30" : "hover:border-white/10"}`} onClick={() => setSelectedAction(action.id === selectedAction ? null : action.id)}>
            <div className="flex items-start gap-4">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${action.status === "proposed" ? "bg-amber-500/10 text-amber-400" : action.status === "pending" ? "bg-cyan-500/10 text-cyan-400" : "bg-emerald-500/10 text-emerald-400"}`}>
                {action.status === "proposed" ? <AlertCircle size={20} /> : action.status === "pending" ? <Clock size={20} /> : <CheckCircle size={20} />}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-semibold text-white">{action.title}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-lg ${action.status === "proposed" ? "bg-amber-500/10 text-amber-400" : action.status === "pending" ? "bg-cyan-500/10 text-cyan-400" : "bg-emerald-500/10 text-emerald-400"}`}>{action.status}</span>
                </div>
                <div className="text-sm text-slate-400 mb-2">{action.description}</div>
                <div className="text-xs text-slate-500">Based on: {action.basedOn}</div>
                <div className="text-xs text-slate-600 mt-1">Evidence: {action.evidence}</div>
              </div>
            </div>
            {selectedAction === action.id && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="mt-4 pt-4 border-t border-white/5 flex gap-3">
                {action.status === "proposed" && <>
                  <button className="px-4 py-2 bg-emerald-500/15 text-emerald-400 rounded-lg text-sm font-medium hover:bg-emerald-500/25 transition-colors border border-emerald-500/20">Approve</button>
                  <button className="px-4 py-2 bg-[#111827]/60 border border-white/5 text-slate-400 rounded-lg text-sm font-medium hover:text-slate-200 hover:border-white/10 transition-all">Edit</button>
                  <button className="px-4 py-2 bg-[#111827]/60 border border-white/5 text-slate-400 rounded-lg text-sm font-medium hover:text-slate-200 hover:border-white/10 transition-all ml-auto">Dismiss</button>
                </>}
                {action.status === "pending" && <button className="px-4 py-2 bg-cyan-500/15 text-cyan-400 rounded-lg text-sm font-medium hover:bg-cyan-500/25 transition-colors border border-cyan-500/20">Execute</button>}
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
