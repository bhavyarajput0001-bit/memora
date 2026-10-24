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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || '';

function buildUrl(path: string): string {
  return API_BASE ? `${API_BASE}${path}` : `/api${path}`;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<{ success: boolean; data: T }> {
  try {
    const res = await fetch(buildUrl(path), {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const json = await res.json();
    return { success: true, data: json } as { success: boolean; data: T };
  } catch (error) {
    // Graceful fallback during static generation / SSR — return empty results
    return { success: false, data: {} as T };
  }
}

// ---------------------------------------------------------------------------
// API client
// ---------------------------------------------------------------------------
const api = {
  // Memory stats
  getMemoryStats: () =>
    request<{ chunks: number; entities: number; documents: number }>('?action=stats'),

  // Timeline
  getTimeline: (days: number = 30) =>
    request<{ events: Array<{ id: string; title: string; date: string; type: string }> }>(
      `/v1/timeline?days=${days}`
    ),

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
};

export { api };
export type { Conflict, MemoryFact, Source };