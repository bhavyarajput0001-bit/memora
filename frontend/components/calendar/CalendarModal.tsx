"use client";

import { useState, useEffect } from "react";
import { 
  Calendar as CalendarIcon, 
  Plus, 
  Clock, 
  MapPin,
  CheckCircle,
  X,
  TrendingUp,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time?: string;
  location?: string;
  description?: string;
  source: "manual" | "google" | "apple" | "other";
}

interface CalendarModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CalendarModal({ isOpen, onClose }: CalendarModalProps) {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [newEvent, setNewEvent] = useState({
    title: "",
    date: "",
    time: "",
    location: "",
    description: "",
  });
  const [isAdding, setIsAdding] = useState(false);

  // Load events from backend
  useEffect(() => {
    const loadEvents = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/timeline/?days=30");
        const data = await response.json();
        if (data.success && data.data.events) {
          setEvents(data.data.events.map((e: any) => ({
            id: e.id,
            title: e.title || e.description,
            date: e.date,
            time: e.time,
            location: e.location,
            description: e.description,
            source: "manual" as const,
          })));
        }
      } catch (error) {
        console.error("Failed to load calendar events:", error);
      }
    };
    if (isOpen) loadEvents();
  }, [isOpen]);

  const addEvent = () => {
    if (!newEvent.title || !newEvent.date) return;
    
    const event: CalendarEvent = {
      id: Date.now().toString(),
      ...newEvent,
      source: "manual",
    };
    
    setEvents([event, ...events]);
    setNewEvent({ title: "", date: "", time: "", location: "", description: "" });
    setIsAdding(false);

    // Save to backend
    fetch("http://127.0.0.1:8000/api/v1/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: newEvent.title,
        date: newEvent.date,
        time: newEvent.time,
        location: newEvent.location,
        description: newEvent.description,
      }),
    }).catch(console.error);
  };

  const deleteEvent = (id: string) => {
    setEvents(events.filter(e => e.id !== id));
  };

  const getDaysUntil = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const diff = Math.ceil((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", { 
      month: "short", 
      day: "numeric" 
    });
  };

  const formatFullDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", { 
      weekday: "short",
      month: "short", 
      day: "numeric",
      year: "numeric"
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal Panel - Glassmorphism */}
          <motion.div
            initial={{ opacity: 0, x: 300, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.95 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed top-0 right-0 h-full w-96 glass-card z-50 flex flex-col border-l border-white/10"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/20 flex items-center justify-center">
                  <CalendarIcon size={20} className="text-cyan-400" />
                </div>
                <div>
                  <h2 className="font-semibold text-white">Upcoming Events</h2>
                  <p className="text-xs text-slate-500">{events.length} events scheduled</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/10 rounded-xl transition-all"
              >
                <X size={18} className="text-slate-400" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 scroll-smooth">
              {events.length === 0 && !isAdding ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                  <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4">
                    <CalendarIcon size={28} className="text-slate-600" />
                  </div>
                  <p className="text-slate-400 font-medium mb-1">No events yet</p>
                  <p className="text-xs text-slate-600">Add your first event to get started</p>
                  <button
                    onClick={() => setIsAdding(true)}
                    className="mt-6 px-4 py-2.5 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-all flex items-center gap-2"
                  >
                    <Plus size={14} /> Add Event
                  </button>
                </div>
              ) : isAdding ? (
                /* Add Event Form */
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-slate-300">New Event</h3>
                    <button
                      onClick={() => setIsAdding(false)}
                      className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs text-slate-500 mb-1.5">Title *</label>
                      <input
                        type="text"
                        value={newEvent.title}
                        onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                        placeholder="Meeting title..."
                        className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-cyan-500/50 transition-colors"
                        autoFocus
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-slate-500 mb-1.5">Date *</label>
                        <input
                          type="date"
                          value={newEvent.date}
                          onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                          className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 outline-none focus:border-cyan-500/50 transition-colors"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-slate-500 mb-1.5">Time</label>
                        <input
                          type="time"
                          value={newEvent.time}
                          onChange={(e) => setNewEvent({ ...newEvent, time: e.target.value })}
                          className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 outline-none focus:border-cyan-500/50 transition-colors"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs text-slate-500 mb-1.5">Location</label>
                      <div className="relative">
                        <MapPin size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600" />
                        <input
                          type="text"
                          value={newEvent.location}
                          onChange={(e) => setNewEvent({ ...newEvent, location: e.target.value })}
                          placeholder="Add location..."
                          className="w-full pl-9 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-cyan-500/50 transition-colors"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs text-slate-500 mb-1.5">Description</label>
                      <textarea
                        value={newEvent.description}
                        onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                        placeholder="Add details..."
                        rows={3}
                        className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-cyan-500/50 transition-colors resize-none"
                      />
                    </div>
                  </div>

                  <button
                    onClick={addEvent}
                    disabled={!newEvent.title || !newEvent.date}
                    className="w-full px-4 py-2.5 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <CheckCircle size={14} /> Add Event
                  </button>
                </motion.div>
              ) : (
                /* Event List */
                <div className="space-y-3">
                  {events.map((event, i) => {
                    const daysUntil = getDaysUntil(event.date);
                    return (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="p-3 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-all group"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <div className={`w-2 h-2 rounded-full ${
                                daysUntil <= 0 ? "bg-emerald-500" :
                                daysUntil <= 3 ? "bg-amber-500" :
                                daysUntil <= 7 ? "bg-cyan-500" : "bg-slate-500"
                              }`} />
                              <span className="text-sm text-slate-200 font-medium truncate">{event.title}</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-slate-500 ml-4">
                              <CalendarIcon size={10} />
                              <span>{formatFullDate(event.date)}</span>
                              {event.time && (
                                <>
                                  <Clock size={10} />
                                  <span>{event.time}</span>
                                </>
                              )}
                            </div>
                            {event.location && (
                              <div className="flex items-center gap-1 text-xs text-slate-600 ml-4 mt-1">
                                <MapPin size={10} />
                                <span className="truncate">{event.location}</span>
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => deleteEvent(event.id)}
                            className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-white/10 rounded-lg transition-all"
                          >
                            <X size={12} className="text-slate-500" />
                          </button>
                        </div>
                        {daysUntil >= 0 && (
                          <div className="ml-4 mt-2 flex items-center gap-2">
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              daysUntil === 0 ? "bg-emerald-500/20 text-emerald-400" :
                              daysUntil === 1 ? "bg-amber-500/20 text-amber-400" :
                              "bg-cyan-500/10 text-cyan-400"
                            }`}>
                              {daysUntil === 0 ? "Today" : daysUntil === 1 ? "Tomorrow" : `${daysUntil} days`}
                            </span>
                          </div>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-white/5">
              <button
                onClick={() => setIsAdding(true)}
                className="w-full px-4 py-2.5 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-all flex items-center justify-center gap-2"
              >
                <Plus size={14} /> Add New Event
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}