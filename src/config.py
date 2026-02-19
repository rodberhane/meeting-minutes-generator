"""Configuration management for Meeting Minutes Generator."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    EXPORTS_DIR = BASE_DIR / "exports"
    AUDIO_DIR = DATA_DIR / "audio"

    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    EXPORTS_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)

    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Whisper Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    WHISPER_DEVICE: str = "cpu"  # "cuda" if GPU available

    # Privacy Settings
    PRIVACY_MODE: bool = os.getenv("PRIVACY_MODE", "true").lower() == "true"
    AUDIO_RETENTION_DAYS: int = int(os.getenv("AUDIO_RETENTION_DAYS", "7"))

    # File Limits
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")

    # Database
    STORAGE_PATH: Path = Path(os.getenv("STORAGE_PATH", str(DATA_DIR / "meetings.db")))

    # Supported audio formats
    SUPPORTED_FORMATS = [".mp3", ".wav", ".m4a", ".flac", ".ogg"]

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        if not cls.PRIVACY_MODE and cls.LLM_PROVIDER in ["openai", "anthropic"]:
            if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
                return False
            if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
                return False
        return True

    @classmethod
    def get_status_message(cls) -> str:
        """Get configuration status message."""
        messages = []
        messages.append(f"Privacy Mode: {'Enabled ✅' if cls.PRIVACY_MODE else 'Disabled ⚠️'}")
        messages.append(f"Whisper Model: {cls.WHISPER_MODEL}")
        messages.append(f"LLM Provider: {cls.LLM_PROVIDER}")

        if not cls.PRIVACY_MODE:
            if cls.LLM_PROVIDER == "openai":
                status = "✅" if cls.OPENAI_API_KEY else "❌ Missing API Key"
                messages.append(f"OpenAI: {status}")
            elif cls.LLM_PROVIDER == "anthropic":
                status = "✅" if cls.ANTHROPIC_API_KEY else "❌ Missing API Key"
                messages.append(f"Anthropic: {status}")

        return "\n".join(messages)
