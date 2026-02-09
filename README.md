# langlearn-tts

[![PyPI](https://img.shields.io/pypi/v/langlearn-tts)](https://pypi.org/project/langlearn-tts/)
[![GitHub](https://img.shields.io/github/v/release/jmf-pobox/langlearn-tts-mcp)](https://github.com/jmf-pobox/langlearn-tts-mcp)
[![Tests](https://github.com/jmf-pobox/langlearn-tts-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/jmf-pobox/langlearn-tts-mcp/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/langlearn-tts)](https://pypi.org/project/langlearn-tts/)

Generate audio flashcards and vocabulary drills from text. Ask Claude to synthesize words and phrases in any language, or batch-process entire vocabulary lists from the command line. Audio is slowed to 90% speed by default so learners can hear pronunciation clearly.

The pair mode is the core workflow: give it an English word and its translation, and it produces a single MP3 — `[English audio] [pause] [target language audio]` — ready for Anki, spaced repetition, or passive listening.

Available as both a **Claude Desktop MCP server** (ask Claude to generate audio in conversation) and a **CLI** with identical functionality. Currently supports **AWS Polly**; **ElevenLabs** and **OpenAI TTS** backends are planned so you can pick the provider that fits your setup.

## Features

- **Single synthesis** — convert text to MP3 in any supported language
- **Batch synthesis** — synthesize multiple texts, optionally merged into one file
- **Pair synthesis** — stitch two languages together: `[English] [pause] [L2]`
- **Pair batch** — batch-process vocabulary lists as stitched pairs
- **Auto-play** — MCP tools play audio immediately after synthesis
- **Configurable speech rate** — default 90% for learner-friendly pacing
- **93 voices, 41 languages** — any [AWS Polly voice](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html) works out of the box

## Quick Start

### 1. Install uv (Python package manager)

If you don't have `uv` yet:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

uv manages Python versions automatically — you don't need to install Python separately.

### 2. Install langlearn-tts

```bash
uv tool install langlearn-tts
```

This installs the `langlearn-tts` CLI and `langlearn-tts-server` MCP server globally.

### 3. Install ffmpeg

Required for audio stitching (pairs, merged batches). Single synthesis works without it.

```bash
# macOS (requires Homebrew — install from https://brew.sh if needed)
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

### 4. Configure AWS credentials

The tool uses AWS Polly, which requires an AWS account with `polly:SynthesizeSpeech` and `polly:DescribeVoices` permissions.

**Option A — AWS CLI (recommended):**

Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), then:

```bash
aws configure
```

Enter your Access Key ID, Secret Access Key, and region (e.g., `us-east-1`).

**Option B — Environment variables:**

```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

**Option C — Credentials file** (`~/.aws/credentials`):

```ini
[default]
aws_access_key_id = your-key
aws_secret_access_key = your-secret
region = us-east-1
```

### 5. Verify

```bash
langlearn-tts doctor
```

All required checks should show `✓`. Fix any that show `✗` before continuing.

### From source (development)

```bash
git clone https://github.com/jmf-pobox/langlearn-tts-mcp.git
cd langlearn-tts-mcp
uv sync --all-extras
uv run langlearn-tts --help
```

## Claude Desktop Setup

### Automatic (recommended)

```bash
langlearn-tts install
```

This registers the MCP server with Claude Desktop. Options:

- `--output-dir PATH` — custom audio output directory (default: `~/Claude-Audio`)
- `--uvx-path PATH` — override the `uvx` binary path

Restart Claude Desktop after running `install`.

### Manual

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "langlearn-tts": {
      "command": "/absolute/path/to/uvx",
      "args": ["--from", "langlearn-tts", "langlearn-tts-server"],
      "env": {
        "LANGLEARN_TTS_OUTPUT_DIR": "/absolute/path/to/output/directory"
      }
    }
  }
}
```

Claude Desktop does not inherit your shell PATH. All paths must be absolute. Find your `uvx` path with `which uvx`.

The `LANGLEARN_TTS_OUTPUT_DIR` environment variable sets the default output directory. If unset, files are saved to `~/Claude-Audio/`.

Restart Claude Desktop after editing the config.

## AI Tutor Prompts

langlearn-tts ships with 28 ready-made AI tutor prompts — one for each combination of 7 languages and 4 levels. Paste a prompt into a Claude Desktop Project's Instructions field, and Claude becomes a language tutor that generates audio during lessons.

### Browse prompts

```bash
# List all available prompts
langlearn-tts prompt list

# Print a prompt (pipe to clipboard with pbcopy on macOS)
langlearn-tts prompt show german-high-school | pbcopy
```

### Set up a Claude Desktop Project

1. In Claude Desktop, click **Projects** in the sidebar
2. Click **Create Project** and name it (e.g., "German with Herr Schmidt")
3. Open the project, click **Set custom instructions**
4. Paste the prompt content into the Instructions field
5. Start a new conversation within that project

Using a Project keeps the tutor persona scoped to language learning. Other conversations are unaffected.

### Available languages and levels

| Language | High School | 1st Year | 2nd Year | Advanced |
|----------|-------------|----------|----------|----------|
| German | Herr Schmidt | Professorin Weber | Professor Hartmann | Professor Becker |
| Spanish | Profesora Elena | Profesor Garcia | Profesora Carmen | Profesora Reyes |
| French | Madame Moreau | Professeur Laurent | Professeur Dubois | Professeur Beaumont |
| Russian | Irina Petrovna | Professor Dmitri | Professor Natasha | Professor Mikhail |
| Korean | Kim-seonsaengnim | Professor Park | Professor Kim | Professor Yoon |
| Japanese | Tanaka-sensei | Yamamoto-sensei | Suzuki-sensei | Mori-sensei |
| Chinese | Laoshi Wang | Professor Chen | Professor Zhang | Professor Wei |

Each prompt creates a tutor persona calibrated to the student's level, based on [Mollick & Mollick's "Assigning AI" framework](https://ssrn.com/abstract=4475995). Customize any prompt by adjusting student background, voice selection, speech rate, or focus areas.

## Troubleshooting

```bash
langlearn-tts doctor
```

Checks Python version, ffmpeg, AWS credentials, Polly access, `uvx`, Claude Desktop config, and output directory. Required checks must pass (exit code 1 on failure); optional checks show `○` markers.

## Voices

Any voice from the [AWS Polly voice list](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html) is supported. Voice names are case-insensitive. The tool queries the Polly API on first use and caches the result.

Common voices for language learning:

| Voice | Language | Engine |
|-------|----------|--------|
| joanna | English (US) | neural |
| matthew | English (US) | neural |
| daniel | German | neural |
| vicki | German (female) | neural |
| lucia | Spanish (European) | neural |
| lupe | Spanish (US) | neural |
| léa | French | neural |
| tatyana | Russian | standard |
| seoyeon | Korean | neural |
| takumi | Japanese | neural |
| zhiyu | Chinese (Mandarin) | neural |

The engine (neural, standard, generative, long-form) is selected automatically — neural preferred when available.

## CLI Usage

```bash
# Single synthesis
langlearn-tts synthesize "Guten Morgen" --voice daniel -o morning.mp3

# Custom speech rate (percentage, default 90)
langlearn-tts synthesize "Привет" --voice tatyana --rate 70 -o privet.mp3

# Pair: English + German stitched with a pause
langlearn-tts synthesize-pair "good morning" "Guten Morgen" \
  --voice1 joanna --voice2 daniel -o pair.mp3

# Batch from JSON file (["hello", "world", "good morning"])
langlearn-tts synthesize-batch words.json -d output/

# Batch merged into single file
langlearn-tts synthesize-batch words.json -d output/ --merge --pause 800

# Pair batch from JSON file ([["strong", "stark"], ["house", "Haus"]])
langlearn-tts synthesize-pair-batch pairs.json -d output/

# Browse AI tutor prompts
langlearn-tts prompt list
langlearn-tts prompt show german-high-school | pbcopy
```

## MCP Tools

All four tools are available in Claude Desktop once the server is configured:

| Tool | Description |
|------|-------------|
| `synthesize` | Single text to MP3 |
| `synthesize_batch` | Multiple texts, optionally merged |
| `synthesize_pair` | Two texts stitched with a pause |
| `synthesize_pair_batch` | Multiple pairs, optionally merged |

Each tool accepts `auto_play` (default: true) to play audio immediately after synthesis.

## Roadmap

### Provider Abstraction Layer

A `TTSProvider` protocol that decouples CLI/MCP tools from any specific backend. Enables `--provider` flag, provider auto-detection from API keys, and provider-specific `doctor` checks.

### ElevenLabs Backend

Highest voice quality. 29+ languages, 5,000+ voices, voice cloning. Setup: `pip install langlearn-tts[elevenlabs]` + `ELEVENLABS_API_KEY` env var. Free tier: 10K chars/month.

### OpenAI TTS Backend

Broadest adoption — most users already have an OpenAI key. 6 built-in voices, 50+ languages. Setup: `pip install langlearn-tts[openai]` + `OPENAI_API_KEY` env var. $15/1M chars (tts-1).

## Development

```bash
# Install with dev dependencies
uv sync --all-extras

# Run tests
uv run pytest tests/ -v

# Linting and formatting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type checking
uv run mypy src/ tests/
uv run pyright src/ tests/
```

## License

MIT
