"""Click CLI for langlearn-polly."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import cast

import click

from langlearn_polly.core import PollyClient
from langlearn_polly.types import (
    MergeStrategy,
    SynthesisRequest,
    SynthesisResult,
    resolve_voice,
)

logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def _print_result(result: SynthesisResult) -> None:
    click.echo(f"{result.file_path}")


def _print_results(results: list[SynthesisResult]) -> None:
    for r in results:
        _print_result(r)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
def main(verbose: bool) -> None:
    """langlearn-polly: AWS Polly TTS for language learning."""
    _configure_logging(verbose)


@main.command()
@click.argument("text")
@click.option(
    "--voice",
    default="joanna",
    show_default=True,
    help="Voice name (e.g. joanna, hans, tatyana, seoyeon).",
)
@click.option(
    "--rate",
    default=75,
    show_default=True,
    type=int,
    help="Speech rate as percentage (e.g. 75 = 75%% speed).",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(path_type=Path),
    help="Output file path. Defaults to auto-generated name in pwd.",
)
def synthesize(text: str, voice: str, rate: int, output: Path | None) -> None:
    """Synthesize a single text to an MP3 file."""
    voice_cfg = resolve_voice(voice)
    request = SynthesisRequest(text=text, voice=voice_cfg, rate=rate)

    if output is None:
        output = Path.cwd() / f"{voice}_{text[:20].replace(' ', '_')}.mp3"

    client = PollyClient()
    result = client.synthesize(request, output)
    _print_result(result)


@main.command("synthesize-batch")
@click.option(
    "--voice",
    default="joanna",
    show_default=True,
    help="Voice name for all texts.",
)
@click.option(
    "--rate",
    default=75,
    show_default=True,
    type=int,
    help="Speech rate as percentage.",
)
@click.option(
    "--output-dir",
    "-d",
    default=None,
    type=click.Path(path_type=Path),
    help="Output directory. Defaults to current directory.",
)
@click.option(
    "--merge",
    is_flag=True,
    default=False,
    help="Merge all outputs into a single file.",
)
@click.option(
    "--pause",
    default=500,
    show_default=True,
    type=int,
    help="Pause between segments in ms (used with --merge).",
)
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def synthesize_batch(
    voice: str,
    rate: int,
    output_dir: Path | None,
    merge: bool,
    pause: int,
    input_file: Path,
) -> None:
    """Synthesize a batch of texts from a JSON file.

    INPUT_FILE should contain a JSON array of strings, e.g.:
    ["hello", "world", "good morning"]
    """
    voice_cfg = resolve_voice(voice)
    raw = json.loads(input_file.read_text(encoding="utf-8"))

    if not isinstance(raw, list):
        raise click.BadParameter("INPUT_FILE must contain a JSON array of strings.")

    texts = cast("list[str]", raw)
    requests = [SynthesisRequest(text=t, voice=voice_cfg, rate=rate) for t in texts]
    strategy = (
        MergeStrategy.ONE_FILE_PER_BATCH if merge else MergeStrategy.ONE_FILE_PER_INPUT
    )
    out_dir = output_dir if output_dir is not None else Path.cwd()

    client = PollyClient()
    results = client.synthesize_batch(requests, out_dir, strategy, pause)
    _print_results(results)


@main.command("synthesize-pair")
@click.argument("text1")
@click.argument("text2")
@click.option(
    "--voice1",
    default="joanna",
    show_default=True,
    help="Voice for the first text (typically English).",
)
@click.option(
    "--voice2",
    default="hans",
    show_default=True,
    help="Voice for the second text (typically L2).",
)
@click.option(
    "--rate",
    default=75,
    show_default=True,
    type=int,
    help="Speech rate as percentage.",
)
@click.option(
    "--pause",
    default=500,
    show_default=True,
    type=int,
    help="Pause between the two texts in ms.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(path_type=Path),
    help="Output file path.",
)
def synthesize_pair(
    text1: str,
    text2: str,
    voice1: str,
    voice2: str,
    rate: int,
    pause: int,
    output: Path | None,
) -> None:
    """Synthesize a pair of texts and stitch them with a pause.

    Creates [TEXT1 audio] [pause] [TEXT2 audio] in a single MP3.
    """
    v1 = resolve_voice(voice1)
    v2 = resolve_voice(voice2)
    req1 = SynthesisRequest(text=text1, voice=v1, rate=rate)
    req2 = SynthesisRequest(text=text2, voice=v2, rate=rate)

    if output is None:
        output = Path.cwd() / f"pair_{text1[:10]}_{text2[:10]}.mp3"

    client = PollyClient()
    result = client.synthesize_pair(text1, req1, text2, req2, output, pause)
    _print_result(result)


@main.command("synthesize-pair-batch")
@click.option(
    "--voice1",
    default="joanna",
    show_default=True,
    help="Voice for first texts (typically English).",
)
@click.option(
    "--voice2",
    default="hans",
    show_default=True,
    help="Voice for second texts (typically L2).",
)
@click.option(
    "--rate",
    default=75,
    show_default=True,
    type=int,
    help="Speech rate as percentage.",
)
@click.option(
    "--pause",
    default=500,
    show_default=True,
    type=int,
    help="Pause between pair segments in ms.",
)
@click.option(
    "--output-dir",
    "-d",
    default=None,
    type=click.Path(path_type=Path),
    help="Output directory. Defaults to current directory.",
)
@click.option(
    "--merge",
    is_flag=True,
    default=False,
    help="Merge all pair outputs into a single file.",
)
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def synthesize_pair_batch(
    voice1: str,
    voice2: str,
    rate: int,
    pause: int,
    output_dir: Path | None,
    merge: bool,
    input_file: Path,
) -> None:
    """Synthesize a batch of text pairs from a JSON file.

    INPUT_FILE should contain a JSON array of [text1, text2] pairs:
    [["strong", "stark"], ["house", "Haus"]]
    """
    v1 = resolve_voice(voice1)
    v2 = resolve_voice(voice2)

    raw = json.loads(input_file.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise click.BadParameter(
            "INPUT_FILE must contain a JSON array of [text1, text2] pairs."
        )

    raw_pairs = cast("list[list[str]]", raw)
    pairs: list[tuple[SynthesisRequest, SynthesisRequest]] = [
        (
            SynthesisRequest(text=p[0], voice=v1, rate=rate),
            SynthesisRequest(text=p[1], voice=v2, rate=rate),
        )
        for p in raw_pairs
    ]

    strategy = (
        MergeStrategy.ONE_FILE_PER_BATCH if merge else MergeStrategy.ONE_FILE_PER_INPUT
    )
    out_dir = output_dir if output_dir is not None else Path.cwd()

    client = PollyClient()
    results = client.synthesize_pair_batch(pairs, out_dir, strategy, pause)
    _print_results(results)
