"""LLM-based meeting summarization and action item extraction."""

import json
import logging
from typing import List, Optional

from src.config import Config
from src.schemas import TranscriptSegment, MeetingMinutes, ActionItem

logger = logging.getLogger(__name__)


class MeetingSummarizer:
    """Generate meeting minutes from transcript using LLM."""

    SYSTEM_PROMPT = """You are a professional meeting minutes assistant. Your task is to analyze meeting transcripts and extract structured information.

Generate a JSON response with the following structure:
{
    "summary": ["bullet point 1", "bullet point 2", ...],  // 5-8 max
    "decisions": ["decision 1", "decision 2", ...],
    "action_items": [
        {
            "owner": "person name",
            "task": "clear task description",
            "due_date": "date if mentioned, null otherwise",
            "confidence": 0.9
        }
    ],
    "risks": ["risk or open question 1", ...]
}

Guidelines:
- Summary: Focus on key outcomes and topics discussed (5-8 bullets max)
- Decisions: Clear, actionable decisions made during the meeting
- Action items: Must have owner and task. Extract due date if mentioned. Set confidence based on clarity
- Risks: Important concerns, blockers, or open questions raised
- Be concise and professional
- If a section has no content, return an empty list"""

    def __init__(self, provider: str = None, model: str = None, api_key: str = None):
        """Initialize summarizer.

        Args:
            provider: LLM provider (openai, anthropic, local)
            model: Model name
            api_key: API key for cloud providers
        """
        self.provider = provider or Config.LLM_PROVIDER
        self.model = model or Config.LLM_MODEL
        self.api_key = api_key or self._get_api_key()
        self.client = None
        self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Get API key for the provider."""
        if self.provider == "openai":
            return Config.OPENAI_API_KEY
        elif self.provider == "anthropic":
            return Config.ANTHROPIC_API_KEY
        return None

    def _initialize_client(self):
        """Initialize LLM client based on provider."""
        if Config.PRIVACY_MODE and self.provider in ["openai", "anthropic"]:
            logger.warning("Privacy mode enabled, but cloud LLM provider selected")
            logger.warning("Consider using local LLM or disabling privacy mode")

        try:
            if self.provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"Initialized OpenAI client with model: {self.model}")

            elif self.provider == "anthropic":
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                logger.info(f"Initialized Anthropic client with model: {self.model}")

            else:
                logger.warning(f"Unsupported provider: {self.provider}")
                self.client = None

        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None

    def summarize(
        self,
        transcript_segments: List[TranscriptSegment],
        meeting_context: Optional[str] = None
    ) -> MeetingMinutes:
        """Generate meeting minutes from transcript.

        Args:
            transcript_segments: List of transcript segments
            meeting_context: Optional context about the meeting

        Returns:
            MeetingMinutes object
        """
        if not self.client:
            logger.warning("No LLM client available, returning empty minutes")
            return MeetingMinutes()

        # Format transcript for LLM
        transcript_text = self._format_transcript(transcript_segments)

        # Build user prompt
        user_prompt = f"""Meeting Transcript:

{transcript_text}"""

        if meeting_context:
            user_prompt = f"Meeting Context: {meeting_context}\n\n{user_prompt}"

        try:
            # Get completion from LLM
            response = self._get_completion(user_prompt)

            # Parse and validate response
            minutes = self._parse_response(response)

            logger.info("Meeting minutes generated successfully")
            return minutes

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return MeetingMinutes()

    def _format_transcript(self, segments: List[TranscriptSegment]) -> str:
        """Format transcript segments for LLM processing.

        Args:
            segments: Transcript segments

        Returns:
            Formatted transcript string
        """
        lines = []
        current_speaker = None

        for seg in segments:
            timestamp = self._format_timestamp(seg.start)

            # Group consecutive segments from same speaker
            if seg.speaker != current_speaker:
                lines.append(f"\n[{timestamp}] {seg.speaker}:")
                current_speaker = seg.speaker

            lines.append(f"  {seg.text}")

        return "\n".join(lines)

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp in MM:SS format.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _get_completion(self, prompt: str) -> str:
        """Get completion from LLM.

        Args:
            prompt: User prompt

        Returns:
            LLM response text
        """
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.content[0].text

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _parse_response(self, response: str) -> MeetingMinutes:
        """Parse LLM response into MeetingMinutes.

        Args:
            response: LLM response text

        Returns:
            MeetingMinutes object
        """
        try:
            # Parse JSON response
            data = json.loads(response)

            # Validate and convert to schema
            action_items = [
                ActionItem(**item) for item in data.get("action_items", [])
            ]

            minutes = MeetingMinutes(
                summary=data.get("summary", []),
                decisions=data.get("decisions", []),
                action_items=action_items,
                risks=data.get("risks", []),
                notes=data.get("notes")
            )

            # Validate schema
            self._validate_minutes(minutes)

            return minutes

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Try to extract JSON from markdown code blocks
            return self._extract_json_from_markdown(response)

        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return MeetingMinutes()

    def _extract_json_from_markdown(self, response: str) -> MeetingMinutes:
        """Extract JSON from markdown code blocks.

        Args:
            response: Response text that may contain markdown

        Returns:
            MeetingMinutes object
        """
        try:
            # Look for JSON in code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response

            data = json.loads(json_str)

            action_items = [
                ActionItem(**item) for item in data.get("action_items", [])
            ]

            return MeetingMinutes(
                summary=data.get("summary", []),
                decisions=data.get("decisions", []),
                action_items=action_items,
                risks=data.get("risks", [])
            )

        except Exception as e:
            logger.error(f"Failed to extract JSON from markdown: {e}")
            return MeetingMinutes()

    def _validate_minutes(self, minutes: MeetingMinutes):
        """Validate meeting minutes structure.

        Args:
            minutes: MeetingMinutes object

        Raises:
            ValueError: If validation fails
        """
        # Ensure summary is not too long
        if len(minutes.summary) > 8:
            logger.warning(f"Summary has {len(minutes.summary)} bullets, truncating to 8")
            minutes.summary = minutes.summary[:8]

        # Validate action items
        for item in minutes.action_items:
            if not item.owner or not item.task:
                raise ValueError("Action items must have owner and task")
