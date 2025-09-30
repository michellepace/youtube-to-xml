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

Convert directly from YouTube URL:
```bash
youtube-to-xml https://youtu.be/Q4gsvJvRjCU

🎬 Processing: https://www.youtube.com/watch?v=Q4gsvJvRjCU
✅ Created: how-claude-code-hooks-save-me-hours-daily.xml
```

Output XML (condensed - 4 chapters, 163 lines total):
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

Manually copy YouTube transcript into a text file, then:

```bash
youtube-to-xml my_transcript.txt
# ✅ Created: my_transcript.xml
```

Copy-Paste Exact YT Format for `my_transcript.txt`:
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

Output XML:
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

## 📊 Technical Details

- **Architecture**: Pure functions with clear module separation
- **Key Modules**: See [CLAUDE.md Key Modules section](CLAUDE.md#key-modules)
- **Dependencies**: Python 3.13+, `yt-dlp` for YouTube downloads, see [pyproject.toml](pyproject.toml)
- **Python Package Management**: [UV](https://docs.astral.sh/uv/concepts/projects/)
- **Test Driven Development**: 123 tests (20 slow, 103 unit, ~102 seconds)
- **Terminology**: Uses TRANSCRIPT terminology throughout codebase, see [docs/terminology.md](docs/terminology.md)

<figure align="center">
  <a href="docs/terminology.md">
    <img src="docs/images/terminology.youtube.jpg" alt="YouTube video interface showing the Transcript panel with timestamp and text displayed on single lines (e.g., '0:02 features in Claude Code and for some'). Orange annotations highlight chapter titles and transcript lines structure.">
  </a>
  <figcaption>YouTube transcript terminology throughout codebase: (click to read)</figcaption>
</figure>

## 🛠️ Development

Setup:
```bash
git clone https://github.com/michellepace/youtube-to-xml.git
cd youtube-to-xml
uv sync
```

Code Quality:
```bash
uv run ruff check --fix           # Lint and auto-fix (see pyproject.toml)
uv run ruff format                # Format code (see pyproject.toml)
```

Testing:
```bash
uv run pytest                     # All tests
uv run pytest -m "slow"           # Only slow tests (internet required)
uv run pytest -m "not slow"       # All tests except slow tests
uv run pre-commit run --all-files # (see .pre-commit-config.yaml)
```

---

## 📕 *Own Notes*

Learnt:
- [CodeRabbit for PR review](https://www.anthropic.com/customers/coderabbit)
- [Use Claude Code Docs](https://github.com/ericbuess/claude-code-docs)
- [Use Claude Code Project Index](https://github.com/ericbuess/claude-code-project-index)
- [Manage MCPs nicely](docs/knowledge/manage-mcps-nicely.md)
- [Git branch workflow](docs/knowledge/git-branch-flow.md)

Open Questions:
- **Q1.** Is there something I could have done better with UV?
- **Q2.** Is my "[architecture](/docs/SPEC.md#architecture--data-flow)" nice (one day I may make it a service)?
- **Q3.** Are [tests](/tests/) clear and sane, or over-engineered?
- **Q4.** Did I do exceptions well - define as type with default messages [exceptions.py](/src/youtube_to_xml/exceptions.py)?
- **Q5.** Is the code clean and clear?
- **Q6.** Was it safe to exclude "XML security" Ruff [S314](pyproject.toml)?

To Do:
- [ ] Evals to prove XML format vs plain. Use Hamel's [simple approach](https://hamel.dev/blog/posts/evals-faq/#q-what-are-llm-evals), then try Braintrust again)
- [ ] If so, improve XML perhaps to [this](docs/knowledge/working-notes.md#better-format). Remove all the white space? JSON?