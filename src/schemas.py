"""Data schemas for Meeting Minutes Generator."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class TranscriptSegment(BaseModel):
    """A segment of transcribed speech."""
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text")
    speaker: str = Field(default="Speaker 1", description="Speaker label")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")

    @validator('text')
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class ActionItem(BaseModel):
    """An action item extracted from the meeting."""
    owner: str = Field(..., description="Person responsible")
    task: str = Field(..., description="Task description")
    due_date: Optional[str] = Field(None, description="Due date if mentioned")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")
    status: str = Field(default="Open", description="Status of action item")


class MeetingMinutes(BaseModel):
    """Structured meeting minutes."""
    summary: List[str] = Field(default_factory=list, description="Executive summary bullets")
    decisions: List[str] = Field(default_factory=list, description="Key decisions made")
    action_items: List[ActionItem] = Field(default_factory=list, description="Action items")
    risks: List[str] = Field(default_factory=list, description="Risks and open questions")
    notes: Optional[str] = Field(None, description="Additional notes")

    @validator('summary')
    def summary_max_length(cls, v):
        if len(v) > 8:
            return v[:8]
        return v


class Meeting(BaseModel):
    """Complete meeting data."""
    id: Optional[int] = None
    title: str = Field(..., description="Meeting title")
    date: datetime = Field(default_factory=datetime.now)
    participants: List[str] = Field(default_factory=list, description="List of participants")
    agenda: Optional[str] = Field(None, description="Meeting agenda")
    transcript: List[TranscriptSegment] = Field(default_factory=list)
    minutes: Optional[MeetingMinutes] = None
    audio_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExportOptions(BaseModel):
    """Options for exporting meeting minutes."""
    include_transcript: bool = True
    include_timestamps: bool = True
    include_speaker_labels: bool = True
    format: str = Field(..., pattern="^(docx|pdf)$")
    company_logo: Optional[str] = None
    template_style: str = Field(default="professional")
