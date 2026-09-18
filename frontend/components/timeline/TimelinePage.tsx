"use client";

import { useState, useEffect } from "react";
import { Calendar, Clock, MapPin, Users, FileText } from "lucide-react";
import { motion } from "framer-motion";
import { api, TimelineEvent } from "@/lib/api";

export default function TimelinePage() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTimeline(30).then(res => {
      if (res.success) {
        setEvents(res.data.events.sort((a, b) => new Date(a.start_at).getTime() - new Date(b.start_at).getTime()));
      }
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
          <span className="text-slate-400 text-sm">Loading timeline...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Timeline</h1>
        <p className="text-slate-400">Your memories, in chronological order</p>
      </div>

      {events.length > 0 ? (
        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-cyan-500/30 via-white/10 to-transparent" />
          <div className="space-y-4">
            {events.map((event, i) => (
              <motion.div key={event.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className={`relative pl-20 cursor-pointer group ${selectedEvent === event.id ? "scale-[1.02]" : ""}`} onClick={() => setSelectedEvent(event.id === selectedEvent ? null : event.id)}>
                <div className="absolute left-0 top-0 w-16 h-16 rounded-xl bg-[#111827] border border-white/10 flex flex-col items-center justify-center group-hover:border-cyan-500/30 transition-colors">
                  <span className="text-xs text-slate-500">{new Date(event.start_at).toLocaleDateString('en-US', { month: 'short' })}</span>
                  <span className="text-lg font-bold text-white">{new Date(event.start_at).getDate()}</span>
                </div>
                <div className={`absolute left-6 top-6 w-3 h-3 rounded-full border-2 ${selectedEvent === event.id ? "bg-cyan-500 border-cyan-500 shadow-lg shadow-cyan-500/50" : "bg-[#111827] border-white/20 group-hover:border-cyan-500/50"}`} />
                <div className="glass-card p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-cyan-400 font-medium">{new Date(event.start_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                    {event.participants && <span className="text-xs text-slate-500 flex items-center gap-1"><Users size={12} />{event.participants.join(", ")}</span>}
                  </div>
                  <h3 className="text-base font-semibold text-white mb-1">{event.title}</h3>
                  <p className="text-sm text-slate-400">{event.description}</p>
                  {event.filename && <p className="text-xs text-slate-600 mt-2">Source: {event.filename}</p>}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <Calendar size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400">No events in timeline</p>
          <p className="text-slate-600 text-sm mt-1">Events will appear as you ingest documents</p>
        </div>
      )}
    </div>
  );
}
