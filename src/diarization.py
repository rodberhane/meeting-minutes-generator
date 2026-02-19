"""Speaker diarization for meeting audio."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

from src.config import Config
from src.schemas import TranscriptSegment

logger = logging.getLogger(__name__)


class SpeakerDiarizer:
    """Identify and label speakers in audio."""

    def __init__(self, use_auth_token: Optional[str] = None):
        """Initialize diarizer.

        Args:
            use_auth_token: HuggingFace token for pyannote.audio models
        """
        self.use_auth_token = use_auth_token
        self.pipeline = None
        self._load_pipeline()

    def _load_pipeline(self):
        """Load pyannote.audio diarization pipeline."""
        try:
            from pyannote.audio import Pipeline
            logger.info("Loading pyannote.audio diarization pipeline")

            # Note: Requires HuggingFace token for model access
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.use_auth_token
            )

            logger.info("Diarization pipeline loaded")
        except Exception as e:
            logger.warning(f"Could not load pyannote.audio: {e}")
            logger.info("Diarization will use fallback method")
            self.pipeline = None

    def diarize(
        self,
        audio_path: str | Path,
        num_speakers: Optional[int] = None
    ) -> List[Tuple[float, float, str]]:
        """Perform speaker diarization.

        Args:
            audio_path: Path to audio file
            num_speakers: Optional number of speakers (for better accuracy)

        Returns:
            List of (start, end, speaker_label) tuples
        """
        audio_path = Path(audio_path)

        if self.pipeline is None:
            return self._fallback_diarization(audio_path, num_speakers)

        try:
            logger.info(f"Diarizing: {audio_path.name}")

            # Run diarization
            diarization_result = self.pipeline(
                str(audio_path),
                num_speakers=num_speakers
            )

            # Convert to list of segments
            speaker_segments = []
            for turn, _, speaker in diarization_result.itertracks(yield_label=True):
                speaker_segments.append((
                    turn.start,
                    turn.end,
                    f"Speaker {speaker}"
                ))

            logger.info(f"Diarization complete: {len(speaker_segments)} speaker turns")
            return speaker_segments

        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            return self._fallback_diarization(audio_path, num_speakers)

    def _fallback_diarization(
        self,
        audio_path: Path,
        num_speakers: Optional[int] = None
    ) -> List[Tuple[float, float, str]]:
        """Fallback diarization using simple heuristics.

        Args:
            audio_path: Path to audio file
            num_speakers: Number of speakers (ignored in fallback)

        Returns:
            List of speaker segments
        """
        logger.info("Using fallback diarization")

        # Simple approach: alternate speakers every 30 seconds
        # User can manually adjust in the UI
        try:
            import librosa
            duration = librosa.get_duration(path=str(audio_path))

            segments = []
            current_time = 0.0
            speaker_num = 1
            segment_length = 30.0  # seconds

            while current_time < duration:
                end_time = min(current_time + segment_length, duration)
                segments.append((
                    current_time,
                    end_time,
                    f"Speaker {speaker_num}"
                ))
                current_time = end_time
                speaker_num = 2 if speaker_num == 1 else 1  # Alternate

            return segments

        except Exception as e:
            logger.error(f"Fallback diarization failed: {e}")
            return []

    def apply_diarization(
        self,
        transcript_segments: List[TranscriptSegment],
        speaker_segments: List[Tuple[float, float, str]]
    ) -> List[TranscriptSegment]:
        """Apply speaker labels to transcript segments.

        Args:
            transcript_segments: List of transcript segments
            speaker_segments: List of (start, end, speaker) tuples

        Returns:
            Updated transcript segments with speaker labels
        """
        if not speaker_segments:
            return transcript_segments

        updated_segments = []

        for seg in transcript_segments:
            # Find overlapping speaker segment
            speaker = self._find_speaker(
                seg.start,
                seg.end,
                speaker_segments
            )

            # Update segment with speaker label
            updated_seg = seg.model_copy()
            updated_seg.speaker = speaker
            updated_segments.append(updated_seg)

        return updated_segments

    def _find_speaker(
        self,
        start: float,
        end: float,
        speaker_segments: List[Tuple[float, float, str]]
    ) -> str:
        """Find the speaker for a given time range.

        Args:
            start: Start time
            end: End time
            speaker_segments: List of speaker segments

        Returns:
            Speaker label
        """
        # Find speaker with maximum overlap
        max_overlap = 0.0
        best_speaker = "Speaker 1"

        segment_duration = end - start

        for sp_start, sp_end, speaker in speaker_segments:
            # Calculate overlap
            overlap_start = max(start, sp_start)
            overlap_end = min(end, sp_end)
            overlap = max(0, overlap_end - overlap_start)

            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = speaker

        return best_speaker


def merge_transcript_and_diarization(
    transcript_segments: List[TranscriptSegment],
    audio_path: str | Path,
    num_speakers: Optional[int] = None,
    use_auth_token: Optional[str] = None
) -> List[TranscriptSegment]:
    """Merge transcript with speaker diarization.

    Args:
        transcript_segments: Transcript segments
        audio_path: Path to audio file
        num_speakers: Optional number of speakers
        use_auth_token: HuggingFace auth token

    Returns:
        Transcript segments with speaker labels
    """
    try:
        diarizer = SpeakerDiarizer(use_auth_token)
        speaker_segments = diarizer.diarize(audio_path, num_speakers)
        return diarizer.apply_diarization(transcript_segments, speaker_segments)
    except Exception as e:
        logger.error(f"Failed to merge diarization: {e}")
        return transcript_segments
