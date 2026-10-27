import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// Consolidated dashboard data endpoint
// Reduces multiple API calls to a single request

const DashboardDataSchema = z.object({
  includeStats: z.boolean().optional().default(true),
  includeActivities: z.boolean().optional().default(true),
  includeConflicts: z.boolean().optional().default(true),
  activityDays: z.number().optional().default(7),
  conflictLimit: z.number().optional().default(3),
});

// Mock data stores
const mockStats = {
  total_facts: 42,
  total_entities: 18,
  total_documents: 12,
  recent_facts: [
    { id: '1', content: 'Project deadline moved', timestamp: '2026-10-24T10:00:00Z' },
    { id: '2', content: 'New team member added', timestamp: '2026-10-23T15:30:00Z' },
  ]
};

const mockEvents = [
  { id: '1', title: 'Team Meeting', date: '2026-10-25', type: 'meeting' },
  { id: '2', title: 'Project Deadline', date: '2026-10-30', type: 'deadline' },
];

const mockConflicts = [
  { id: '1', subject: 'Project Atlas', predicate: 'deadline', value_a: 'Sep 24', value_b: 'Sep 26', severity: 'high' },
];

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const includeStats = url.searchParams.get('stats') !== 'false';
  const includeActivities = url.searchParams.get('activities') !== 'false';
  const includeConflicts = url.searchParams.get('conflicts') !== 'false';
  const activityDays = parseInt(url.searchParams.get('days') || '7');
  const conflictLimit = parseInt(url.searchParams.get('limit') || '3');

  try {
    const result: any = {};

    // Fetch stats if requested
    if (includeStats) {
      result.stats = mockStats;
    }

    // Fetch activities if requested
    if (includeActivities) {
      result.activities = mockEvents
        .filter(e => new Date(e.date) > new Date(Date.now() - activityDays * 24 * 60 * 60 * 1000))
        .slice(0, 5);
    }

    // Fetch conflicts if requested
    if (includeConflicts) {
      result.conflicts = mockConflicts.slice(0, conflictLimit);
    }

    return NextResponse.json({
      success: true,
      data: result,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Dashboard API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}