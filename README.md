# 🎥 YouTube-to-XML

Convert YouTube transcripts to structured XML format with automatic chapter detection.

**Problem**: Raw YouTube transcripts are unstructured text that LLMs struggle to parse effectively, degrading AI chat responses about video content.

**Solution**: Converts transcripts to XML with semantic chapter elements for improved AI comprehension.

![Description](docs/images/youtube-to-xml-narrow.jpg)

## 🚀 Quick Start

**Prerequisites:** [Install UV](https://docs.astral.sh/uv/getting-started/installation/) first.

### Option 1: File Method

> [!TIP]  
> This installs **both** `youtube-to-xml` and `transcript-auto-fetcher` commands globally. Both commands work fully after installation.

```bash
# Install CLI tool globally
uv tool install git+https://github.com/michellepace/youtube-to-xml.git

# Manually copy YouTube transcript into my_transcript.txt, then:
youtube-to-xml my_transcript.txt
# ✅ Created: my_transcript.xml
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

> 📁 **[View example files →](example_transcripts/introduction-to-cows.txt)** | **[Generated XML →](example_transcripts/introduction-to-cows.xml)**

### Option 2: URL Method (Experimental)

> [!CAUTION]  
> This is experimental because it's a separate script pending integration into the main CLI.

```bash
# Use the globally installed command (after Option 1 installation)
transcript-auto-fetcher https://youtu.be/Q4gsvJvRjCU

🎬 Processing: https://www.youtube.com/watch?v=Q4gsvJvRjCU
📊 Fetching video metadata...
   Title: How Claude Code Hooks Save Me HOURS Daily
   Duration: 2m 43s
📝 Downloading subtitles...
   Parsed 75 subtitles
📑 Organising into 4 chapter(s)...
🔧 Building XML document...
✅ Created: how-claude-code-hooks-save-me-hours-daily.xml
```

**Output XML (condensed - 5 chapters, 163 lines total):**
```xml
<?xml version='1.0' encoding='utf-8'?>
<transcript video_title="How Claude Code Hooks Save Me HOURS Daily" 
            upload_date="2025-07-12" 
            duration="2m 43s" 
            video_url="https://www.youtube.com/watch?v=Q4gsvJvRjCU">
  <chapters>
    <chapter title="Intro" start_time="0:00">
      0:00
      Hooks are hands down one of the best
      0:02
      features in Claude Code and for some
      <!-- ... more transcript content ... -->
    </chapter>
    <chapter title="Hooks" start_time="0:19">
      0:20
      To create your first hook, use the hooks
      <!-- ... more transcript content ... -->
    </chapter>
    <!-- ... 3 more chapters ... -->
  </chapters>
</transcript>
```

> 📁 **[View complete XML output →](example_transcripts/how-claude-code-hooks-save-me-hours-daily.xml)**

**Features:**
- ✅ Downloads video metadata and subtitles (transcript content)
- ✅ Output XML structure matches the file method
- ✅ The attributes are all populated with video metadata

## 📊 Technical Details

Built with Test-Driven Development using:
- **Key Modules**
   - **[cli.py](src/youtube_to_xml/cli.py)** — Argparse with error handling and structured logging
   - **[parser.py](src/youtube_to_xml/parser.py)** — Regex-based timestamp detection and chapter boundary rules
   - **[xml_builder.py](src/youtube_to_xml/xml_builder.py)** — ElementTree API for valid XML generation
   - **[exceptions.py](src/youtube_to_xml/exceptions.py)** — Custom error hierarchy for clean error handling
- **Architecture**: Pure functions with clear module separation
- **Dependencies**:
  - Runtime Dependencies: `yt-dlp` (fetch transcript and metadata from YouTube URL)
  - Dev Dependencies: `pytest`, `ruff`, `pre-commit`
- **Package Management**: UV Package Application

Performance tested with transcripts up to 15,000 lines completing in 0.02 seconds

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

## 📕 Notes

**What I Learnt**
- [Manage MCPs Nicely](docs/knowledge/manage-mcps-nicely.md)
- [Git Branch Workflow](docs/knowledge/git-branch-flow.md)
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
2. If so, improve XML perhaps to [this](docs/knowledge/working-notes.md#better-format). I don't think so, disjoint.
3. Integrate experimental [scripts/transcript_auto_fetcher.py](scripts/transcript_auto_fetcher.py) functionality into main CLI, then remove the standalone script.