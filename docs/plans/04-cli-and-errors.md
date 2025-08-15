# REVISED Implementation Plan: Error Handling Pattern & CLI

## ✅ Critical Validations Completed

- Confirmed exactly 3 ValueError raises in parser.py (lines 44, 51, 57)
- Found only 1 existing test using ValueError (line 124 in test_parser.py)
- Verified xml_builder.py only imports chapter class (unaffected)
- Confirmed pyproject.toml help text matches SPEC.md requirements
- Validated entry point syntax for pyproject.toml

## 📋 Phase 1: Exception Module

Create `src/youtube_to_xml/exceptions.py`
```python
class EmptyFileError(ValueError):
    def __init__(self, message: str = "Cannot parse an empty transcript file")

class InvalidTranscriptFormatError(ValueError):
    def __init__(self, message: str = "Transcript must start with a chapter title, not a timestamp")

class MissingTimestampError(ValueError):
    def __init__(self, message: str = "Transcript must contain at least one timestamp")
```

## 🔧 Phase 2: Parser Updates

Update `src/youtube_to_xml/parser.py`
- Add import: `from youtube_to_xml.exceptions import (EmptyFileError, InvalidTranscriptFormatError, MissingTimestampError)`
- Line 44: Replace `raise ValueError(msg)` → `raise EmptyFileError()`
- Line 51: Replace `raise ValueError(msg)` → `raise InvalidTranscriptFormatError()`
- Line 57: Replace `raise ValueError(msg)` → `raise MissingTimestampError()`

## ✅ Phase 3: Test Updates

Update `tests/test_parser.py`
1. Add imports for custom exceptions
2. Update existing test (line 124): Change `pytest.raises(ValueError, match="timestamp")` → `pytest.raises(InvalidTranscriptFormatError)`
3. Add two new tests:
   - `test_rejects_empty_transcript()` → tests EmptyFileError
   - `test_rejects_transcript_without_timestamps()` → tests MissingTimestampError

## 📋 Phase 4: CLI Implementation

Create `src/youtube_to_xml/cli.py` with:
- `parse_arguments()`: argparse with exact help text from SPEC.md lines 194-221
- `main()`:
  - Read file (catch FileNotFoundError, PermissionError)
  - Parse transcript (catch EmptyFileError, InvalidTranscriptFormatError, MissingTimestampError)
  - Generate XML with `chapters_to_xml()`
  - Create transcript_files/ directory (relative to cwd)
  - Write XML file (catch PermissionError)
  - Print success: ✅ Created: {output_path}

## 🔧 Phase 5: Package Configuration

1. Update `src/youtube_to_xml/__init__.py`: Replace with `"""YouTube to XML converter package."""`
2. Update `pyproject.toml`: Change line 13 from `youtube-to-xml = "youtube_to_xml:main"` to `youtube-to-xml = "youtube_to_xml.cli:main"`

## ✅ Phase 6: Testing

1. **Run existing tests:** `uv run pytest` (expect 35 passing tests)
2. **Create** `tests/test_cli.py` **with 4 tests using subprocess + tmp_path:**
   - `test_valid_transcript_creates_xml()`
   - `test_missing_file_shows_error()`
   - `test_empty_file_shows_error()` (new)
   - `test_invalid_format_shows_error()` (new)
3. **Manual CLI testing:**
   - **Valid:** `uv run youtube-to-xml sample.txt`
   - **Missing:** `uv run youtube-to-xml nonexistent.txt`
   - **Empty:** `echo "" > empty.txt && uv run youtube-to-xml empty.txt`
   - **Invalid:** `echo "bad" > invalid.txt && uv run youtube-to-xml invalid.txt`
   - **Help:** `uv run youtube-to-xml --help`
4. **Quality checks:**
   - `uv run ruff check`
   - `uv run ruff format`
   - `uv run pre-commit run --all-files`

## Key Details to Remember

- Exception default messages must match current ValueError messages exactly
- CLI must use `Path.read_text()` and `Path.write_text()` with `encoding="utf-8"`
- Output directory is relative to working directory, not script location
- Test file uses `cwd=tmp_path` to isolate file operations
- Entry point change requires rebuilding package (`uv sync` will handle this)

## Success Criteria

- All 35+ existing tests pass with new exception types
- CLI produces exact error messages per `SPEC.md`
- Clean separation: parser raises exceptions → CLI formats for users
- Foundation ready for future API/service layers