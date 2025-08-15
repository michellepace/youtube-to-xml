# 🎥 YouTube-to-XML

Convert YouTube transcripts to structured XML format with automatic chapter detection.

**Problem**: Raw YouTube transcripts are unstructured text that LLMs struggle to parse effectively, degrading AI chat responses about video content.

**Solution**: Converts transcripts to XML with semantic chapter elements for improved AI comprehension.

```bash
youtube-to-xml my_transcript.txt
# ✅ Created: transcript_files/my_transcript.xml
```

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

Performance tested with transcripts up to 15,000 lines completing in 0.02 seconds.