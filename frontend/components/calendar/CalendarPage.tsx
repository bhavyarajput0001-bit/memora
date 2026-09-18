"use client";

import { useState, useEffect } from "react";
import { X, Search, Database, Users, Calendar, TrendingUp, FileText, Loader2, ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { ReactNode } from "react";
import { api } from "@/lib/api";

type Category = "facts" | "people" | "events" | "relationships" | "sources";
type ViewMode = "month" | "week" | "day";

interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  startTime?: string;
  endTime?: string;
  location?: string;
  description?: string;
  color?: string;
}

const COLORS = ["#c5221f", "#188038", "#039be5", "#f1c40f", "#8e24aa", "#607d8b"];

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<ViewMode>("month");
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [showEventModal, setShowEventModal] = useState(false);
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null);
  const [formData, setFormData] = useState({
    title: "",
    date: "",
    startTime: "09:00",
    endTime: "10:00",
    location: "",
    description: "",
    color: COLORS[0],
  });
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [categoryItems, setCategoryItems] = useState<any[]>([]);
  const [categoryLoading, setCategoryLoading] = useState(false);
  const [categorySearch, setCategorySearch] = useState("");

  // Load events
  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const response = await api.getTimeline(90);
      if (response.success) {
        const loadedEvents = (response.data.events || []).map((e: any) => ({
          id: e.id,
          title: e.title || "Untitled Event",
          date: e.start_at || e.date,
          startTime: e.time || "",
          endTime: "",
          location: e.location || "",
          description: e.description || "",
          color: COLORS[Math.floor(Math.random() * COLORS.length)],
        }));
        setEvents(loadedEvents);
      }
    } catch (error) {
      console.error("Failed to load events:", error);
    }
  };

  const openNewEventModal = (date?: string) => {
    setEditingEvent(null);
    setFormData({
      title: "",
      date: date || currentDate.toISOString().split("T")[0],
      startTime: "09:00",
      endTime: "10:00",
      location: "",
      description: "",
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
    });
    setShowEventModal(true);
  };

  const openEditEventModal = (event: CalendarEvent) => {
    setEditingEvent(event);
    setFormData({
      title: event.title,
      date: event.date,
      startTime: event.startTime || "09:00",
      endTime: event.endTime || "10:00",
      location: event.location || "",
      description: event.description || "",
      color: event.color || COLORS[0],
    });
    setShowEventModal(true);
  };

  const saveEvent = async () => {
    if (!formData.title || !formData.date) return;

    try {
      const payload = {
        title: formData.title,
        date: formData.date,
        time: formData.startTime,
        location: formData.location,
        description: formData.description,
        color: formData.color,
      };

      if (editingEvent) {
        await fetch(`http://127.0.0.1:8000/api/v1/events/${editingEvent.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } else {
        await fetch("http://127.0.0.1:8000/api/v1/events", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      await loadEvents();
      setShowEventModal(false);
    } catch (error) {
      console.error("Failed to save event:", error);
    }
  };

  const deleteEvent = async (id: string) => {
    try {
      await fetch(`http://127.0.0.1:8000/api/v1/events/${id}`, {
        method: "DELETE",
      });
      setEvents(events.filter(e => e.id !== id));
      setShowEventModal(false);
    } catch (error) {
      console.error("Failed to delete event:", error);
    }
  };

  // Load category data
  const loadCategoryData = async (cat: Category) => {
    setSelectedCategory(cat);
    setCategoryLoading(true);
    try {
      let response;
      switch (cat) {
        case "facts":
          response = await api.getFacts();
          if (response.success) setCategoryItems(response.data.facts || []);
          break;
        case "people":
          response = await api.getEntities();
          if (response.success) setCategoryItems(response.data.entities || []);
          break;
        case "events":
          response = await api.getTimeline(30);
          if (response.success) setCategoryItems(response.data.events || []);
          break;
        case "sources":
          response = await api.getSources();
          if (response.success) setCategoryItems(response.data.sources || []);
          break;
        case "relationships":
          const factsResp = await api.getFacts();
          if (factsResp.success) {
            const rels = factsResp.data.facts?.filter((f: any) =>
              f.predicate?.includes("works_on") ||
              f.predicate?.includes("assigned_to") ||
              f.predicate?.includes("leads")
            ) || [];
            setCategoryItems(rels);
          }
          break;
      }
    } catch (error) {
      console.error(`Failed to load ${cat}:`, error);
    } finally {
      setCategoryLoading(false);
    }
  };

  const filteredItems = categoryItems.filter(item => {
    const searchStr = JSON.stringify(item).toLowerCase();
    return searchStr.includes(categorySearch.toLowerCase());
  });

  const categoryConfig: Record<Category, { label: string; icon: any; color: string }> = {
    facts: { label: "Facts", icon: Database, color: "cyan" },
    people: { label: "People", icon: Users, color: "emerald" },
    events: { label: "Events", icon: Calendar, color: "amber" },
    relationships: { label: "Relationships", icon: TrendingUp, color: "violet" },
    sources: { label: "Sources", icon: FileText, color: "slate" },
  };

  const colorMap: Record<string, string> = {
    cyan: "#06b6d4",
    emerald: "#10b981",
    amber: "#f59e0b",
    violet: "#8b5cf6",
    slate: "#64748b",
  };

  // Calendar helpers
  const getDaysInMonth = (date: Date) => new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  const getFirstDayOfMonth = (date: Date) => new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  const getEventsForDate = (dateStr: string) => events.filter(e => e.date === dateStr);
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const prevMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));

  const renderMonthView = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];

    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="h-28 bg-transparent" />);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      const dayEvents = getEventsForDate(dateStr);
      const isToday = dateStr === new Date().toISOString().split("T")[0];

      days.push(
        <div
          key={day}
          onClick={() => openNewEventModal(dateStr)}
          className="h-28 bg-white/5 border border-white/5 rounded-lg p-2 cursor-pointer hover:bg-white/10 transition-all group"
        >
          <div className="flex items-center justify-between mb-1">
            <span className={`text-sm font-medium w-7 h-7 rounded-full flex items-center justify-center ${
              isToday ? "bg-cyan-500 text-white" : "text-slate-400"
            }`}>
              {day}
            </span>
            <button
              onClick={(e) => { e.stopPropagation(); openNewEventModal(dateStr); }}
              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-all"
            >
              <Plus size={14} className="text-slate-400" />
            </button>
          </div>
          <div className="space-y-1 overflow-hidden mt-1">
            {dayEvents.slice(0, 2).map((event, i) => (
              <div
                key={i}
                onClick={(e) => { e.stopPropagation(); openEditEventModal(event); }}
                className="text-xs px-1.5 py-0.5 rounded truncate cursor-pointer hover:brightness-110"
                style={{ backgroundColor: `${event.color}30`, color: event.color }}
              >
                {event.startTime && <span className="opacity-75">{event.startTime} </span>}
                {event.title}
              </div>
            ))}
            {dayEvents.length > 2 && (
              <div className="text-xs text-slate-500 pl-1">+{dayEvents.length - 2} more</div>
            )}
          </div>
        </div>
      );
    }

    return days;
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Calendar</h1>
          <p className="text-slate-500 text-sm">{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-white/5 border border-white/10 rounded-xl p-1">
            {(["month", "week", "day"] as ViewMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  viewMode === mode ? "bg-cyan-500/20 text-cyan-400" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
          <button
            onClick={() => openNewEventModal()}
            className="flex items-center gap-2 px-4 py-2.5 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-all"
          >
            <Plus size={16} /> New Event
          </button>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button onClick={prevMonth} className="p-2 hover:bg-white/10 rounded-lg transition-all">
            <ChevronLeft size={20} className="text-slate-400" />
          </button>
          <button onClick={() => setCurrentDate(new Date())} className="px-3 py-1.5 text-sm text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-all">
            Today
          </button>
          <button onClick={nextMonth} className="p-2 hover:bg-white/10 rounded-lg transition-all">
            <ChevronRight size={20} className="text-slate-400" />
          </button>
        </div>
      </div>

      {/* Month Grid */}
      <div className="glass-card p-4">
        <div className="grid grid-cols-7 gap-2 mb-2">
          {dayNames.map((day) => (
            <div key={day} className="text-center text-xs font-medium text-slate-500 py-2">
              {day}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-2">
          {renderMonthView()}
        </div>
      </div>

      {/* Bottom Section: Memory Categories + Upcoming Events */}
      <div className="grid grid-cols-2 gap-6">
        {/* Memory Overview Categories */}
        <div className="glass-card p-5">
          <h3 className="font-semibold text-white mb-4">Memory Overview</h3>
          <div className="grid grid-cols-5 gap-2">
            {(Object.keys(categoryConfig) as Category[]).map((cat) => {
              const config = categoryConfig[cat];
              const Icon = config.icon;
              return (
                <button
                  key={cat}
                  onClick={() => loadCategoryData(cat)}
                  className="flex flex-col items-center gap-1 p-3 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 hover:bg-white/10 transition-all"
                >
                  <Icon size={20} className="text-slate-400" />
                  <span className="text-[10px] text-slate-500">{config.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Upcoming Events */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">Upcoming Events</h3>
            <button onClick={() => openNewEventModal()} className="p-1.5 hover:bg-white/10 rounded-lg transition-all">
              <Plus size={16} className="text-slate-400" />
            </button>
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {events.filter(e => new Date(e.date) >= new Date())
              .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
              .slice(0, 4)
              .map((event) => {
                const daysUntil = Math.ceil((new Date(event.date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
                return (
                  <div
                    key={event.id}
                    onClick={() => openEditEventModal(event)}
                    className="flex items-center gap-3 p-2.5 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 cursor-pointer transition-all"
                  >
                    <div className="w-1 h-8 rounded-full flex-shrink-0" style={{ backgroundColor: event.color }} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-200 font-medium truncate">{event.title}</p>
                      <p className="text-xs text-slate-500">
                        {new Date(event.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                        {event.startTime && ` • ${event.startTime}`}
                      </p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      daysUntil === 0 ? "bg-emerald-500/20 text-emerald-400" :
                      daysUntil === 1 ? "bg-amber-500/20 text-amber-400" :
                      "bg-cyan-500/10 text-cyan-400"
                    }`}>
                      {daysUntil === 0 ? "Today" : daysUntil === 1 ? "Tomorrow" : `${daysUntil}d`}
                    </span>
                  </div>
                );
              })}
            {events.filter(e => new Date(e.date) >= new Date()).length === 0 && (
              <div className="text-center py-6 text-slate-500">
                <p className="text-sm">No upcoming events</p>
                <button onClick={() => openNewEventModal()} className="mt-2 text-xs text-cyan-400 hover:text-cyan-300">
                  + Add event
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Event Modal */}
      <AnimatePresence>
        {showEventModal && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowEventModal(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md glass-card z-50"
            >
              <div className="p-5 border-b border-white/5 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">{editingEvent ? "Edit Event" : "New Event"}</h2>
                <button onClick={() => setShowEventModal(false)} className="p-1.5 hover:bg-white/10 rounded-lg transition-all">
                  <X size={18} className="text-slate-400" />
                </button>
              </div>
              <div className="p-5 space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-1.5">Title *</label>
                  <input type="text" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} placeholder="Event title..." className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors" autoFocus />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-1.5">Date *</label>
                    <input type="date" value={formData.date} onChange={(e) => setFormData({ ...formData, date: e.target.value })} className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 outline-none focus:border-cyan-500/50 transition-colors" />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-1.5">Color</label>
                    <div className="flex gap-2 mt-2">
                      {COLORS.map((color) => (
                        <button key={color} onClick={() => setFormData({ ...formData, color })} className={`w-6 h-6 rounded-full transition-all ${formData.color === color ? "ring-2 ring-white ring-offset-2 ring-offset-[#0a0f1e]" : ""}`} style={{ backgroundColor: color }} />
                      ))}
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-1.5">Start Time</label>
                    <input type="time" value={formData.startTime} onChange={(e) => setFormData({ ...formData, startTime: e.target.value })} className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 outline-none focus:border-cyan-500/50 transition-colors" />
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-1.5">End Time</label>
                    <input type="time" value={formData.endTime} onChange={(e) => setFormData({ ...formData, endTime: e.target.value })} className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 outline-none focus:border-cyan-500/50 transition-colors" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-1.5">Location</label>
                  <input type="text" value={formData.location} onChange={(e) => setFormData({ ...formData, location: e.target.value })} placeholder="Add location..." className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors" />
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-1.5">Description</label>
                  <textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} placeholder="Add description..." rows={3} className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors resize-none" />
                </div>
              </div>
              <div className="p-5 border-t border-white/5 flex items-center justify-between">
                {editingEvent ? (
                  <button onClick={() => deleteEvent(editingEvent.id)} className="flex items-center gap-2 px-3 py-2 text-rose-400 hover:bg-rose-500/10 rounded-xl transition-all text-sm">
                    <X size={14} /> Delete
                  </button>
                ) : <div />}
                <div className="flex items-center gap-3">
                  <button onClick={() => setShowEventModal(false)} className="px-4 py-2.5 bg-white/5 border border-white/10 text-slate-400 rounded-xl text-sm hover:bg-white/10 transition-all">Cancel</button>
                  <button onClick={saveEvent} disabled={!formData.title || !formData.date} className="px-4 py-2.5 bg-cyan-500/15 border border-cyan-500/20 text-cyan-400 rounded-xl text-sm font-medium hover:bg-cyan-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    {editingEvent ? "Save Changes" : "Create Event"}
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Category Detail Panel (slides from right) */}
      <AnimatePresence>
        {selectedCategory && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedCategory(null)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="fixed top-0 right-0 h-full w-96 glass-card z-50 flex flex-col border-l border-white/10"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-5 border-b border-white/5 flex-shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
                    {categoryConfig[selectedCategory].icon({ size: 20, className: "text-slate-400" } as any)}
                  </div>
                  <div>
                    <h2 className="font-semibold text-white text-lg">{categoryConfig[selectedCategory].label}</h2>
                    <p className="text-xs text-slate-500">{filteredItems.length} items</p>
                  </div>
                </div>
                <button onClick={() => setSelectedCategory(null)} className="p-2 hover:bg-white/10 rounded-xl transition-all">
                  <X size={18} className="text-slate-400" />
                </button>
              </div>

              {/* Search */}
              <div className="px-5 py-3 border-b border-white/5 flex-shrink-0">
                <div className="relative">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    value={categorySearch}
                    onChange={(e) => setCategorySearch(e.target.value)}
                    placeholder={`Search ${categoryConfig[selectedCategory].label.toLowerCase()}...`}
                    className="w-full pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-slate-200 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
                  />
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-4 scroll-smooth">
                {categoryLoading ? (
                  <div className="flex flex-col items-center justify-center h-40 gap-3">
                    <Loader2 size={28} className="text-cyan-500 animate-spin" />
                    <p className="text-slate-500 text-sm">Loading...</p>
                  </div>
                ) : filteredItems.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-40 text-center">
                    <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-3">
                      {categoryConfig[selectedCategory].icon({ size: 22, className: "text-slate-600" } as any)}
                    </div>
                    <p className="text-slate-400 font-medium text-sm">No items found</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {filteredItems.map((item, i) => (
                      <motion.div
                        key={item.id || i}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.03 }}
                        className="p-3 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-all"
                      >
                        {selectedCategory === "facts" && (
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400">{item.status || "confirmed"}</span>
                              <span className="text-xs text-slate-600">{(item.confidence * 100).toFixed(0)}%</span>
                            </div>
                            <p className="text-sm text-slate-200">{item.subject} <span className="text-cyan-400">{item.predicate}</span> {item.object}</p>
                          </div>
                        )}
                        {selectedCategory === "people" && (
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-emerald-500/15 border border-emerald-500/20 flex items-center justify-center">
                              <Users size={14} className="text-emerald-400" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-slate-200">{item.canonical_name}</p>
                              <p className="text-xs text-slate-500">{item.entity_type}</p>
                            </div>
                          </div>
                        )}
                        {selectedCategory === "events" && (
                          <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/20 flex items-center justify-center flex-shrink-0">
                              <Calendar size={14} className="text-amber-400" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-slate-200 truncate">{item.title}</p>
                              <p className="text-xs text-slate-500">{new Date(item.start_at).toLocaleDateString()}</p>
                            </div>
                          </div>
                        )}
                        {selectedCategory === "relationships" && (
                          <div className="flex items-center gap-2 text-sm">
                            <span className="text-slate-300">{item.subject}</span>
                            <span className="text-cyan-400">→</span>
                            <span className="text-slate-300">{item.object}</span>
                          </div>
                        )}
                        {selectedCategory === "sources" && (
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-violet-500/15 border border-violet-500/20 flex items-center justify-center flex-shrink-0">
                              <FileText size={14} className="text-violet-400" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-slate-200 truncate">{item.title || item.filename}</p>
                              <p className="text-xs text-slate-500">{item.source_type}</p>
                            </div>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}