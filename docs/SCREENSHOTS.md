# Screenshots & UI Guide

## Application Interface

### 1. Home Page
![Home Page](screenshots/home.png)
*Main dashboard showing features, statistics, and quick start guide*

**Key Elements:**
- Feature highlights (transcription, diarization, export)
- Privacy information
- Quick start guide
- Meeting statistics
- Create meeting button

### 2. New Meeting - Upload Stage
![Upload Stage](screenshots/upload.png)
*Meeting information and audio upload interface*

**Features:**
- Meeting metadata form (title, date, participants, agenda)
- Audio file upload with format validation
- File size and format indicators
- Progress indicators showing current stage

### 3. New Meeting - Transcription Stage
![Transcription Stage](screenshots/transcribe.png)
*Real-time transcription with speaker identification*

**Shows:**
- Transcription progress indicator
- Live transcript preview with timestamps
- Speaker labels (Speaker 1, Speaker 2, etc.)
- Confidence indicators (🟢 high, 🟡 medium, 🔴 low)
- Speaker name editing interface
- Transcription options (model selection, language, number of speakers)

### 4. New Meeting - Minutes Stage
![Minutes Stage](screenshots/minutes.png)
*AI-generated meeting minutes with editing capability*

**Sections:**
- Executive Summary (editable text area)
- Key Decisions (editable list)
- Action Items (editable table with owner, task, due date)
- Risks & Open Questions (editable list)
- Add/remove action items dynamically

### 5. Export Stage
![Export Stage](screenshots/export.png)
*Document generation and download*

**Options:**
- Include/exclude full transcript
- Include/exclude timestamps
- Include/exclude speaker labels
- Export to DOCX or PDF
- Direct download buttons

### 6. Meeting History
![History Page](screenshots/history.png)
*Searchable archive of all meetings*

**Features:**
- Search by title or participant name
- Meeting cards with summary preview
- Quick export buttons (DOCX/PDF)
- Delete meeting option
- Meeting metadata display

### 7. Settings Page
![Settings Page](screenshots/settings.png)
*Configuration and system information*

**Settings:**
- Privacy mode toggle
- Whisper model selection
- LLM provider configuration
- API key management
- Audio retention settings
- System status indicators

## Document Outputs

### 8. DOCX Export Sample
![DOCX Sample](screenshots/export_docx.png)
*Professional Word document with formatted tables*

**Structure:**
- Meeting Minutes header (centered)
- Metadata table (title, date, participants, agenda)
- Executive Summary (bullets)
- Key Decisions (bullets)
- Action Items (formatted table)
- Risks & Open Questions (bullets)
- Full transcript (optional)
- Footer with generation timestamp

### 9. PDF Export Sample
![PDF Sample](screenshots/export_pdf.png)
*Professionally formatted PDF document*

**Features:**
- Consistent typography and spacing
- Color-coded section headers
- Formatted tables with styling
- Page breaks where appropriate
- Footer with disclaimer

## Workflow Visualization

### Complete Process Flow
```
┌─────────────┐
│   Upload    │  Enter meeting details + audio file
│   Audio     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Transcribe  │  Whisper AI converts speech to text
│   + Diarize │  Identify and label speakers
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generate   │  LLM extracts summary, decisions,
│   Minutes   │  action items, and risks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Review &    │  Human reviews and edits minutes
│    Edit     │  Correct any errors or omissions
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Export    │  Generate DOCX/PDF documents
│  & Share    │  Download or share
└─────────────┘
```

## UI Components Showcase

### Progress Indicators
```
✅ Upload    ⏳ Transcribe    ⚪ Minutes    ⚪ Export
```

### Confidence Indicators
- 🟢 High confidence (>0.8)
- 🟡 Medium confidence (0.5-0.8)
- 🔴 Low confidence (<0.5)

### Speaker Labels
```
[00:12] Speaker 1
  Good morning everyone, let's get started.

[00:18] Speaker 2
  Thanks for joining. I have an update on the project.
```

### Action Items Table
| Owner | Action | Due Date | Status |
|-------|--------|----------|--------|
| John Smith | Prepare budget proposal | 2026-02-21 | Open |
| Sarah Lee | Review architecture doc | 2026-02-25 | Open |

## Color Scheme

### Primary Colors
- **Blue (#0066cc)**: Headers, primary buttons, links
- **Gray (#666666)**: Secondary text
- **Light Gray (#f0f2f6)**: Background panels
- **Green (#00cc00)**: Success states, high confidence
- **Yellow (#ffcc00)**: Warnings, medium confidence
- **Red (#cc0000)**: Errors, low confidence

### Dark Theme
- Background: #1a1a1a
- Text: #ffffff
- Accent: #4d94ff

## Responsive Design

### Desktop View (1920x1080)
- Three-column layout for features
- Sidebar navigation always visible
- Wide content area for transcript viewing

### Tablet View (768x1024)
- Two-column layout
- Collapsible sidebar
- Adjusted spacing and font sizes

### Mobile View (375x667)
- Single column layout
- Hamburger menu for navigation
- Stacked UI elements
- Touch-optimized buttons

## Accessibility Features

- ✅ ARIA labels on all interactive elements
- ✅ Keyboard navigation support
- ✅ High contrast mode compatible
- ✅ Screen reader friendly
- ✅ Semantic HTML structure
- ✅ Focus indicators on buttons and inputs

## User Experience Highlights

### Progressive Disclosure
- Collapsible sections for long content
- Expandable transcript preview
- Optional advanced settings

### Immediate Feedback
- Loading spinners during processing
- Success/error toast notifications
- Real-time validation messages
- Progress percentages

### Error Handling
- Clear error messages with solutions
- Fallback options when features fail
- Graceful degradation

---

**Note**: Actual screenshots will be added after the first run of the application. To generate screenshots:

1. Run `streamlit run app.py`
2. Navigate through all pages
3. Take screenshots at key stages
4. Save to `docs/screenshots/` directory
5. Update this file with actual image references

For demo purposes, you can use the application walkthrough described above.
