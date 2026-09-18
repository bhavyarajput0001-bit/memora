"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, CheckCircle, AlertTriangle, FileText, ArrowRight, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  conflicts?: Conflict[];
  confidence?: number;
  status?: string;
  metadata?: {
    sourcesAnalyzed?: number;
    factsFound?: number;
    conflictsDetected?: number;
  };
}

interface Source {
  id: string;
  filename: string;
  page?: number;
  snippet: string;
}

interface Conflict {
  fact_a: { value: string; source: string; date: string };
  fact_b: { value: string; source: string; date: string };
  resolution?: string;
}

const mockConversations = [
  { id: "1", query: "What is the latest deadline for Project Atlas?", time: "2 hours ago" },
  { id: "2", query: "Who is responsible for the backend?", time: "Yesterday" },
  { id: "3", query: "What changed between Sep 20 and Sep 22?", time: "2 days ago" },
];

const mockResponse: Message = {
  id: "resp-1",
  role: "assistant",
  content: "Project Atlas' latest demo deadline appears to be **September 26**.",
  confidence: 0.97,
  status: "likely_current",
  sources: [
    { id: "doc-2", filename: "Rahul Message", page: 1, snippet: "...the demo has been moved to September 26, 2026..." },
    { id: "doc-1", filename: "Project Notes", page: 1, snippet: "The project demo is scheduled for September 24, 2026." },
  ],
  conflicts: [
    {
      fact_a: { value: "Sep 24", source: "Project Notes", date: "Sep 20" },
      fact_b: { value: "Sep 26", source: "Rahul Message", date: "Sep 22" },
      resolution: "Likely superseded by Rahul Message",
    },
  ],
  metadata: { sourcesAnalyzed: 4, factsFound: 2, conflictsDetected: 1 },
};

export default function AskPage() {
  const [messages, setMessages] = useState<Message[]>([mockResponse]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage: Message = { id: `user-${Date.now()}`, role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setTimeout(() => {
      setMessages((prev) => [...prev, mockResponse]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="flex h-full gap-6">
      {/* Left Panel */}
      <div className="w-64 flex-shrink-0 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-white">Conversations</h2>
          <button className="p-2 rounded-lg hover:bg-[#111827] text-slate-400 transition-colors">
            <Send size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto space-y-1">
          {mockConversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => setSelectedConversation(conv.id)}
              className={`w-full text-left px-3 py-3 rounded-xl text-sm transition-all duration-200 ${
                selectedConversation === conv.id
                  ? "bg-cyan-500/15 text-cyan-400"
                  : "text-slate-400 hover:text-slate-200 hover:bg-[#111827]"
              }`}
            >
              <div className="truncate font-medium">{conv.query}</div>
              <div className="text-xs mt-1 opacity-60">{conv.time}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Center Panel */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto space-y-6">
          {messages.map((msg) => (
            <motion.div key={msg.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              {msg.role === "user" && (
                <div className="flex justify-end">
                  <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="max-w-2xl px-5 py-3.5 bg-gradient-to-r from-cyan-500/20 to-cyan-600/20 border border-cyan-500/30 rounded-2xl text-white">
                    {msg.content}
                  </motion.div>
                </div>
              )}
              {msg.role === "assistant" && (
                <div className="space-y-4 max-w-3xl">
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-400 to-cyan-600 flex items-center justify-center">
                        <Sparkles size={12} className="text-white" />
                      </div>
                      <span className="text-xs font-medium text-cyan-400 uppercase tracking-wider">MEMORA</span>
                      <CheckCircle size={14} className="text-emerald-500" />
                      <span className="text-xs text-slate-500">{msg.status === "likely_current" ? "LIKELY CURRENT" : msg.status || "ANSWER"}</span>
                      {msg.confidence && <span className="text-xs text-slate-500">{(msg.confidence * 100).toFixed(0)}% confidence</span>}
                    </div>
                    <div className="prose prose-invert max-w-none">
                      <p className="text-slate-200 text-lg leading-relaxed">{msg.content}</p>
                    </div>
                  </div>

                  {msg.conflicts && msg.conflicts.length > 0 && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <AlertTriangle size={16} className="text-amber-500" />
                        <span className="text-sm font-semibold text-amber-500">CONFLICT DETECTED</span>
                      </div>
                      <div className="space-y-2">
                        {msg.conflicts.map((conflict, i) => (
                          <div key={i} className="text-sm">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="px-2.5 py-1 bg-rose-500/10 text-rose-400 rounded-lg text-xs font-medium border border-rose-500/20">{conflict.fact_a.value}</span>
                              <span className="text-slate-500 text-xs">{conflict.fact_a.source} — {conflict.fact_a.date}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-lg text-xs font-medium border border-emerald-500/20">{conflict.fact_b.value}</span>
                              <span className="text-slate-500 text-xs">{conflict.fact_b.source} — {conflict.fact_b.date}</span>
                            </div>
                            {conflict.resolution && <div className="text-xs text-slate-500 mt-2">{conflict.resolution}</div>}
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {msg.sources && msg.sources.length > 0 && (
                    <div>
                      <div className="text-xs text-slate-500 mb-2 uppercase tracking-wider">Sources ({msg.sources.length})</div>
                      <div className="space-y-2">
                        {msg.sources.map((source) => (
                          <div key={source.id} className="flex items-start gap-3 p-3 glass-card">
                            <FileText size={16} className="text-cyan-500 flex-shrink-0 mt-0.5" />
                            <div className="flex-1 min-w-0">
                              <div className="text-sm text-slate-200 font-medium">{source.filename}</div>
                              {source.page && <div className="text-xs text-slate-500">Page {source.page}</div>}
                              <div className="text-xs text-slate-400 mt-1 line-clamp-2">"{source.snippet}"</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          ))}
          {isLoading && (
            <div className="flex items-center gap-2 text-slate-500">
              <Loader2 size={16} className="animate-spin" />
              <span className="text-sm">Analyzing sources...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="pt-4 border-t border-white/5">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask a follow-up question..."
              className="flex-1 px-4 py-3 bg-[#111827]/60 border border-white/5 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
            <button onClick={handleSend} disabled={isLoading || !input.trim()} className="px-4 py-3 bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed text-white rounded-xl transition-all duration-200 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40">
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="w-80 flex-shrink-0 hidden lg:block">
        <div className="glass-card p-5 h-full">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <FileText size={16} className="text-cyan-500" />
            Source Evidence
          </h3>
          <div className="space-y-3">
            {mockResponse.sources?.map((source) => (
              <div key={source.id} className="p-3 bg-[#0a0f1e]/60 border border-white/5 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <FileText size={14} className="text-cyan-500" />
                  <span className="text-sm text-slate-200 font-medium">{source.filename}</span>
                </div>
                {source.page && <div className="text-xs text-slate-500 mb-2">Page {source.page}</div>}
                <div className="text-xs text-slate-400">"{source.snippet}"</div>
                <div className="flex gap-2 mt-3">
                  <button className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors">Open source</button>
                  <button className="text-xs text-slate-500 hover:text-slate-300 transition-colors">View timeline</button>
                  <button className="text-xs text-slate-500 hover:text-slate-300 transition-colors">View graph</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
