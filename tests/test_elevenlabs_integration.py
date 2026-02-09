"""ElevenLabs integration tests — requires ELEVENLABS_API_KEY.

Run with: uv run pytest tests/test_elevenlabs_integration.py -v -m integration
"""

from __future__ import annotations

from pathlib import Path

import pytest

from langlearn_tts.providers.elevenlabs import ElevenLabsProvider
from langlearn_tts.types import SynthesisRequest

pytestmark = pytest.mark.integration


@pytest.fixture
def provider() -> ElevenLabsProvider:
    """Create a real ElevenLabsProvider (no mock client)."""
    return ElevenLabsProvider()


class TestCheckHealth:
    def test_check_health_reports_subscription(
        self, provider: ElevenLabsProvider
    ) -> None:
        checks = provider.check_health()

        assert any(check.passed and "API key: set" in check.message for check in checks)
        assert any(
            check.passed and "subscription" in check.message.lower()
            for check in checks
        )


class TestResolveVoice:
    def test_resolve_voice_known_name(self, provider: ElevenLabsProvider) -> None:
        """Known voice name resolves via the live API voice list."""
        import langlearn_tts.providers.elevenlabs as elevenlabs

        saved_voices = dict(elevenlabs.VOICES)
        saved_loaded = elevenlabs._voices_loaded  # pyright: ignore[reportPrivateUsage]

        elevenlabs.VOICES.clear()
        elevenlabs._voices_loaded = False  # pyright: ignore[reportPrivateUsage]

        try:
            result = provider.resolve_voice("alice")
            assert result == "alice"
        finally:
            elevenlabs.VOICES.clear()
            elevenlabs.VOICES.update(saved_voices)
            elevenlabs._voices_loaded = saved_loaded  # pyright: ignore[reportPrivateUsage]

    def test_resolve_voice_unknown_raises(self, provider: ElevenLabsProvider) -> None:
        with pytest.raises(ValueError, match="Unknown voice"):
            provider.resolve_voice("zzz_nonexistent_voice_zzz")


class TestSynthesize:
    def test_synthesize_short_text(
        self, provider: ElevenLabsProvider, tmp_path: Path
    ) -> None:
        request = SynthesisRequest(text="Hello, world.", voice="rachel", rate=100)
        out = tmp_path / "hello.mp3"

        result = provider.synthesize(request, out)

        assert result.file_path == out
        assert result.text == "Hello, world."
        assert result.voice_name == "rachel"
        assert out.exists()
        assert out.stat().st_size > 0

    def test_synthesize_non_english(
        self, provider: ElevenLabsProvider, tmp_path: Path
    ) -> None:
        """German text synthesis."""
        request = SynthesisRequest(
            text="Guten Tag, wie geht es Ihnen?", voice="rachel", rate=100
        )
        out = tmp_path / "german.mp3"

        result = provider.synthesize(request, out)

        assert out.exists()
        assert out.stat().st_size > 0
        assert result.text == "Guten Tag, wie geht es Ihnen?"

    def test_synthesize_with_voice_settings(
        self, provider: ElevenLabsProvider, tmp_path: Path
    ) -> None:
        request = SynthesisRequest(
            text="Testing voice settings.",
            voice="rachel",
            rate=100,
            stability=0.5,
            similarity=0.7,
            style=0.3,
            speaker_boost=True,
        )
        out = tmp_path / "settings.mp3"

        result = provider.synthesize(request, out)

        assert out.exists()
        assert out.stat().st_size > 0
        assert result.voice_name == "rachel"
