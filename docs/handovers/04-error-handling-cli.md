# YouTube-to-XML Error Handling Pattern & Implementation Guide

## The Pattern: Context-Free Exceptions with Presentation Layers

### Core Principle
Each layer of your application has a specific responsibility:
- **Parser**: Detects and raises specific exception types with technical messages
- **Exceptions**: Define error types and carry context-free problem descriptions  
- **CLI**: Catches exceptions and formats them for command-line users
- **Future API**: Will catch the same exceptions and format for HTTP/JSON responses
- **Tests**: Verify only exception types, not message content

### Why This Pattern Is Ideal

1. **Portability**: Your parser module can be used in CLI, API, or any other context without modification
2. **Maintainability**: Error messages can be refined without breaking tests
3. **Clarity**: Each exception type clearly indicates what went wrong
4. **No Duplication**: Core error information lives in one place (exception classes)
5. **Future-Proof**: When you build your Next.js service, the same parser and exceptions work perfectly

### Architecture Diagram
```
Parser Module          Exceptions Module        Presentation Layers
─────────────         ─────────────────        ──────────────────
                                               
parse_transcript() ──> EmptyFileError          CLI (cli.py)
                      "Cannot parse empty      ├─> "❌ Your file is empty: video.txt"
                       transcript file"        
                                               API endpoint  
                      InvalidTranscriptFormat  ├─> {"error": "invalid_format",
                      "Must start with         │    "details": "Must start with...",
                       chapter title"          │    "status": 400}
                                               
                      MissingTimestampError    GUI (future)
                      "Must contain at least   └─> Dialog box with error icon
                       one timestamp"
```

## Important Note: CLI Separation for Clarity

**For better separation of concerns**, the CLI implementation is placed in a dedicated `cli.py` file rather than `__init__.py`. This makes the distinction between package initialization and CLI functionality explicit. This requires updating the entry point in `pyproject.toml`:

```toml
[project.scripts]
youtube-to-xml = "youtube_to_xml.cli:main"  # Note: .cli module, not root package
```

This separation also makes future expansion cleaner - API endpoints, GUIs, or other entry points can be added as sibling modules without cluttering the package root.

## Your Implementation Path

### Step 1: Create `src/youtube_to_xml/exceptions.py`

Create a new file with your custom exception classes:

```python
"""Custom exceptions for YouTube transcript processing."""


class EmptyFileError(ValueError):
    """Raised when attempting to parse an empty transcript file."""
    
    def __init__(self, message: str = "Cannot parse an empty transcript file") -> None:
        super().__init__(message)


class InvalidTranscriptFormatError(ValueError):
    """Raised when transcript doesn't follow required format."""
    
    def __init__(
        self, 
        message: str = "Transcript must start with a chapter title, not a timestamp"
    ) -> None:
        super().__init__(message)


class MissingTimestampError(ValueError):
    """Raised when transcript contains no timestamps."""
    
    def __init__(
        self, 
        message: str = "Transcript must contain at least one timestamp"
    ) -> None:
        super().__init__(message)
```

### Step 2: Update `src/youtube_to_xml/parser.py`

Add import at the top:
```python
from youtube_to_xml.exceptions import (
    EmptyFileError,
    InvalidTranscriptFormatError,
    MissingTimestampError,
)
```

Update the `validate_transcript_format` function to raise custom exceptions:

**Change from:**
```python
if not raw_transcript.strip():
    msg = "Your file is empty"
    raise ValueError(msg)
```

**To:**
```python
if not raw_transcript.strip():
    raise EmptyFileError()
```

**Change from:**
```python
if transcript_lines and TIMESTAMP_PATTERN.match(transcript_lines[0].strip()):
    msg = "Wrong format - transcript must start with a chapter title, not a timestamp"
    raise ValueError(msg)
```

**To:**
```python
if transcript_lines and TIMESTAMP_PATTERN.match(transcript_lines[0].strip()):
    raise InvalidTranscriptFormatError()
```

**Change from:**
```python
if not timestamp_indices:
    msg = "Wrong format - transcript must contain at least one timestamp"
    raise ValueError(msg)
```

**To:**
```python
if not timestamp_indices:
    raise MissingTimestampError()
```

### Step 3: Update `tests/test_parser.py`

Add import at the top:
```python
from youtube_to_xml.exceptions import (
    EmptyFileError,
    InvalidTranscriptFormatError,
    MissingTimestampError,
)
```

Update test assertions to check exception types instead of message strings:

**Example changes:**

```python
# OLD: String matching
def test_rejects_transcript_starting_with_timestamp() -> None:
    with pytest.raises(ValueError, match="timestamp"):
        parse_transcript(starts_with_timestamp)

# NEW: Type checking
def test_rejects_transcript_starting_with_timestamp() -> None:
    with pytest.raises(InvalidTranscriptFormatError):
        parse_transcript(starts_with_timestamp)
```

For any test currently checking `ValueError`, determine which specific exception it should expect:
- Empty file tests → `EmptyFileError`
- Format validation tests → `InvalidTranscriptFormatError`  
- Missing timestamp tests → `MissingTimestampError`

### Step 4: Create `src/youtube_to_xml/cli.py`

Create a new file with the complete CLI implementation:

```python
"""YouTube to XML converter CLI entry point."""

import argparse
import sys
from pathlib import Path

from youtube_to_xml.exceptions import (
    EmptyFileError,
    InvalidTranscriptFormatError,
    MissingTimestampError,
)
from youtube_to_xml.parser import parse_transcript
from youtube_to_xml.xml_builder import chapters_to_xml


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="youtube-to-xml",
        description="Convert YouTube transcripts to XML format with chapter detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
✅ Example YouTube Transcript

📋 EXPECTED FORMAT:
   ┌─────────────────────────────────────────
   │ Introduction to Bret Taylor
   │ 00:04
   │ You're CTO of Meta and and co-CEO of...
   └─────────────────────────────────────────

🔧 REQUIREMENTS:
   - Must start with a chapter title (non-timestamp line)
   - Second line must be a timestamp
   - Third line must be content (non-timestamp line)

💡 Check that your transcript follows this basic pattern
""",
    )
    parser.add_argument(
        "transcript",
        metavar="transcript.txt",
        help="YouTube transcript text file to convert",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for YouTube to XML converter."""
    args = parse_arguments()
    transcript_path = Path(args.transcript)
    
    # Read the input file
    try:
        raw_content = transcript_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ We couldn't find your file: {transcript_path}")
        sys.exit(1)
    except PermissionError:
        print(f"❌ We don't have permission to access: {transcript_path}")
        sys.exit(1)
    
    # Parse the transcript
    try:
        chapters = parse_transcript(raw_content)
    except EmptyFileError:
        print(f"❌ Your file is empty: {transcript_path}")
        sys.exit(1)
    except (InvalidTranscriptFormatError, MissingTimestampError):
        print(f"❌ Wrong format in '{transcript_path}' - run 'youtube-to-xml --help'")
        sys.exit(1)
    
    # Generate XML
    xml_content = chapters_to_xml(chapters)
    
    # Create output directory and write XML
    output_dir = Path("transcript_files")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_filename = transcript_path.stem + ".xml"
    output_path = output_dir / output_filename
    
    try:
        output_path.write_text(xml_content, encoding="utf-8")
    except PermissionError:
        print(f"❌ Cannot write to: {output_path}")
        sys.exit(1)
    
    # Success message
    print(f"✅ Created: {output_path}")
```

### Step 5: Update `src/youtube_to_xml/__init__.py`

Keep this file empty or minimal - it only needs to mark the directory as a Python package:

```python
"""YouTube to XML converter package."""
```

### Step 6: Update `pyproject.toml`

Update the entry point to reference the cli module:

```toml
[project.scripts]
youtube-to-xml = "youtube_to_xml.cli:main"
```

## Testing Your Implementation

After making these changes:

1. **Run existing tests** to ensure they pass with new exception types:
   ```bash
   uv run pytest
   ```

2. **Test the CLI manually**:
   ```bash
   # Valid transcript
   uv run youtube-to-xml sample.txt
   
   # Missing file
   uv run youtube-to-xml nonexistent.txt
   
   # Empty file
   echo "" > empty.txt
   uv run youtube-to-xml empty.txt
   
   # Invalid format (starts with timestamp)
   echo "0:00" > invalid.txt
   echo "Content" >> invalid.txt
   uv run youtube-to-xml invalid.txt
   ```

3. **Verify help message**:
   ```bash
   uv run youtube-to-xml --help
   ```

4. **Create `tests/test_cli.py`** to test CLI functionality:
   ```python
   """Tests for CLI functionality."""
   
   import subprocess
   from pathlib import Path
   
   import pytest
   
   
   def test_valid_transcript_creates_xml(tmp_path: Path) -> None:
       """Test that valid transcript produces XML output."""
       # Create test file in tmp directory
       test_file = tmp_path / "test.txt"
       test_file.write_text("Chapter One\n0:00\nContent here", encoding="utf-8")
       
       # Run CLI from tmp directory to isolate all file operations
       result = subprocess.run(
           ["uv", "run", "youtube-to-xml", "test.txt"],
           capture_output=True,
           text=True,
           cwd=tmp_path,  # Run from tmp directory
       )
       
       # Check success
       assert result.returncode == 0
       assert "Created:" in result.stdout
       
       # Verify output file exists in tmp location
       output_file = tmp_path / "transcript_files" / "test.xml"
       assert output_file.exists()
   
   
   def test_missing_file_shows_error(tmp_path: Path) -> None:
       """Test error message for missing file."""
       result = subprocess.run(
           ["uv", "run", "youtube-to-xml", "nonexistent.txt"],
           capture_output=True,
           text=True,
           cwd=tmp_path,  # Run from tmp directory for consistency
       )
       
       assert result.returncode == 1
       assert "couldn't find your file" in result.stdout
   ```
   
   **Note**: Using `cwd=tmp_path` ensures all file operations happen in the temporary directory, preventing test pollution of your project directory. This follows the same isolation principle as `test_xml_builder.py` but adapted for subprocess testing.

## Benefits for Your Future Service

When you build your Next.js API endpoint, you can reuse the exact same parser and exceptions:

```javascript
// Example Next.js API route (future)
import { exec } from 'child_process';

export default async function handler(req, res) {
  try {
    // Call Python parser service
    const result = await parseTranscript(req.body.content);
    res.status(200).json({ chapters: result });
  } catch (error) {
    if (error.type === 'InvalidTranscriptFormatError') {
      res.status(400).json({
        error: 'invalid_format',
        message: error.message  // "Transcript must start with chapter title..."
      });
    }
    // Handle other exception types...
  }
}
```

The same parser module, same exceptions, different presentation layer. The CLI lives in `cli.py`, the API would live in its own module - clean separation. That's the power of this pattern.