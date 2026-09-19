import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: 'MEMORA',
    version: '1.0.0',
    demo_mode: true
  });
}
