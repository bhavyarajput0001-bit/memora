# MEMORA - Upload Feature Added

## New Feature: Upload/Connect Buttons

When you click on any of the buttons below the ask bar, a popup modal appears:

### PDF / Screenshot
- **Add File** button in center with drag & drop area
- Click to open file picker (Finder on macOS)
- Select files to upload
- Shows file list with size and name
- Upload progress indicator
- Success checkmark animation

### Email / Calendar / Notes
- **API Key Input** field
- Connect button to establish connection
- Secure connection indicator
- Success state when connected

## How It Works

1. Click any button: PDF, Screenshot, Email, Calendar, or Notes
2. Modal opens with appropriate UI for that type
3. For files: upload and process → auto-refresh stats
4. For connections: enter API key → connect → auto-refresh

## Auto-Refresh

When upload or connection completes:
- Memory stats update automatically (Facts, People, Events, Relationships, Sources)
- Recent Activity shows the new event
- Dashboard shows "Synced just now" status

## Files Added/Modified

- `components/dashboard/UploadModal.tsx` - Upload/Connect modal component
- `components/dashboard/Dashboard.tsx` - Added upload button handlers
- Backend already has endpoints: `/api/v1/ingest/file`, `/api/v1/ingest/text`

## Access

Dashboard: http://localhost:3001
- Click any button below the Ask bar to test upload modal