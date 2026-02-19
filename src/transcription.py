"""Audio transcription using Whisper."""

import logging
import warnings
from pathlib import Path
from typing import List, Optional, Tuple
import torch

warnings.filterwarnings("ignore", category=FutureWarning)

from src.config import Config
from src.schemas import TranscriptSegment

logger = logging.getLogger(__name__)


class AudioTranscriber:
    """Transcribe audio files using Whisper."""

    def __init__(self, model_name: str = None, device: str = None):
        """Initialize transcriber.

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
            device: Device to use (cpu, cuda)
        """
        self.model_name = model_name or Config.WHISPER_MODEL
        self.device = device or Config.WHISPER_DEVICE
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load Whisper model."""
        try:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe(
        self,
        audio_path: str | Path,
        language: str = "en",
        initial_prompt: Optional[str] = None
    ) -> Tuple[List[TranscriptSegment], dict]:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en')
            initial_prompt: Optional prompt to guide transcription

        Returns:
            Tuple of (segments, metadata)
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing: {audio_path.name}")

        try:
            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                initial_prompt=initial_prompt,
                word_timestamps=True,
                verbose=False
            )

            # Convert to transcript segments
            segments = []
            for seg in result.get("segments", []):
                segment = TranscriptSegment(
                    start=seg["start"],
                    end=seg["end"],
                    text=seg["text"].strip(),
                    speaker="Speaker 1",  # Will be updated by diarization
                    confidence=self._calculate_confidence(seg)
                )
                segments.append(segment)

            metadata = {
                "language": result.get("language", language),
                "duration": result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0,
                "model": self.model_name
            }

            logger.info(f"Transcription complete: {len(segments)} segments")
            return segments, metadata

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def _calculate_confidence(self, segment: dict) -> float:
        """Calculate confidence score for a segment.

        Args:
            segment: Whisper segment dict

        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Whisper doesn't provide direct confidence scores
        # Use heuristics based on segment properties
        text = segment.get("text", "").strip()
        duration = segment.get("end", 0) - segment.get("start", 0)

        # Low confidence indicators
        if len(text) < 5:
            return 0.6
        if duration < 0.5:
            return 0.7
        if "[" in text or "]" in text:  # Often indicates uncertainty
            return 0.5

        # Check for common filler words
        fillers = ["um", "uh", "er", "ah"]
        if any(filler in text.lower() for filler in fillers):
            return 0.8

        return 0.95

    def transcribe_with_vad(
        self,
        audio_path: str | Path,
        language: str = "en"
    ) -> Tuple[List[TranscriptSegment], dict]:
        """Transcribe with Voice Activity Detection to remove silence.

        Args:
            audio_path: Path to audio file
            language: Language code

        Returns:
            Tuple of (segments, metadata)
        """
        # For now, use standard transcription
        # TODO: Implement VAD preprocessing with webrtcvad
        return self.transcribe(audio_path, language)


class FastTranscriber:
    """Faster transcription using faster-whisper."""

    def __init__(self, model_name: str = None, device: str = None):
        """Initialize faster transcriber.

        Args:
            model_name: Whisper model name
            device: Device to use
        """
        self.model_name = model_name or Config.WHISPER_MODEL
        self.device = device or Config.WHISPER_DEVICE
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load faster-whisper model."""
        try:
            from faster_whisper import WhisperModel
            logger.info(f"Loading faster-whisper model: {self.model_name}")

            # Use CPU by default for compatibility
            compute_type = "int8" if self.device == "cpu" else "float16"

            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=compute_type
            )
            logger.info("Faster-whisper model loaded")
        except Exception as e:
            logger.error(f"Failed to load faster-whisper: {e}")
            raise

    def transcribe(
        self,
        audio_path: str | Path,
        language: str = "en"
    ) -> Tuple[List[TranscriptSegment], dict]:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            language: Language code

        Returns:
            Tuple of (segments, metadata)
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Fast transcribing: {audio_path.name}")

        try:
            segments_generator, info = self.model.transcribe(
                str(audio_path),
                language=language,
                word_timestamps=False
            )

            segments = []
            for seg in segments_generator:
                segment = TranscriptSegment(
                    start=seg.start,
                    end=seg.end,
                    text=seg.text.strip(),
                    speaker="Speaker 1",
                    confidence=0.9  # faster-whisper doesn't provide confidence
                )
                segments.append(segment)

            metadata = {
                "language": info.language,
                "duration": info.duration,
                "model": self.model_name
            }

            logger.info(f"Fast transcription complete: {len(segments)} segments")
            return segments, metadata

        except Exception as e:
            logger.error(f"Fast transcription failed: {e}")
            raise


def get_transcriber(use_fast: bool = True) -> AudioTranscriber | FastTranscriber:
    """Get appropriate transcriber based on configuration.

    Args:
        use_fast: Use faster-whisper if True, else standard whisper

    Returns:
        Transcriber instance
    """
    try:
        if use_fast:
            return FastTranscriber()
        else:
            return AudioTranscriber()
    except Exception as e:
        logger.warning(f"Failed to load preferred transcriber, falling back: {e}")
        # Fallback to standard whisper
        return AudioTranscriber()
