"""Database storage for meetings."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.config import Config
from src.schemas import Meeting, TranscriptSegment, MeetingMinutes

logger = logging.getLogger(__name__)

Base = declarative_base()


class MeetingDB(Base):
    """Database model for meetings."""

    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    participants = Column(Text)  # JSON string
    agenda = Column(Text, nullable=True)
    transcript = Column(Text)  # JSON string
    minutes = Column(Text, nullable=True)  # JSON string
    audio_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class MeetingStorage:
    """Storage manager for meetings."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize storage.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or Config.STORAGE_PATH
        self.engine = None
        self.Session = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize database connection and create tables."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            db_url = f"sqlite:///{self.db_path}"
            self.engine = create_engine(db_url, echo=False)

            # Create tables
            Base.metadata.create_all(self.engine)

            # Create session factory
            self.Session = sessionmaker(bind=self.engine)

            logger.info(f"Database initialized: {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def save_meeting(self, meeting: Meeting) -> int:
        """Save meeting to database.

        Args:
            meeting: Meeting object

        Returns:
            Meeting ID
        """
        session: Session = self.Session()

        try:
            # Convert to database model
            db_meeting = MeetingDB(
                title=meeting.title,
                date=meeting.date,
                participants=json.dumps(meeting.participants),
                agenda=meeting.agenda,
                transcript=json.dumps([seg.model_dump() for seg in meeting.transcript]),
                minutes=json.dumps(meeting.minutes.model_dump()) if meeting.minutes else None,
                audio_path=meeting.audio_path,
                created_at=meeting.created_at,
                updated_at=meeting.updated_at
            )

            if meeting.id:
                # Update existing
                db_meeting.id = meeting.id
                session.merge(db_meeting)
            else:
                # Create new
                session.add(db_meeting)

            session.commit()

            meeting_id = db_meeting.id
            logger.info(f"Meeting saved: ID {meeting_id}")

            return meeting_id

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save meeting: {e}")
            raise

        finally:
            session.close()

    def get_meeting(self, meeting_id: int) -> Optional[Meeting]:
        """Get meeting by ID.

        Args:
            meeting_id: Meeting ID

        Returns:
            Meeting object or None
        """
        session: Session = self.Session()

        try:
            db_meeting = session.query(MeetingDB).filter_by(id=meeting_id).first()

            if not db_meeting:
                return None

            # Convert to Meeting schema
            return self._db_to_meeting(db_meeting)

        except Exception as e:
            logger.error(f"Failed to get meeting: {e}")
            return None

        finally:
            session.close()

    def list_meetings(
        self,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None
    ) -> List[Meeting]:
        """List meetings.

        Args:
            limit: Maximum number of meetings to return
            offset: Offset for pagination
            search: Optional search query (searches title and participants)

        Returns:
            List of meetings
        """
        session: Session = self.Session()

        try:
            query = session.query(MeetingDB)

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    (MeetingDB.title.like(search_term)) |
                    (MeetingDB.participants.like(search_term))
                )

            query = query.order_by(MeetingDB.date.desc())
            query = query.limit(limit).offset(offset)

            db_meetings = query.all()

            return [self._db_to_meeting(db_meeting) for db_meeting in db_meetings]

        except Exception as e:
            logger.error(f"Failed to list meetings: {e}")
            return []

        finally:
            session.close()

    def delete_meeting(self, meeting_id: int) -> bool:
        """Delete meeting.

        Args:
            meeting_id: Meeting ID

        Returns:
            True if deleted, False otherwise
        """
        session: Session = self.Session()

        try:
            db_meeting = session.query(MeetingDB).filter_by(id=meeting_id).first()

            if not db_meeting:
                return False

            # Delete audio file if exists
            if db_meeting.audio_path:
                audio_path = Path(db_meeting.audio_path)
                if audio_path.exists():
                    audio_path.unlink()

            session.delete(db_meeting)
            session.commit()

            logger.info(f"Meeting deleted: ID {meeting_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete meeting: {e}")
            return False

        finally:
            session.close()

    def update_meeting(self, meeting: Meeting) -> bool:
        """Update existing meeting.

        Args:
            meeting: Meeting object with id

        Returns:
            True if updated, False otherwise
        """
        if not meeting.id:
            logger.error("Meeting ID required for update")
            return False

        try:
            self.save_meeting(meeting)
            return True
        except Exception as e:
            logger.error(f"Failed to update meeting: {e}")
            return False

    def _db_to_meeting(self, db_meeting: MeetingDB) -> Meeting:
        """Convert database model to Meeting schema.

        Args:
            db_meeting: Database model

        Returns:
            Meeting object
        """
        # Parse transcript
        transcript_data = json.loads(db_meeting.transcript) if db_meeting.transcript else []
        transcript = [TranscriptSegment(**seg) for seg in transcript_data]

        # Parse minutes
        minutes = None
        if db_meeting.minutes:
            minutes_data = json.loads(db_meeting.minutes)
            minutes = MeetingMinutes(**minutes_data)

        # Parse participants
        participants = json.loads(db_meeting.participants) if db_meeting.participants else []

        return Meeting(
            id=db_meeting.id,
            title=db_meeting.title,
            date=db_meeting.date,
            participants=participants,
            agenda=db_meeting.agenda,
            transcript=transcript,
            minutes=minutes,
            audio_path=db_meeting.audio_path,
            created_at=db_meeting.created_at,
            updated_at=db_meeting.updated_at
        )

    def get_statistics(self) -> dict:
        """Get database statistics.

        Returns:
            Dictionary with statistics
        """
        session: Session = self.Session()

        try:
            total_meetings = session.query(MeetingDB).count()

            recent_meeting = session.query(MeetingDB)\
                .order_by(MeetingDB.date.desc())\
                .first()

            return {
                "total_meetings": total_meetings,
                "most_recent_date": recent_meeting.date if recent_meeting else None,
                "database_path": str(self.db_path)
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

        finally:
            session.close()
