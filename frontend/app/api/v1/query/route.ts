import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// Input validation schema
const QuerySchema = z.object({
  query: z.string().min(1).max(1000),
  limit: z.number().int().min(1).max(50).optional().default(5),
});

interface MemoryChunk {
  id: string;
  text: string;
  metadata: any;
}

interface MemoryEntity {
  id: string;
  name: string;
  type: string;
  aliases: string[];
}

const store = {
  chunks: [] as MemoryChunk[],
  entities: [] as MemoryEntity[],
};

function tokenize(text: string): string[] {
  return text.toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(t => t.length > 1);
}

function tfidfScore(query: string, document: string): number {
  const queryTokens = tokenize(query);
  const docTokens = tokenize(document);
  if (queryTokens.length === 0 || docTokens.length === 0) return 0;

  const docSet = new Set(docTokens);
  let score = 0;
  for (const token of queryTokens) {
    if (docSet.has(token)) score += 1;
  }
  return score / Math.max(queryTokens.length, 1);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate input with Zod
    const parsed = QuerySchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        {
          error: 'Invalid query parameters',
          details: parsed.error.flatten()
        },
        { status: 400 }
      );
    }

    const { query, limit } = parsed.data;

    const scored = store.chunks
      .map(chunk => ({ ...chunk, score: tfidfScore(query, chunk.text) }))
      .filter(c => c.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    const entityMatches = store.entities.filter(e =>
      e.name.toLowerCase().includes(query.toLowerCase()) ||
      e.aliases.some(a => a.toLowerCase().includes(query.toLowerCase()))
    );

    const answer = scored.length > 0
      ? `Found ${scored.length} relevant memories.`
      : 'No relevant memories found.';

    return NextResponse.json({
      query,
      answer,
      sources: scored.map(s => ({
        id: s.id,
        filename: s.metadata?.filename || 'unknown',
        score: s.score,
        text: s.text.substring(0, 200)
      })),
      entities: entityMatches,
      confidence: scored.length > 0 ? Math.min(0.9, 0.5 + scored[0].score * 0.5) : 0.1
    });

  } catch (error) {
    console.error('Query API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export { store };