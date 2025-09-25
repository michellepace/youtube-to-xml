# 🎥 YouTube-to-XML

Convert YouTube transcripts to structured XML format with automatic chapter detection.

**Problem**: Raw YouTube transcripts are unstructured text that LLMs struggle to parse, degrading AI chat responses about video content.

**Solution**: Converts transcripts to XML with chapter elements for improved AI comprehension.

![Description](docs/images/readme.cover.skinny.md)

## 📦 Install

(1) First, install UV Python Package and Project Manager [from here](https://docs.astral.sh/uv/getting-started/installation/).

(2) Then, install `youtube-to-xml` accessible from anywhere in your terminal:
```bash
uv tool install git+https://github.com/michellepace/youtube-to-xml.git
```

## 🚀 Usage

The `youtube-to-xml` command intelligently auto-detects whether you're providing a YouTube URL or a transcript file.

### Option 1: URL Method (Easiest)

```bash
# Convert directly from YouTube URL
youtube-to-xml https://youtu.be/Q4gsvJvRjCU

🎬 Processing: https://www.youtube.com/watch?v=Q4gsvJvRjCU
✅ Created: how-claude-code-hooks-save-me-hours-daily.xml
```

**Output XML (condensed - 4 chapters, 163 lines total):**
```xml
<?xml version='1.0' encoding='utf-8'?>
<transcript video_title="How Claude Code Hooks Save Me HOURS Daily"
            video_published="2025-07-12"
            video_duration="2m 43s"
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
    <!-- ... 2 more chapters ... -->
  </chapters>
</transcript>
```

> 📁 **[View Output XML →](example_transcripts/how-claude-code-hooks-save-me-hours-daily.xml)**

### Option 2: File Method

```bash
# Manually copy YouTube transcript into a text file, then:
youtube-to-xml my_transcript.txt
# ✅ Created: my_transcript.xml
```

**Copy-Paste Exact YT Format for `my_transcript.txt`:**
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
<transcript video_title="" video_published="" video_duration="" video_url="">
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

> 📁 **[View example files →](example_transcripts/introduction-to-cows.txt)** | **[Output XML →](example_transcripts/introduction-to-cows.xml)**

*Output structure matches the URL method but with empty metadata attributes (title, duration, etc.)*

<figure align="center">
  <a href="docs/terminology.md">
    <img src="docs/images/terminology.youtube.jpg" alt="YouTube video interface showing the Transcript panel with timestamp and text displayed on single lines (e.g., '0:02 features in Claude Code and for some'). Orange annotations highlight chapter titles and transcript lines structure.">
  </a>
  <figcaption>YouTube transcript terminology used throughout code: (click to read)</figcaption>
</figure>

## 📊 Technical Details

**Terminology**: Code uses consistent TRANSCRIPT terminology. **[View terminology guide →](docs/terminology.md)**

**Package & Project Management**: [UV Package Application](https://docs.astral.sh/uv/concepts/projects/)

**Architecture**: Pure functions with clear module separation

**Test-Driven Development**: 123 tests (17 integration, 106 unit, ~68 seconds)

**Dependencies**:
- Runtime Dependencies: `yt-dlp` (fetch metadata and download transcript from YouTube URL)
- Dev Dependencies: `pytest`, `ruff`, `pre-commit`

**Key Modules**
- **[cli.py](src/youtube_to_xml/cli.py)** — Unified CLI with intelligent auto-detection (URLs vs .txt files)
- **[file_parser.py](src/youtube_to_xml/file_parser.py)** — Regex-based timestamp detection and chapter boundary rules
- **[url_parser.py](src/youtube_to_xml/url_parser.py)** — YouTube URL processing with metadata extraction
- **[xml_builder.py](src/youtube_to_xml/xml_builder.py)** — ElementTree API for valid XML generation
- **[exceptions.py](src/youtube_to_xml/exceptions.py)** — Custom error hierarchy for clean error handling
- **[test_end_to_end.py](tests/test_end_to_end.py)** — Workflow tests for file and URL processing

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

---

## 📕 *Own Notes*

**Learning Notes**
- [Code Rabbit for PR review](https://www.anthropic.com/customers/coderabbit)
- [Use Claude Code Docs](https://github.com/ericbuess/claude-code-docs)
- [Use Claude Code Project Index](https://github.com/ericbuess/claude-code-project-index)
- [Manage MCPs Nicely](docs/knowledge/manage-mcps-nicely.md)
- [Git Branch Workflow](docs/knowledge/git-branch-flow.md)

**Outstanding Questions**
- **Q1.** Is there something I could have done better with UV?
- **Q2.** Is my "[architecture](/docs/SPEC.md#architecture--data-flow)" nice (one day I may make it a service)?
- **Q3.** Are my [tests](/tests/) clear and sane, or did I seriously overcomplicate / over cook it?
- **Q4.** Did I do the errors properly (make them a type, define in [exceptions.py](/src/youtube_to_xml/exceptions.py), customising messages in [cli.py](/src/youtube_to_xml/cli.py))?
- **Q5.** Is the code "clean"... was I right to make private methods in file_parser.py and only expose one public function. It was at the cost of direct testability, but does it matter?
- **Q6.** Was I right to exclude the "XML security" Ruff [S314](pyproject.toml), as I'm generating xml only.

**To Do**
1. ~~Integrate URL functionality into main CLI~~ ✅ COMPLETE (unified CLI with auto-detection)
2. Evals to prove XML format vs plain (Use Hamels [simple approach](https://hamel.dev/blog/posts/evals-faq/#q-what-are-llm-evals), then try Braintrust again)
3. If so, improve XML perhaps to [this](docs/knowledge/working-notes.md#better-format). Remove all the white space? JSON?