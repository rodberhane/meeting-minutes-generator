"""Tests for data schemas."""

import pytest
from datetime import datetime
from src.schemas import (
    TranscriptSegment,
    ActionItem,
    MeetingMinutes,
    Meeting,
    ExportOptions
)


def test_transcript_segment_creation():
    """Test TranscriptSegment creation."""
    segment = TranscriptSegment(
        start=0.0,
        end=5.0,
        text="Hello world",
        speaker="Speaker 1",
        confidence=0.9
    )

    assert segment.start == 0.0
    assert segment.end == 5.0
    assert segment.text == "Hello world"
    assert segment.speaker == "Speaker 1"
    assert segment.confidence == 0.9


def test_transcript_segment_text_validation():
    """Test that empty text is rejected."""
    with pytest.raises(ValueError):
        TranscriptSegment(
            start=0.0,
            end=5.0,
            text="",
            speaker="Speaker 1"
        )


def test_action_item_creation():
    """Test ActionItem creation."""
    item = ActionItem(
        owner="John Doe",
        task="Review documentation",
        due_date="2026-02-20",
        confidence=0.95,
        status="Open"
    )

    assert item.owner == "John Doe"
    assert item.task == "Review documentation"
    assert item.due_date == "2026-02-20"
    assert item.confidence == 0.95
    assert item.status == "Open"


def test_action_item_defaults():
    """Test ActionItem default values."""
    item = ActionItem(
        owner="Jane Smith",
        task="Update slides"
    )

    assert item.due_date is None
    assert item.confidence == 1.0
    assert item.status == "Open"


def test_meeting_minutes_creation():
    """Test MeetingMinutes creation."""
    action_items = [
        ActionItem(owner="Alice", task="Task 1"),
        ActionItem(owner="Bob", task="Task 2")
    ]

    minutes = MeetingMinutes(
        summary=["Point 1", "Point 2", "Point 3"],
        decisions=["Decision 1"],
        action_items=action_items,
        risks=["Risk 1"],
        notes="Additional notes"
    )

    assert len(minutes.summary) == 3
    assert len(minutes.decisions) == 1
    assert len(minutes.action_items) == 2
    assert len(minutes.risks) == 1
    assert minutes.notes == "Additional notes"


def test_meeting_minutes_summary_max_length():
    """Test that summary is truncated to 8 items."""
    minutes = MeetingMinutes(
        summary=[f"Point {i}" for i in range(10)]
    )

    assert len(minutes.summary) == 8


def test_meeting_creation():
    """Test Meeting creation."""
    meeting = Meeting(
        title="Weekly Sync",
        date=datetime(2026, 2, 18, 10, 0),
        participants=["Alice", "Bob"],
        agenda="Discuss project updates"
    )

    assert meeting.title == "Weekly Sync"
    assert meeting.date == datetime(2026, 2, 18, 10, 0)
    assert len(meeting.participants) == 2
    assert meeting.agenda == "Discuss project updates"
    assert meeting.transcript == []
    assert meeting.minutes is None


def test_export_options_validation():
    """Test ExportOptions validation."""
    options = ExportOptions(
        format="docx",
        include_transcript=True,
        include_timestamps=True,
        include_speaker_labels=True
    )

    assert options.format == "docx"
    assert options.include_transcript is True


def test_export_options_format_validation():
    """Test that invalid format is rejected."""
    with pytest.raises(ValueError):
        ExportOptions(
            format="invalid",
            include_transcript=True
        )
