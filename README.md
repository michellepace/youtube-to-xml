# 🎥 YouTube-to-XML

Convert YouTube transcripts to structured XML format with automatic chapter detection.

```bash
youtube-to-xml transcript.txt
# ✅ Created: transcript_files/transcript.xml
```

## 🚀 Installation

### Global CLI Tool (Recommended)
```bash
uv tool install git+https://github.com/michellepace/youtube-to-xml.git
youtube-to-xml --help
```

### Development Setup
```bash
git clone https://github.com/michellepace/youtube-to-xml.git
cd youtube-to-xml
uv sync
uv run youtube-to-xml --help
```

## 📋 Usage

### Basic Conversion
```bash
youtube-to-xml my_transcript.txt
```

### Expected Input Format
Your transcript file should start with a chapter title, followed by timestamps and content:

```text
Introduction to Python
0:00
Welcome to this tutorial on Python basics
2:30
Let's start with the fundamentals
Getting Started
15:45
First, we'll install Python
```

### Output
Generates structured XML in `transcript_files/` directory:

```xml
<transcript>
  <chapters>
    <chapter title="Introduction to Python" start_time="0:00">
      0:00
      Welcome to this tutorial on Python basics
      2:30
      Let's start with the fundamentals
    </chapter>
    <chapter title="Getting Started" start_time="15:45">
      15:45
      First, we'll install Python
    </chapter>
  </chapters>
</transcript>
```

## 🎯 Why This Project

**Problem**: Raw YouTube transcripts are unstructured text that LLMs struggle to parse effectively, degrading AI chat responses about video content.

**Solution**: Converts transcripts to XML with semantic chapter elements for improved AI comprehension.

**Key Features**:
- Automatic chapter detection using timestamp patterns
- Valid XML output that parses with standard libraries
- Clear visual error messages for invalid formats
- Long videos: converts approx. 10 hours of transcript in 0.02 seconds

## 🛠️ Development

### Requirements
- Python 3.13+
- UV package manager

### Running Tests
```bash
uv run python -m pytest          # All tests
uv run python -m pytest -v       # Verbose output
```

### Code Quality
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

Performance tested with transcripts up to 15,000 lines completing in 0.02 seconds.