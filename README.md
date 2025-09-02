# 🎥 YouTube-to-XML

Convert YouTube transcripts to structured XML format with automatic chapter detection.

**Problem**: Raw YouTube transcripts are unstructured text that LLMs struggle to parse effectively, degrading AI chat responses about video content.

**Solution**: Converts transcripts to XML with semantic chapter elements for improved AI comprehension.

![Description](docs/misc/youtube-to-xml-narrow.jpg)

## 🚀 Quick Start

**Prerequisites:** [Install UV](https://docs.astral.sh/uv/getting-started/installation/) first.

### Option 1: Manual Method (Current CLI)

> [!TIP]  
> This installs the tool globally on your system. Only `youtube-to-xml` is available after installation (not `transcript-auto-fetcher`).

For manual transcript processing:

```bash
# Install CLI tool globally
uv tool install git+https://github.com/michellepace/youtube-to-xml.git

# Manually copy YouTube transcript into my_transcript.txt, then:
youtube-to-xml my_transcript.txt
# ✅ Created: transcript_files/my_transcript.xml
```

**Required Format for `my_transcript.txt`:**
```text
Introduction to Cows
0:02
Welcome to this talk about erm.. er
2:30
Let's start with the fundamentals
Washing the cow
15:45
First, we'll start with the patches
```

**Output XML:**
```xml
<?xml version='1.0' encoding='utf-8'?>
<transcript video_title="" upload_date="" duration="" video_url="">
  <chapters>
    <chapter title="Introduction to Cows" start_time="0:02">
      0:02
      Welcome to this talk about erm.. er
      2:30
      Let's start with the fundamentals</chapter>
    <chapter title="Washing the cow" start_time="15:45">
      15:45
      First, we'll start with the patches</chapter>
  </chapters>
</transcript>
```

### Option 2: Automated (Experimental)

> [!WARNING]  
> **Experimental - Clone Required**: This entry point only works when run from a cloned repository. It cannot be installed globally as the `scripts/` directory is not packaged.

Get YouTube transcripts directly from URL:

```bash
git clone https://github.com/michellepace/youtube-to-xml.git
cd youtube-to-xml
uv sync
uv run transcript-auto-fetcher https://youtu.be/Q4gsvJvRjCU
```

**Output:**
```
🎬 Processing: https://www.youtube.com/watch?v=Q4gsvJvRjCU
📊 Fetching video metadata...
   Title: How Claude Code Hooks Save Me HOURS Daily
   Duration: 2m 43s
📝 Downloading subtitles...
   Parsed 75 subtitles
📑 Organising into 4 chapter(s)...
🔧 Building XML document...
✅ Created: /home/mp/projects/python/youtube-to-xml/how-claude-code-hooks-save-me-hours-daily.xml
```

**Features:**
- ✅ Downloads video metadata (title, duration, upload date)
- ✅ Downloads video subtitles (i.e. transcript content)
- ✅ Organises subtitles by video chapters automatically
- ✅ Prioritises manual subtitles over auto-generated ones
- ✅ Creates structured XML output

> **Note:** The main CLI will be enhanced (and refactored) to integrate this automated functionality, eliminating the need for the experimental script.

## 🛠️ Development

**Setup:**
```bash
git clone https://github.com/michellepace/youtube-to-xml.git
cd youtube-to-xml
uv sync
```

**Testing:**
```bash
uv run pytest                    # All tests
uv run pytest -v                 # Verbose output
```

**Code Quality:**
```bash
uv run ruff check                 # Lint
uv run ruff format                # Format
uv run pre-commit run --all-files # All hooks
```

## 📊 Technical Details

Built with Test-Driven Development using:
- **Parser**: Regex-based timestamp detection and chapter boundary rules
- **XML Builder**: ElementTree API for valid XML generation
- **CLI**: Argparse with comprehensive error handling
- **Architecture**: Pure functions with clear module separation
- **Dependencies**:
  - Runtime Dependencies: `yt-dlp` (fetch transcript and metadata from YouTube URL). This is currently used by the experimental [scripts/transcript_auto_fetcher.py](scripts/transcript_auto_fetcher.py) only.
  - Dev Dependencies: `pytest`, `ruff`, `pre-commit`
- **Package Management**: UV Package Application

Performance tested with transcripts up to 15,000 lines completing in 0.02 seconds.

## 📕 Notes

**What I Learnt**
- [Manage MCPs Nicely](docs/misc/manage-mcps-nicely.md)
- [Git Branch Workflow](docs/misc/git-branch-flow.md)
- [Code Rabbit for PR review](https://www.anthropic.com/customers/coderabbit)
- Next time: [Claude Code Docs](https://github.com/ericbuess/claude-code-docs) & [Project Index](https://github.com/ericbuess/claude-code-project-index) (see [chat](https://claude.ai/chat/c70ff077-6ebb-4c75-bf2b-74e31d2cb649))

**Outstanding Questions**
- **Q1.** Is there something I could have done better with UV?
- **Q2.** Is my "[architecture](/docs/SPEC.md#architecture--data-flow)" nice (one day I may make it a service)?
- **Q3.** Are my [tests](/tests/) clear and sane, or did I seriously overcomplicate / over cook it?
- **Q4.** Did I do the errors properly (make them a type, define in [exceptions.py](/src/youtube_to_xml/exceptions.py), customising messages in [cli.py](/src/youtube_to_xml/cli.py))?
- **Q5.** Is the code "clean"... was I right to make private methods in parser.py and only expose one public function. It was at the cost of direct testability, but does it matter?
- **Q6.** Was I right to exclude the "XML security" Ruff [S314](pyproject.toml), as I'm generating xml only.

**To Do**
1. Evals to prove XML format vs plain (myself here, then Braintrust)
2. If so, improve XML perhaps to [this](docs/misc/working-notes.md#better-format). I don't think so, disjoint.
3. Integrate experimental [scripts/transcript_auto_fetcher.py](scripts/transcript_auto_fetcher.py) functionality into main CLI, then remove the standalone script.