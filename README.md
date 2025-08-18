# 🎥 YouTube-to-XML

Convert YouTube transcripts to structured XML format with automatic chapter detection.

**Problem**: Raw YouTube transcripts are unstructured text that LLMs struggle to parse effectively, degrading AI chat responses about video content.

**Solution**: Converts transcripts to XML with semantic chapter elements for improved AI comprehension.

```bash
youtube-to-xml my_transcript.txt
# ✅ Created: transcript_files/my_transcript.xml
```

![Description](docs/misc/youtube-to-xml-narrow.jpg)

## 🚀 Installation

**Prerequisites**

UV must be installed first on your machine, follow the [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

**Use as a Command Line Tool (recommended)**

```bash
uv tool install git+https://github.com/michellepace/youtube-to-xml.git
youtube-to-xml --help
```

**Clone to Develop Further**

```bash
git clone https://github.com/michellepace/youtube-to-xml.git
cd youtube-to-xml
uv sync
uv run youtube-to-xml --help
```

## 📋 Usage

**Basic Steps**

1. Manually copy a YouTube transcript into a .txt file (sorry)

2. Then run this command
   ```bash
   youtube-to-xml my_transcript.txt
   ```

3. Upload `my_transcript.xml` into a claude.ai project, chat, or other LLM

**Required Format for `my_transcript.txt` (input)**

Your transcript file should start with a chapter title, followed by timestamps and content:

```text
Introduction to Cows
0:02
Welcome to this talk about erm.. er
2:30
Let's start with the fundamentals
Washing the cow
15:45
First, we'll start with the patches
11:59:59
That took a long time
12:04:27
Usually it s much quicker
```

**Transcript in XML `my_transcript.xml` (output)**

Generates structured XML in `transcript_files/` directory:

```xml
<?xml version='1.0' encoding='utf-8'?>
<transcript>
  <chapters>
    <chapter title="Introduction to Cows" start_time="0:02">
      0:02
      Welcome to this talk about erm.. er
      2:30
      Let's start with the fundamentals</chapter>
    <chapter title="Washing the cow" start_time="15:45">
      15:45
      First, we'll start with the patches
      11:59:59
      That took a long time
      12:04:27
      Usually it s much quicker</chapter>
  </chapters>
</transcript>
```

## 🛠️ Development

**Requirements**

- Python 3.13+
- UV package manager [installed](https://docs.astral.sh/uv/getting-started/installation/)

**How to Run Tests**

```bash
uv run python -m pytest          # All tests
uv run python -m pytest -v       # Verbose output
```

**Code Quality Automation**

```bash
uv run ruff check                 # Lint
uv run ruff format                # Format
uv run pre-commit run --all-files # All hooks (uv-sync, pytest, ruff)
```

## 📊 Technical Details

Built with Test-Driven Development using:
- **Parser**: Regex-based timestamp detection and chapter boundary rules
- **XML Builder**: ElementTree API for valid XML generation
- **CLI**: Argparse with comprehensive error handling
- **Architecture**: Pure functions with clear module separation
- **Dependencies**: None
- **Package & Project Management**: UV Package Application (see [here](https://docs.astral.sh/uv/concepts/projects/) and [why](https://docs.astral.sh/uv/concepts/projects/config/#project-packaging))

Performance tested with transcripts up to 15,000 lines completing in 0.02 seconds.

## 📕 Notes

**What I Learnt**
- [Manage MCPs Nicely](docs/misc/manage-mcps-nicely.md)
- [Git Branch Workflow](docs/misc/git-branch-flow.md)
- [Code Rabbit for PR review](https://www.anthropic.com/customers/coderabbit)
- Next time: [Claude Code Docs](https://github.com/ericbuess/claude-code-docs) & [Project Index](https://github.com/ericbuess/claude-code-project-index) (see [chat](https://claude.ai/chat/c70ff077-6ebb-4c75-bf2b-74e31d2cb649))

**Outstanding Questions**
- **Q1.** Is there something I could have done better with UV ?
- **Q2.** Is my "[architecture](/docs/SPEC.md#architecture--data-flow)" nice (one day I may make it a service)?
- **Q3.** Are my [tests](/tests/) clear and sane, or did I seriously overcomplicate / over cook it?
- **Q4.** Did I do the errors properly (make them a type, define in [exceptions.py](/src/youtube_to_xml/exceptions.py), customising messages in [cli.py](/src/youtube_to_xml/cli.py))?
- **Q5.** Is the code "clean"... was I right to make private methods in parser.py and only expose one public function. It was at the cost of direct testability, but does it matter?
- **Q6.** Was I right to exclude the "XML security" Ruff [S314](pyproject.toml), as I'm generating xml only.

**To Do**
1. Evals to prove XML format vs plain (myself here, then Braintrust)
2. If so, improve XML perhaps to [this](docs/misc/working-notes.md#better-format). I don't think so, disjoint.
3. Refactor everything to do "Transcript from URL" as scripted [here](scripts/youtube_transcript_fetcher.py)