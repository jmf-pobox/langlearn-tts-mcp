"""Domain types for langlearn-polly."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_polly.literals import (
        EngineType,
        LanguageCodeType,
        VoiceIdType,
    )


class MergeStrategy(Enum):
    """Controls whether batch operations produce one file per input or one
    merged file for the entire batch."""

    ONE_FILE_PER_INPUT = "separate"
    ONE_FILE_PER_BATCH = "single"


@dataclass(frozen=True)
class VoiceConfig:
    """Maps a voice to its Polly parameters.

    Each VoiceConfig bundles a Polly voice ID with its required language
    code and engine type, eliminating the need for callers to know these
    implementation details.
    """

    voice_id: VoiceIdType
    language_code: LanguageCodeType
    engine: EngineType


# Voices keyed by a short human-readable name.
# Extend this mapping to add support for new languages/voices.
VOICES: dict[str, VoiceConfig] = {
    # English (US)
    "joanna": VoiceConfig(voice_id="Joanna", language_code="en-US", engine="neural"),
    "matthew": VoiceConfig(voice_id="Matthew", language_code="en-US", engine="neural"),
    # German
    "marlene": VoiceConfig(voice_id="Marlene", language_code="de-DE", engine="neural"),
    "hans": VoiceConfig(voice_id="Hans", language_code="de-DE", engine="neural"),
    "vicki": VoiceConfig(voice_id="Vicki", language_code="de-DE", engine="standard"),
    "daniel": VoiceConfig(voice_id="Daniel", language_code="de-DE", engine="standard"),
    # Russian
    "tatyana": VoiceConfig(
        voice_id="Tatyana", language_code="ru-RU", engine="standard"
    ),
    "maxim": VoiceConfig(voice_id="Maxim", language_code="ru-RU", engine="standard"),
    # Korean
    "seoyeon": VoiceConfig(voice_id="Seoyeon", language_code="ko-KR", engine="neural"),
}


def resolve_voice(name: str) -> VoiceConfig:
    """Resolve a voice name to its configuration.

    Args:
        name: Case-insensitive voice name (e.g. "joanna", "Hans").

    Returns:
        The corresponding VoiceConfig.

    Raises:
        ValueError: If the voice name is not found in VOICES.
    """
    key = name.lower()
    if key not in VOICES:
        available = ", ".join(sorted(VOICES))
        raise ValueError(f"Unknown voice '{name}'. Available: {available}")
    return VOICES[key]


@dataclass(frozen=True)
class SynthesisRequest:
    """A request to synthesize a single text to audio."""

    text: str
    voice: VoiceConfig
    rate: int = 75
    """Speech rate as a percentage (e.g. 75 = 75% speed)."""


@dataclass(frozen=True)
class SynthesisResult:
    """The result of a synthesis operation."""

    file_path: Path
    text: str
    voice_name: str

    def to_dict(self) -> dict[str, str]:
        """Serialize to a dict suitable for MCP tool responses."""
        return {
            "file_path": str(self.file_path),
            "text": self.text,
            "voice": self.voice_name,
        }


def generate_filename(text: str, prefix: str = "") -> str:
    """Generate a deterministic MP3 filename from text content.

    Uses an MD5 hash of the text to produce a stable, filesystem-safe
    filename. An optional prefix is prepended for disambiguation.

    Args:
        text: The source text.
        prefix: Optional prefix (e.g. "pair_").

    Returns:
        A filename like "a1b2c3d4.mp3" or "pair_a1b2c3d4.mp3".
    """
    digest = hashlib.md5(text.encode()).hexdigest()[:12]
    if prefix:
        return f"{prefix}{digest}.mp3"
    return f"{digest}.mp3"
