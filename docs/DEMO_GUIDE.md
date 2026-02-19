# Demo Guide - Meeting Minutes Generator

This guide helps you demo the Meeting Minutes Generator with sample data.

## Quick Demo (5 minutes)

### Option 1: Using Sample JSON (No Audio Required)

If you don't have an audio file, you can import a pre-generated transcript:

```python
from src.schemas import Meeting, TranscriptSegment, MeetingMinutes, ActionItem
from src.storage import MeetingStorage
from datetime import datetime

# Create sample meeting
transcript = [
    TranscriptSegment(start=0.0, end=5.0, text="Good morning everyone, let's start our weekly sync.", speaker="John Smith"),
    TranscriptSegment(start=5.0, end=12.0, text="Thanks John. I have an update on the Q1 project. We've completed 80% of the deliverables.", speaker="Sarah Johnson"),
    TranscriptSegment(start=12.0, end=18.0, text="That's excellent progress. What about the remaining 20%?", speaker="John Smith"),
    TranscriptSegment(start=18.0, end=25.0, text="We're on track to complete everything by end of month. However, we need approval for the extra budget.", speaker="Sarah Johnson"),
    TranscriptSegment(start=25.0, end=30.0, text="Let's discuss the budget. Bob, can you prepare a proposal?", speaker="John Smith"),
    TranscriptSegment(start=30.0, end=35.0, text="Sure, I'll have it ready by Friday.", speaker="Bob Wilson"),
]

minutes = MeetingMinutes(
    summary=[
        "Q1 project is 80% complete and on track",
        "Additional budget required for project completion",
        "Team coordination is working well"
    ],
    decisions=[
        "Approved proceeding with current project timeline",
        "Budget proposal to be submitted by end of week"
    ],
    action_items=[
        ActionItem(owner="Bob Wilson", task="Prepare budget proposal", due_date="2026-02-21"),
        ActionItem(owner="Sarah Johnson", task="Complete remaining Q1 deliverables", due_date="2026-02-28")
    ],
    risks=[
        "Budget approval may take longer than expected",
        "Resource constraints in final week of month"
    ]
)

meeting = Meeting(
    title="Weekly Team Sync - Feb 2026",
    date=datetime(2026, 2, 18, 10, 0),
    participants=["John Smith", "Sarah Johnson", "Bob Wilson"],
    agenda="1. Q1 project update\n2. Budget discussion\n3. Next steps",
    transcript=transcript,
    minutes=minutes
)

# Save to database
storage = MeetingStorage()
meeting_id = storage.save_meeting(meeting)

print(f"Demo meeting saved with ID: {meeting_id}")
print("Now run: streamlit run app.py")
print("Go to History page to see the meeting!")
```

### Option 2: Using Real Audio

1. **Get a sample audio file**
   - Record a short meeting (2-5 minutes)
   - Use a YouTube video with meeting content
   - Use any MP3/WAV file with spoken content

2. **Run the app**
   ```bash
   streamlit run app.py
   ```

3. **Process the meeting**
   - Click "New Meeting"
   - Upload your audio file
   - Fill in meeting details
   - Wait for transcription (~1-2 min per minute of audio)
   - Review and edit the generated minutes
   - Export to DOCX or PDF

## Demo Script for Presentations

### Introduction (1 minute)
"I built a Meeting Minutes Generator that automates the tedious task of creating meeting documentation. Instead of manually taking notes, you can simply upload a recording and get professional minutes in minutes."

### Features Demo (3 minutes)

**1. Upload & Process**
- Show the upload interface
- Explain supported formats and file size limits
- Upload a pre-recorded meeting

**2. Transcription**
- Show the transcription progress
- Highlight the speaker diarization feature
- Point out confidence scores and timestamps

**3. AI-Powered Minutes**
- Show the generated executive summary
- Highlight automatically extracted action items
- Demonstrate the edit interface

**4. Professional Export**
- Export to both DOCX and PDF
- Open the documents to show formatting
- Emphasize the professional appearance

**5. Meeting History**
- Show the searchable history
- Demonstrate searching by title/participant
- Show how easy it is to re-export old meetings

### Technical Highlights (1 minute)
- "Uses OpenAI's Whisper for accurate transcription"
- "Speaker diarization with pyannote.audio"
- "LLM-powered summarization extracts key insights"
- "Privacy-first: all processing can be done locally"
- "Full Python stack with Streamlit UI"

### Use Cases
1. **Corporate Teams**: Reduce admin overhead for recurring meetings
2. **Project Management**: Track action items and decisions automatically
3. **Remote Work**: Ensure everyone has access to accurate meeting records
4. **Compliance**: Maintain searchable meeting archives
5. **Personal Productivity**: Never lose track of important discussions

## Sample Meeting Types

### 1. Sprint Planning
- Duration: 30-45 minutes
- Participants: 5-8 people
- Key content: User stories, estimates, commitments
- Action items: Task assignments, spike research

### 2. Client Kickoff
- Duration: 60 minutes
- Participants: 4-6 people
- Key content: Project scope, timeline, expectations
- Action items: Contract review, resource allocation

### 3. Board Meeting
- Duration: 90-120 minutes
- Participants: 6-10 people
- Key content: Financial review, strategic decisions
- Action items: Approvals, follow-up investigations

### 4. Standup/Sync
- Duration: 15 minutes
- Participants: 3-5 people
- Key content: Quick updates, blockers
- Action items: Immediate follow-ups

## Performance Expectations

| Audio Length | Transcription Time | Summarization Time | Total Time |
|--------------|-------------------|-------------------|-----------|
| 5 minutes    | 1-2 minutes       | 10-20 seconds     | ~2 minutes |
| 15 minutes   | 3-5 minutes       | 15-30 seconds     | ~5 minutes |
| 30 minutes   | 6-10 minutes      | 20-40 seconds     | ~10 minutes |
| 60 minutes   | 12-20 minutes     | 30-60 seconds     | ~20 minutes |

*Times based on "base" Whisper model on CPU. GPU is 5-10x faster.*

## Common Demo Questions & Answers

**Q: Can it distinguish between different speakers?**
A: Yes, it uses pyannote.audio for speaker diarization. You can also manually rename speakers in the UI.

**Q: What about privacy? Does audio get uploaded?**
A: In privacy mode (default), everything runs locally. Audio never leaves your machine. LLM summarization can also use local models.

**Q: What languages are supported?**
A: Whisper supports 99 languages. Currently, the UI is in English, but transcription works in multiple languages.

**Q: Can I edit the minutes before exporting?**
A: Yes! The entire transcript and all minutes sections are fully editable in the UI before export.

**Q: Does it work offline?**
A: Transcription works 100% offline. Summarization requires either an API key or local LLM setup.

**Q: What's the accuracy like?**
A: Whisper "base" model achieves 85-90% accuracy on clear audio. "large" model can reach 95%+ accuracy.

## Tips for Best Results

### Audio Quality
- Use good microphone (not phone speaker)
- Minimize background noise
- Clear speech at normal pace
- One person speaking at a time

### Meeting Structure
- Start with introductions (helps with speaker ID)
- Have a clear agenda
- Summarize key points and action items at the end
- Keep meetings focused (30-60 minutes ideal)

### Post-Processing
- Review low-confidence segments (marked in yellow/red)
- Correct speaker names for clarity
- Edit or add to the AI-generated summary
- Verify action items have clear owners and due dates

## Extending the Demo

### Integration Ideas
1. **Calendar Integration**: Auto-process scheduled meeting recordings
2. **Slack/Teams Bot**: Share minutes automatically after meetings
3. **Task Management**: Create Jira/Asana tickets from action items
4. **Email Reports**: Send formatted minutes to participants
5. **Analytics Dashboard**: Track action item completion rates

### Custom Features to Highlight
- Confidence scoring for quality control
- Searchable meeting history
- Flexible export formats
- Privacy-first architecture
- Extensible Python codebase

## Technical Setup for Demo

### Pre-Demo Checklist
- [ ] Install all dependencies
- [ ] Configure .env with API keys
- [ ] Test with a 2-minute sample audio
- [ ] Clear old demo data from database
- [ ] Open Streamlit in browser
- [ ] Have backup sample JSON ready
- [ ] Prepare DOCX/PDF samples to show

### Demo Environment
```bash
# Recommended setup
WHISPER_MODEL=base          # Fast enough, good quality
PRIVACY_MODE=false          # Allow API for summarization
LLM_PROVIDER=openai        # Most reliable
LLM_MODEL=gpt-4-turbo-preview
```

### Fallback Plan
If live demo fails:
1. Show pre-generated exports (keep DOCX/PDF samples)
2. Walk through code architecture
3. Show unit test results
4. Display sample JSON data

---

**Remember**: The goal is to showcase how this tool saves time and improves meeting productivity. Focus on the value proposition and end-to-end workflow!
