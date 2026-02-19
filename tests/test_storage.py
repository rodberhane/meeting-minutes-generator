"""Tests for storage module."""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from src.storage import MeetingStorage
from src.schemas import Meeting, TranscriptSegment, MeetingMinutes, ActionItem


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test.db"

    yield db_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def storage(temp_db):
    """Create storage instance with temp database."""
    return MeetingStorage(db_path=temp_db)


@pytest.fixture
def sample_meeting():
    """Create a sample meeting."""
    transcript = [
        TranscriptSegment(
            start=0.0,
            end=5.0,
            text="Hello everyone",
            speaker="Speaker 1"
        ),
        TranscriptSegment(
            start=5.0,
            end=10.0,
            text="Hi there",
            speaker="Speaker 2"
        )
    ]

    minutes = MeetingMinutes(
        summary=["Discussed project status", "Reviewed timeline"],
        decisions=["Move forward with Plan A"],
        action_items=[
            ActionItem(owner="Alice", task="Complete report", due_date="2026-02-20")
        ],
        risks=["Potential delay in Q2"]
    )

    return Meeting(
        title="Team Sync",
        date=datetime(2026, 2, 18, 10, 0),
        participants=["Alice", "Bob", "Charlie"],
        agenda="Project updates",
        transcript=transcript,
        minutes=minutes
    )


def test_save_meeting(storage, sample_meeting):
    """Test saving a meeting."""
    meeting_id = storage.save_meeting(sample_meeting)

    assert meeting_id is not None
    assert meeting_id > 0


def test_get_meeting(storage, sample_meeting):
    """Test retrieving a meeting."""
    meeting_id = storage.save_meeting(sample_meeting)

    retrieved = storage.get_meeting(meeting_id)

    assert retrieved is not None
    assert retrieved.title == sample_meeting.title
    assert retrieved.date == sample_meeting.date
    assert len(retrieved.participants) == 3
    assert len(retrieved.transcript) == 2
    assert retrieved.minutes is not None
    assert len(retrieved.minutes.summary) == 2


def test_list_meetings(storage, sample_meeting):
    """Test listing meetings."""
    # Save multiple meetings
    storage.save_meeting(sample_meeting)

    meeting2 = sample_meeting.model_copy()
    meeting2.title = "Sprint Planning"
    storage.save_meeting(meeting2)

    # List all
    meetings = storage.list_meetings()

    assert len(meetings) == 2


def test_search_meetings(storage, sample_meeting):
    """Test searching meetings."""
    storage.save_meeting(sample_meeting)

    meeting2 = sample_meeting.model_copy()
    meeting2.title = "Sprint Planning"
    storage.save_meeting(meeting2)

    # Search by title
    results = storage.list_meetings(search="Sprint")

    assert len(results) == 1
    assert results[0].title == "Sprint Planning"


def test_delete_meeting(storage, sample_meeting):
    """Test deleting a meeting."""
    meeting_id = storage.save_meeting(sample_meeting)

    # Delete
    success = storage.delete_meeting(meeting_id)

    assert success is True

    # Verify deleted
    retrieved = storage.get_meeting(meeting_id)
    assert retrieved is None


def test_update_meeting(storage, sample_meeting):
    """Test updating a meeting."""
    meeting_id = storage.save_meeting(sample_meeting)

    # Update title
    sample_meeting.id = meeting_id
    sample_meeting.title = "Updated Title"

    success = storage.update_meeting(sample_meeting)

    assert success is True

    # Verify update
    retrieved = storage.get_meeting(meeting_id)
    assert retrieved.title == "Updated Title"


def test_get_statistics(storage, sample_meeting):
    """Test getting database statistics."""
    storage.save_meeting(sample_meeting)
    storage.save_meeting(sample_meeting)

    stats = storage.get_statistics()

    assert stats["total_meetings"] == 2
    assert stats["most_recent_date"] is not None
