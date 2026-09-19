import { NextRequest, NextResponse } from 'next/server';

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

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const action = url.searchParams.get('action');
  
  try {
    switch (action) {
      case 'stats':
        return NextResponse.json({
          chunks: store.chunks.length,
          entities: store.entities.length,
          documents: 0
        });
      
      case 'entities':
        return NextResponse.json(store.entities);
      
      case 'chunks':
        return NextResponse.json(store.chunks);
      
      default:
        return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
    }
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
