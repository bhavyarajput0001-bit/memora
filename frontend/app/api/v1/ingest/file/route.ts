import { NextRequest, NextResponse } from 'next/server';

/**
 * Serverless proxy for file ingestion.
 *
 * Forwards multipart uploads to the MEMORA backend (Render or local).
 * Set MEMORA_BACKEND_URL in the Vercel project env to point at the
 * FastAPI backend, e.g. https://memora-backend.onrender.com
 *
 * Returning a relative URL (no NEXT_PUBLIC_API_BASE_URL) keeps this
 * same-origin, so the browser CSP (connect-src 'self') allows it.
 */
const BACKEND = (process.env.MEMORA_BACKEND_URL || '').replace(/\/+$/, '');

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  if (!BACKEND) {
    return NextResponse.json(
      { success: false, error: 'Backend not configured (set MEMORA_BACKEND_URL)' },
      { status: 503 }
    );
  }

  try {
    const body = Buffer.from(await req.arrayBuffer());
    const res = await fetch(`${BACKEND}/api/v1/ingest/file`, {
      method: 'POST',
      headers: {
        'Content-Type': req.headers.get('content-type') || 'multipart/form-data',
      },
      body,
    });
    const json = await res.json().catch(() => ({}));
    return NextResponse.json(json, { status: res.status });
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: `Ingestion proxy failed: ${error?.message || 'unknown'}` },
      { status: 502 }
    );
  }
}
