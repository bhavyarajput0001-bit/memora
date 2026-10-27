import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// Input validation schemas
const TimelineQuerySchema = z.object({
  days: z.string().regex(/^\d+$/).optional().default('30').transform(Number),
});

const EventBodySchema = z.object({
  title: z.string().min(1).max(255),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  time: z.string().optional(),
  location: z.string().max(500).optional(),
  description: z.string().max(5000).optional(),
  color: z.string().optional(),
});

// Mock data store
const events = [
  { id: '1', title: 'Project Meeting', date: '2026-10-25', time: '10:00', description: 'Weekly sync' },
  { id: '2', title: 'Demo Day', date: '2026-10-30', time: '14:00', description: 'Product demo' },
];

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const daysParam = url.searchParams.get('days');
  
  try {
    // Validate query parameters
    const query = TimelineQuerySchema.safeParse({ days: daysParam });
    if (!query.success) {
      return NextResponse.json(
        { error: 'Invalid query parameters', details: query.error.errors },
        { status: 400 }
      );
    }

    const days = query.data.days;
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    const filteredEvents = events.filter(e => new Date(e.date) >= cutoffDate);

    return NextResponse.json({
      success: true,
      data: {
        events: filteredEvents,
        total: filteredEvents.length,
        daysRequested: days
      }
    });
  } catch (error) {
    console.error('Timeline API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate request body
    const parsed = EventBodySchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid event data', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const newEvent = {
      id: Date.now().toString(),
      ...parsed.data,
      createdAt: new Date().toISOString(),
    };

    events.push(newEvent);

    return NextResponse.json(
      { success: true, data: newEvent },
      { status: 201 }
    );
  } catch (error) {
    console.error('Create event error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const eventId = url.pathname.split('/').pop();
    
    if (!eventId) {
      return NextResponse.json(
        { error: 'Event ID is required' },
        { status: 400 }
      );
    }

    const body = await request.json();
    const parsed = EventBodySchema.safeParse(body);
    
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid event data', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const eventIndex = events.findIndex(e => e.id === eventId);
    if (eventIndex === -1) {
      return NextResponse.json(
        { error: 'Event not found' },
        { status: 404 }
      );
    }

    events[eventIndex] = {
      ...events[eventIndex],
      ...parsed.data,
      updatedAt: new Date().toISOString(),
    };

    return NextResponse.json({ success: true, data: events[eventIndex] });
  } catch (error) {
    console.error('Update event error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const eventId = url.pathname.split('/').pop();
    
    if (!eventId) {
      return NextResponse.json(
        { error: 'Event ID is required' },
        { status: 400 }
      );
    }

    const eventIndex = events.findIndex(e => e.id === eventId);
    if (eventIndex === -1) {
      return NextResponse.json(
        { error: 'Event not found' },
        { status: 404 }
      );
    }

    events.splice(eventIndex, 1);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Delete event error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}