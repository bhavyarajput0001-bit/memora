"use client";

import { useState, useEffect } from "react";
import { 
  Calendar as CalendarIcon, 
  Plus, 
  Clock, 
  MapPin,
  CheckCircle,
  X,
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

export default function CalendarSidebar() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: "",
    date: "",
    time: "",
    location: "",
    description: "",
  });

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
    loadEvents();
  }, []);

  const addEvent = () => {
    if (!newEvent.title || !newEvent.date) return;
    
    const event: CalendarEvent = {
      id: Date.now().toString(),
      ...newEvent,
      source: "manual",
    };
    
    setEvents([event, ...events]);
    setNewEvent({ title: "", date: "", time: "", location: "", description: "" });
    setShowAddModal(false);

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

  return (
    <>
      {/* Floating Calendar Button */}
      <button
        onClick={() => setShowAddModal(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-cyan-500 hover:bg-cyan-400 text-white rounded-full shadow-lg shadow-cyan-500/30 flex items-center justify-center transition-all hover:scale-110 z-50"
      >
        <Plus size={24} />
      </button>

      {/* Calendar Modal */}
      <AnimatePresence>
        {showAddModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-card w-full max-w-md p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">Add Event</h2>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X size={18} className="text-slate-400" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-1.5">Title *</label>
                  <input
                    type="text"
                    value={newEvent.title}
                    onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                    placeholder="Meeting with team..."
                    className="w-full px-4 py-2.5 bg-[#0a0f1e]/60 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-1.5">Date *</label>
                    <input
                      type="date"
                      value={newEvent.date}
                      onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                      className="w-full px-4 py-2.5 bg-[#0a0f1e]/60 border border-white/10 rounded-xl text-sm text-slate-200 outline-none focus:border-cyan-500/50 transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-1.5">Time</label>
                    <input
                      type="time"
                      value={newEvent.time}
                      onChange={(e) => setNewEvent({ ...newEvent, time: e.target.value })}
                      className="w-full px-4 py-2.5 bg-[#0a0f1e]/60 border border-white/10 rounded-xl text-sm text-slate-200 outline-none focus:border-cyan-500/50 transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-1.5">Location</label>
                  <input
                    type="text"
                    value={newEvent.location}
                    onChange={(e) => setNewEvent({ ...newEvent, location: e.target.value })}
                    placeholder="Office, Zoom, etc."
                    className="w-full px-4 py-2.5 bg-[#0a0f1e]/60 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-1.5">Description</label>
                  <textarea
                    value={newEvent.description}
                    onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                    placeholder="Additional details..."
                    rows={3}
                    className="w-full px-4 py-2.5 bg-[#0a0f1e]/60 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors resize-none"
                  />
                </div>
              </div>

              <div className="flex items-center gap-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 text-slate-400 rounded-xl text-sm font-medium hover:bg-white/10 hover:text-slate-200 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={addEvent}
                  disabled={!newEvent.title || !newEvent.date}
                  className="flex-1 px-4 py-2.5 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Add Event
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Events List in Sidebar */}
      <div className="fixed bottom-24 right-6 w-80 glass-card p-4 z-40 max-h-96 overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-white text-sm">Upcoming Events</h3>
          <button
            onClick={() => setShowAddModal(true)}
            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
          >
            <Plus size={14} className="text-slate-400" />
          </button>
        </div>

        {events.length === 0 ? (
          <div className="text-center py-8">
            <CalendarIcon size={32} className="mx-auto text-slate-700 mb-2" />
            <p className="text-xs text-slate-500">No events yet</p>
            <p className="text-xs text-slate-600 mt-1">Add your first event</p>
          </div>
        ) : (
          <div className="space-y-2">
            {events.slice(0, 5).map((event) => {
              const daysUntil = getDaysUntil(event.date);
              return (
                <div
                  key={event.id}
                  className="p-3 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-all group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-slate-200 font-medium truncate">{event.title}</div>
                      <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                        <Clock size={10} />
                        <span>{formatDate(event.date)}</span>
                        {event.time && (
                          <>
                            <span>•</span>
                            <span>{event.time}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => deleteEvent(event.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-all"
                    >
                      <X size={12} className="text-slate-500" />
                    </button>
                  </div>
                  {daysUntil >= 0 && daysUntil <= 7 && (
                    <div className="mt-2 text-xs text-cyan-400">
                      {daysUntil === 0 ? "Today" : `${daysUntil} day${daysUntil > 1 ? 's' : ''} left`}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}