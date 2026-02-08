"""Tests for langlearn_polly.types."""

from __future__ import annotations

from pathlib import Path

import pytest

from langlearn_polly.types import (
    VOICES,
    MergeStrategy,
    SynthesisRequest,
    SynthesisResult,
    VoiceConfig,
    generate_filename,
    resolve_voice,
)


class TestVoiceConfig:
    def test_voice_config_is_frozen(self):
        cfg = VoiceConfig(voice_id="Joanna", language_code="en-US", engine="neural")
        with pytest.raises(AttributeError):
            cfg.voice_id = "Matthew"  # type: ignore[misc]

    def test_voices_dict_contains_expected_languages(self):
        assert "joanna" in VOICES
        assert "hans" in VOICES
        assert "tatyana" in VOICES
        assert "seoyeon" in VOICES

    def test_voice_config_values(self):
        hans = VOICES["hans"]
        assert hans.voice_id == "Hans"
        assert hans.language_code == "de-DE"
        assert hans.engine == "neural"


class TestResolveVoice:
    def test_resolve_existing_voice(self):
        cfg = resolve_voice("joanna")
        assert cfg.voice_id == "Joanna"

    def test_resolve_case_insensitive(self):
        cfg = resolve_voice("HANS")
        assert cfg.voice_id == "Hans"

    def test_resolve_unknown_voice_raises(self):
        with pytest.raises(ValueError, match="Unknown voice 'nonexistent'"):
            resolve_voice("nonexistent")

    def test_error_message_lists_available_voices(self):
        with pytest.raises(ValueError, match="Available:"):
            resolve_voice("invalid")


class TestMergeStrategy:
    def test_separate_value(self):
        assert MergeStrategy.ONE_FILE_PER_INPUT.value == "separate"

    def test_single_value(self):
        assert MergeStrategy.ONE_FILE_PER_BATCH.value == "single"


class TestSynthesisRequest:
    def test_default_rate(self):
        cfg = VOICES["joanna"]
        req = SynthesisRequest(text="hello", voice=cfg)
        assert req.rate == 75

    def test_custom_rate(self):
        cfg = VOICES["joanna"]
        req = SynthesisRequest(text="hello", voice=cfg, rate=100)
        assert req.rate == 100

    def test_frozen(self):
        cfg = VOICES["joanna"]
        req = SynthesisRequest(text="hello", voice=cfg)
        with pytest.raises(AttributeError):
            req.text = "world"  # type: ignore[misc]


class TestSynthesisResult:
    def test_to_dict(self):
        result = SynthesisResult(
            file_path=Path("/tmp/test.mp3"),
            text="hello",
            voice_name="Joanna",
        )
        d = result.to_dict()
        assert d["file_path"] == "/tmp/test.mp3"
        assert d["text"] == "hello"
        assert d["voice"] == "Joanna"


class TestGenerateFilename:
    def test_deterministic(self):
        name1 = generate_filename("hello")
        name2 = generate_filename("hello")
        assert name1 == name2

    def test_different_text_different_name(self):
        name1 = generate_filename("hello")
        name2 = generate_filename("world")
        assert name1 != name2

    def test_ends_with_mp3(self):
        name = generate_filename("test")
        assert name.endswith(".mp3")

    def test_prefix(self):
        name = generate_filename("test", prefix="pair_")
        assert name.startswith("pair_")
        assert name.endswith(".mp3")

    def test_no_prefix(self):
        name = generate_filename("test")
        assert not name.startswith("pair_")
