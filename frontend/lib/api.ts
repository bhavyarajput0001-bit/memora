// MEMORA Frontend API Client
// Provides types and async API methods for development and Vercel SSR build.
//
// The frontend ships its own lightweight API layer so the Vercel deployment
// is self-contained. When paired with a live Render backend, set
// NEXT_PUBLIC_API_BASE_URL and the same methods (or a real client) should be used.

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export interface Conflict {
  id: string;
  type: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  detectedAt: string; // ISO timestamp
  resolvedAt?: string;
  entitiesInvolved: string[];
}

export interface MemoryFact {
  id: string;
  content: string;
  sourceId: string;
  confidence: number; // 0 - 1
  timestamp: string; // ISO timestamp
  entities: string[];
  categories?: string[];
}

export interface Source {
  id: string;
  type: 'pdf' | 'image' | 'email' | 'calendar' | 'note' | 'web' | 'other';
  name: string;
  filename?: string;
  url?: string;
  uploadedAt: string; // ISO timestamp
  processed: boolean;
  chunkCount?: number;
}

export interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  startTime?: string;
  endTime?: string;
  location?: string;
  description?: string;
  color?: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || '';

function buildUrl(path: string): string {
  return API_BASE ? `${API_BASE}${path}` : `/api${path}`;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<{ success: boolean; data: T; error?: string }> {
  try {
    const res = await fetch(buildUrl(path), {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
      throw new Error(error.error || `HTTP ${res.status}`);
    }
    const json = await res.json();
    return { success: true, data: json } as { success: boolean; data: T };
  } catch (error: any) {
    // Graceful fallback during static generation / SSR — return empty results
    return { success: false, error: error?.message || 'Network error', data: {} as T };
  }
}

async function requestPost<T>(path: string, body: any): Promise<{ success: boolean; data: T; error?: string }> {
  try {
    const res = await fetch(buildUrl(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
      throw new Error(error.error || `HTTP ${res.status}`);
    }
    const json = await res.json();
    return { success: true, data: json } as { success: boolean; data: T };
  } catch (error: any) {
    return { success: false, error: error?.message || 'Network error', data: {} as T };
  }
}

async function requestPut<T>(path: string, body: any): Promise<{ success: boolean; data: T; error?: string }> {
  try {
    const res = await fetch(buildUrl(path), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
      throw new Error(error.error || `HTTP ${res.status}`);
    }
    const json = await res.json();
    return { success: true, data: json } as { success: boolean; data: T };
  } catch (error: any) {
    return { success: false, error: error?.message || 'Network error', data: {} as T };
  }
}

async function requestDelete<T>(path: string): Promise<{ success: boolean; error?: string }> {
  try {
    const res = await fetch(buildUrl(path), {
      method: 'DELETE',
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
      throw new Error(error.error || `HTTP ${res.status}`);
    }
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error?.message || 'Network error' };
  }
}

// ---------------------------------------------------------------------------
// API client
// ---------------------------------------------------------------------------
const api = {
  // Memory stats
  getMemoryStats: () =>
    request<{ total_facts: number; total_entities: number; total_documents: number; recent_facts: any[] }>('?action=stats'),

  // Timeline
  getTimeline: (days: number = 30) =>
    request<{ events: Array<{ id: string; title: string; date: string; type: string; start_at?: string; time?: string; location?: string; description?: string }> }>(
      `/v1/timeline?days=${days}`
    ),

  // Events CRUD
  createEvent: (event: Partial<CalendarEvent>) =>
    requestPost('/v1/events', event),

  updateEvent: (id: string, event: Partial<CalendarEvent>) =>
    requestPut(`/v1/events/${id}`, event),

  deleteEvent: (id: string) =>
    requestDelete(`/v1/events/${id}`),

  // Conflicts
  getConflicts: () =>
    request<{ conflicts: Conflict[] }>('/v1/conflicts'),

  // Facts
  getFacts: () =>
    request<{ facts: MemoryFact[] }>('/v1/memory/facts'),

  // Entities
  getEntities: () =>
    request<{ entities: Array<{ id: string; name: string; type: string; aliases: string[] }> }>(
      '?action=entities'
    ),

  // Sources
  getSources: () =>
    request<{ sources: Source[] }>('/v1/sources'),

  // Graph
  getGraph: () =>
    request<{ nodes: GraphNode[]; links: GraphLink[] }>('/v1/memory/graph'),

  // Dashboard (consolidated)
  getDashboardData: () =>
    request<{
      stats?: { total_facts: number; total_entities: number; total_documents: number; recent_facts: any[] };
      activities?: any[];
      conflicts?: Conflict[];
    }>('/v1/dashboard'),
};

export { api };
export type { Conflict, MemoryFact, Source, CalendarEvent };