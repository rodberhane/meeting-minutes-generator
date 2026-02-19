"""Tests for export module."""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from src.export import DocumentExporter
from src.schemas import Meeting, TranscriptSegment, MeetingMinutes, ActionItem, ExportOptions


@pytest.fixture
def temp_exports_dir():
    """Create temporary exports directory."""
    temp_dir = Path(tempfile.mkdtemp())

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def exporter(temp_exports_dir, monkeypatch):
    """Create exporter with temp directory."""
    from src.config import Config
    monkeypatch.setattr(Config, 'EXPORTS_DIR', temp_exports_dir)

    return DocumentExporter()


@pytest.fixture
def sample_meeting():
    """Create a sample meeting for export."""
    transcript = [
        TranscriptSegment(
            start=0.0,
            end=5.0,
            text="Welcome everyone to the meeting.",
            speaker="John Smith"
        ),
        TranscriptSegment(
            start=5.0,
            end=10.0,
            text="Thank you John. Let's get started.",
            speaker="Jane Doe"
        )
    ]

    minutes = MeetingMinutes(
        summary=[
            "Reviewed Q1 performance metrics",
            "Discussed product roadmap for Q2",
            "Addressed budget concerns"
        ],
        decisions=[
            "Approved marketing budget increase",
            "Postponed feature X to Q3"
        ],
        action_items=[
            ActionItem(
                owner="John Smith",
                task="Prepare Q2 budget proposal",
                due_date="2026-03-01",
                status="Open"
            ),
            ActionItem(
                owner="Jane Doe",
                task="Update product roadmap document",
                due_date="2026-02-25",
                status="Open"
            )
        ],
        risks=[
            "Potential resource constraints in Q2",
            "Dependency on external vendor for feature Y"
        ]
    )

    return Meeting(
        title="Q1 Review Meeting",
        date=datetime(2026, 2, 18, 14, 0),
        participants=["John Smith", "Jane Doe", "Bob Wilson"],
        agenda="1. Review Q1 results\n2. Plan Q2\n3. Budget discussion",
        transcript=transcript,
        minutes=minutes
    )


def test_export_docx(exporter, sample_meeting):
    """Test DOCX export."""
    options = ExportOptions(
        format="docx",
        include_transcript=True,
        include_timestamps=True,
        include_speaker_labels=True
    )

    file_path = exporter.export_docx(sample_meeting, options)

    assert file_path.exists()
    assert file_path.suffix == ".docx"
    assert file_path.stat().st_size > 0


def test_export_pdf(exporter, sample_meeting):
    """Test PDF export."""
    options = ExportOptions(
        format="pdf",
        include_transcript=True,
        include_timestamps=True,
        include_speaker_labels=True
    )

    file_path = exporter.export_pdf(sample_meeting, options)

    assert file_path.exists()
    assert file_path.suffix == ".pdf"
    assert file_path.stat().st_size > 0


def test_export_without_transcript(exporter, sample_meeting):
    """Test export without transcript."""
    options = ExportOptions(
        format="docx",
        include_transcript=False,
        include_timestamps=False,
        include_speaker_labels=False
    )

    file_path = exporter.export_docx(sample_meeting, options)

    assert file_path.exists()


def test_filename_generation(exporter, sample_meeting):
    """Test filename generation."""
    filename = exporter._generate_filename(sample_meeting, "docx")

    assert "20260218" in filename  # Date
    assert "Q1_Review_Meeting" in filename  # Sanitized title
    assert filename.endswith(".docx")


def test_timestamp_formatting(exporter):
    """Test timestamp formatting."""
    assert exporter._format_timestamp(0) == "00:00"
    assert exporter._format_timestamp(65) == "01:05"
    assert exporter._format_timestamp(3665) == "61:05"
