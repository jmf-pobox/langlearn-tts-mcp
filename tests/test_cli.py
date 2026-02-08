"""Tests for langlearn_polly.cli."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from langlearn_polly.cli import main
from langlearn_polly.types import MergeStrategy, SynthesisResult


def _mock_synthesize_result(path: Path, text: str = "hello") -> SynthesisResult:
    return SynthesisResult(
        file_path=path,
        text=text,
        voice_name="Joanna",
    )


class TestSynthesizeCommand:
    @patch("langlearn_polly.cli.PollyClient")
    def test_synthesize_basic(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "test.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize.return_value = _mock_synthesize_result(out)

        runner = CliRunner()
        result = runner.invoke(main, ["synthesize", "hello", "-o", str(out)])

        assert result.exit_code == 0
        assert str(out) in result.output
        mock_instance.synthesize.assert_called_once()

    @patch("langlearn_polly.cli.PollyClient")
    def test_synthesize_custom_voice(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "test.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize.return_value = _mock_synthesize_result(out)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["synthesize", "Hallo", "--voice", "hans", "-o", str(out)],
        )

        assert result.exit_code == 0
        call_args = mock_instance.synthesize.call_args
        request = call_args[0][0]
        assert request.voice.voice_id == "Hans"

    @patch("langlearn_polly.cli.PollyClient")
    def test_synthesize_custom_rate(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "test.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize.return_value = _mock_synthesize_result(out)

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["synthesize", "hello", "--rate", "100", "-o", str(out)],
        )

        assert result.exit_code == 0
        call_args = mock_instance.synthesize.call_args
        request = call_args[0][0]
        assert request.rate == 100

    def test_synthesize_invalid_voice(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["synthesize", "hello", "--voice", "nonexistent"],
        )
        assert result.exit_code != 0


class TestSynthesizeBatchCommand:
    @patch("langlearn_polly.cli.PollyClient")
    def test_batch_basic(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(["hello", "world"]))
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        mock_instance = mock_cls.return_value
        mock_instance.synthesize_batch.return_value = [
            _mock_synthesize_result(out_dir / "a.mp3", "hello"),
            _mock_synthesize_result(out_dir / "b.mp3", "world"),
        ]

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["synthesize-batch", str(input_file), "-d", str(out_dir)],
        )

        assert result.exit_code == 0
        mock_instance.synthesize_batch.assert_called_once()

    @patch("langlearn_polly.cli.PollyClient")
    def test_batch_with_merge(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        input_file = tmp_path / "input.json"
        input_file.write_text(json.dumps(["hello", "world"]))
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        mock_instance = mock_cls.return_value
        mock_instance.synthesize_batch.return_value = [
            _mock_synthesize_result(out_dir / "merged.mp3", "hello | world"),
        ]

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "synthesize-batch",
                str(input_file),
                "-d",
                str(out_dir),
                "--merge",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_instance.synthesize_batch.call_args
        assert call_args[0][2] == MergeStrategy.ONE_FILE_PER_BATCH


class TestSynthesizePairCommand:
    @patch("langlearn_polly.cli.PollyClient")
    def test_pair_basic(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "pair.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize_pair.return_value = SynthesisResult(
            file_path=out,
            text="strong | stark",
            voice_name="Joanna+Hans",
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "synthesize-pair",
                "strong",
                "stark",
                "--voice1",
                "joanna",
                "--voice2",
                "hans",
                "-o",
                str(out),
            ],
        )

        assert result.exit_code == 0
        assert str(out) in result.output

    @patch("langlearn_polly.cli.PollyClient")
    def test_pair_custom_pause(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        out = tmp_path / "pair.mp3"
        mock_instance = mock_cls.return_value
        mock_instance.synthesize_pair.return_value = SynthesisResult(
            file_path=out,
            text="strong | stark",
            voice_name="Joanna+Hans",
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "synthesize-pair",
                "strong",
                "stark",
                "--pause",
                "1000",
                "-o",
                str(out),
            ],
        )

        assert result.exit_code == 0
        call_args = mock_instance.synthesize_pair.call_args
        # pause is the 6th positional arg
        assert call_args[0][5] == 1000


class TestSynthesizePairBatchCommand:
    @patch("langlearn_polly.cli.PollyClient")
    def test_pair_batch_basic(self, mock_cls: MagicMock, tmp_path: Path) -> None:
        input_file = tmp_path / "pairs.json"
        input_file.write_text(json.dumps([["strong", "stark"], ["house", "Haus"]]))
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        mock_instance = mock_cls.return_value
        mock_instance.synthesize_pair_batch.return_value = [
            SynthesisResult(
                file_path=out_dir / "a.mp3",
                text="strong | stark",
                voice_name="Joanna+Hans",
            ),
            SynthesisResult(
                file_path=out_dir / "b.mp3",
                text="house | Haus",
                voice_name="Joanna+Hans",
            ),
        ]

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "synthesize-pair-batch",
                str(input_file),
                "-d",
                str(out_dir),
            ],
        )

        assert result.exit_code == 0
        mock_instance.synthesize_pair_batch.assert_called_once()


class TestMainGroup:
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "langlearn-polly" in result.output

    def test_synthesize_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["synthesize", "--help"])
        assert result.exit_code == 0
        assert "voice" in result.output.lower()

    def test_verbose_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["-v", "--help"])
        assert result.exit_code == 0
