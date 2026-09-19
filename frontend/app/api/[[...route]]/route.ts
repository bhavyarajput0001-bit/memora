/**
 * MEMORA Backend API Routes for Vercel Serverless
 * This replaces the Python backend for Vercel deployment
 */

import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

// In-memory storage (use SQLite for persistence)
interface MemoryStore {
  chunks: Array<{id: string, text: string, metadata: any, embedding?: number[]}>;
  entities: Array<{id: string, name: string, type: string, aliases: string[]}>;
  documents: Array<{id: string, filename: string, content: string}>;
}

const store: MemoryStore = {
  chunks: [],
  entities: [],
  documents: [],
};

// Simple TF-IDF implementation
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

// Simple embedding simulation (no external model needed)
function simpleEmbed(text: string): number[] {
  const tokens = tokenize(text);
  const vec = new Array(64).fill(0);
  for (let i = 0; i < tokens.length; i++) {
    const hash = tokens[i].split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    vec[hash % 64] += 1;
  }
  // Normalize
  const norm = Math.sqrt(vec.reduce((a, b) => a + b * b, 0));
  if (norm > 0) return vec.map(v => v / norm);
  return vec;
}

function cosineSimilarity(a: number[], b: number[]): number {
  const dot = a.reduce((sum, v, i) => sum + v * (b[i] || 0), 0);
  const normA = Math.sqrt(a.reduce((sum, v) => sum + v * v, 0));
  const normB = Math.sqrt(b.reduce((sum, v) => sum + v * v, 0));
  return normB === 0 ? 0 : dot / (normA * normB);
}

// API Route Handler
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, limit = 5 } = body;
    
    if (!query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }
    
    // Search chunks
    const scored = store.chunks.map(chunk => ({
      ...chunk,
      score: tfidfScore(query, chunk.text) + 
             (chunk.embedding ? cosineSimilarity(
               simpleEmbed(query),
               chunk.embedding
             ) * 0.5 : 0)
    })).filter(c => c.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
    
    // Get entities
    const entityMatches = store.entities.filter(e =>
      e.name.toLowerCase().includes(query.toLowerCase()) ||
      e.aliases.some(a => a.toLowerCase().includes(query.toLowerCase()))
    );
    
    const answer = scored.length > 0 
      ? `Found ${scored.length} relevant memories. Top matches: ${scored.slice(0, 3).map(s => s.text.substring(0, 100)).join(', ')}`
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
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action');
  
  try {
    switch (action) {
      case 'health':
        return NextResponse.json({
          status: 'healthy',
          service: 'MEMORA',
          version: '1.0.0',
          demo_mode: true
        });
      
      case 'stats':
        return NextResponse.json({
          chunks: store.chunks.length,
          entities: store.entities.length,
          documents: store.documents.length
        });
      
      case 'entities':
        return NextResponse.json(store.entities);
      
      case 'documents':
        return NextResponse.json(store.documents);
      
      default:
        return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
    }
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// Export types
export type { MemoryStore };