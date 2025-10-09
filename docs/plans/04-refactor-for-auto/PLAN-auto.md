# YouTube-to-XML Refactoring Plan

## Goal

Design and implement YouTube URL processing capability within the main application's clean architecture to create a unified CLI that handles both file and URL inputs seamlessly.

**Current State**: `uv run youtube-to-xml transcript.txt` (files only) + experimental proof-of-concept script
**Target State**: `uv run youtube-to-xml <file_or_url>` (unified auto-detection)

The experimental script `scripts/transcript_auto_fetcher.py` proves YouTube functionality is feasible and demonstrates the desired output format, but will be removed after we implement a proper architectural solution. This refactoring designs clean, separate source modules that both produce identical standardized output formats. This refactoring must meet the Success Criteria below and adhere to the specified Code Design Principles and TDD Implementation guidelines.

## Architecture: Simple & Elegant

```text
Input → Source Detection → TranscriptData → XML Builder → Output
           ↓                    ↓              ↓
        Logging             Logging        Logging
```

Single module approach with standardized internal format.

---

## Phase 1: Foundation - Logging & Exceptions

**Goal**: Set up error handling and logging infrastructure first

### Phase 1 Deliverables

- [x] Create enhanced `exceptions.py` with new exception types
- [x] Create `logging_config.py` with simple file logging
- [x] Add tests for new exceptions
- [x] Existing tests still pass

### Phase 1 Implementation

```python
# exceptions.py
class BaseTranscriptError(Exception):
    """Base exception for all transcript processing."""
    pass

# File input errors (keep existing + base class)
class FileEmptyError(BaseTranscriptError): ...
class FileInvalidFormatError(BaseTranscriptError): ...

# YouTube input errors (new)
class URLFormatError(BaseTranscriptError): ...
class URLVideoNotFoundError(BaseTranscriptError): ...
class URLSubtitlesNotFoundError(BaseTranscriptError): ...
class URLRateLimitError(BaseTranscriptError): ...

# logging_config.py
def setup_logging(log_file="youtube_to_xml.log"):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

### Phase 1 Testing

- `uv run pytest tests/test_exceptions.py -v`
- Verify log file creation
- Existing tests still pass

### **🛑 STOP AFTER PHASE 1**

**Manual Verification Required:**

1. Run `uv run pytest` - all existing tests should still pass
2. Check that new exception types exist in `exceptions.py`
3. Verify `logging_config.py` creates log file when imported
4. Test that `BaseTranscriptError` is the base class for all exceptions

**✅ Await confirmation before proceeding to Phase 2**

---

## Phase 2: Unified Data Model

**Goal**: Create data structures supporting both inputs

### Phase 2 Deliverables

- [ ] Create `models.py` with TranscriptData structure
- [ ] Update Chapter to work with enhanced model
- [ ] Comprehensive tests for models
- [ ] Integration with existing parser

### Phase 2 Implementation

```python
# models.py
@dataclass
class TranscriptData:
    chapters: list[Chapter]
    video_title: str = ""
    upload_date: str = ""
    duration: str = ""
    video_url: str = ""

# Keep Chapter as-is (already perfect):
@dataclass
class Chapter:
    title: str
    start_time: str
    content_lines: list[str]  # Standardized format
```

### Phase 2 Testing

- Unit tests for TranscriptData
- Verify Chapter compatibility
- `uv run pytest tests/test_models.py -v`

### **🛑 STOP AFTER PHASE 2**

**Manual Verification Required:**

1. Run `uv run pytest` - all tests should pass
2. Check `models.py` exists with TranscriptData and Chapter classes
3. Verify TranscriptData has correct default empty strings for metadata
4. Test creating TranscriptData objects with and without metadata
5. Confirm existing Chapter usage still works

**✅ Await confirmation before proceeding to Phase 3**

---

## Phase 3: Source Abstraction

**Goal**: Clean abstraction for both input types in single module

### Phase 3 Deliverables

- [ ] Create `transcript_source.py` with both sources
- [ ] Move file parsing logic from parser.py
- [ ] Add YouTube source with yt-dlp integration
- [ ] Standardize to content_lines format

### Phase 3 Implementation

```python
# transcript_source.py
from abc import ABC, abstractmethod

class TranscriptSource(ABC):
    @abstractmethod
    def load(self) -> TranscriptData:
        pass

class FileSource(TranscriptSource):
    def __init__(self, file_path: Path):
        self.file_path = file_path
    
    def load(self) -> TranscriptData:
        # Adapt existing parser.py logic
        # Returns TranscriptData with empty metadata

class YouTubeSource(TranscriptSource):
    def __init__(self, url: str):
        self.url = url
    
    def load(self) -> TranscriptData:
        # Fetch via yt-dlp
        # Convert subtitles to content_lines format
        # Use YouTube chapters or create single chapter
        # Returns TranscriptData with full metadata
```

### Phase 3 Testing

- Test each source independently
- Mock YouTube for unit tests
- Real YouTube URLs in integration tests
- `uv run pytest tests/test_transcript_source.py -v`

### **🛑 STOP AFTER PHASE 3**

**Manual Verification Required:**

1. Run `uv run pytest` - all tests should pass
2. Test FileSource manually:

   ```python
   from youtube_to_xml.transcript_source import FileSource
   source = FileSource(Path("example_transcripts/x4-chapters.txt"))
   data = source.load()
   print(data.chapters[0].title)  # Should work
   print(data.video_title)        # Should be empty string
   ```

3. Test YouTubeSource with a known working URL:

   ```python
   from youtube_to_xml.transcript_source import YouTubeSource
   source = YouTubeSource("https://www.youtube.com/watch?v=Q4gsvJvRJCU")
   data = source.load()
   print(data.video_title)        # Should have video title
   print(len(data.chapters))      # Should show chapter count
   ```

4. Verify both sources return TranscriptData with proper Chapter objects
5. Check that YouTube metadata is populated, file metadata is empty

**✅ Await confirmation before proceeding to Phase 4**

---

## Phase 4: Enhanced XML Builder

**Goal**: Support metadata attributes (always present, even if empty)

### Phase 4 Deliverables

- [ ] Update `xml_builder.py` to accept TranscriptData
- [ ] Always include metadata attributes (empty for files)
- [ ] Maintain content_lines format
- [ ] Update existing tests

### Phase 4 Implementation

```python
# xml_builder.py
def build_xml(data: TranscriptData) -> str:
    """Build XML with metadata attributes always present."""
    root = ET.Element("transcript")
    root.set("video_title", data.video_title)  # "" for files
    root.set("upload_date", data.upload_date)  # "" for files
    root.set("duration", data.duration)        # "" for files
    root.set("video_url", data.video_url)      # "" for files
    
    # Rest remains similar
```

### Phase 4 Testing

- Test with empty metadata (file input)
- Test with full metadata (YouTube input)
- Verify XML structure consistency
- `uv run pytest tests/test_xml_builder.py -v`

### **🛑 STOP AFTER PHASE 4**

**Manual Verification Required:**

1. Run `uv run pytest` - all tests should pass
2. Test file-based XML generation:

   ```python
   from youtube_to_xml.transcript_source import FileSource
   from youtube_to_xml.xml_builder import build_xml
   source = FileSource(Path("example_transcripts/x4-chapters.txt"))
   data = source.load()
   xml = build_xml(data)
   print(xml)  # Should show <transcript video_title="" upload_date="" ...>
   ```

3. Test YouTube-based XML generation:

   ```python
   from youtube_to_xml.transcript_source import YouTubeSource
   from youtube_to_xml.xml_builder import build_xml
   source = YouTubeSource("https://www.youtube.com/watch?v=Q4gsvJvRJCU")
   data = source.load()
   xml = build_xml(data)
   print(xml)  # Should show <transcript video_title="Video Title" upload_date="2024-01-01" ...>
   ```

4. Verify both XML outputs have the same structure, just different attribute values
5. Check XML is valid and properly formatted

**✅ Await confirmation before proceeding to Phase 5**

---

## Phase 5: Unified CLI with Auto-detection

**Goal**: Single CLI supporting both inputs with smart detection

### Phase 5 Deliverables

- [ ] Update CLI to auto-detect input type
- [ ] Integrate logging throughout
- [ ] Support both workflows seamlessly
- [ ] Update help text

### Phase 5 Implementation

```python
# cli.py
def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    args = parse_arguments()
    
    # Auto-detect: URL pattern or file path
    if is_youtube_url(args.input):
        source = YouTubeSource(args.input)
        logger.info(f"Processing YouTube URL: {args.input}")
    else:
        source = FileSource(Path(args.input))
        logger.info(f"Processing file: {args.input}")
    
    try:
        data = source.load()
        xml = build_xml(data)
        save_output(xml, get_output_filename(data))
        logger.info(f"XML generated successfully: {data.video_title or args.input}")
    except BaseTranscriptError as e:
        logger.error(f"Processing failed: {e}")
        print(f"❌ {e}")
        sys.exit(1)
```

### Phase 5 Testing

- Test file input: `uv run youtube-to-xml transcript.txt`
- Test URL input: `uv run youtube-to_xml https://youtube.com/...`
- Verify logging for both success and failure
- Check auto-detection works correctly

### **🛑 STOP AFTER PHASE 5**

**Manual Verification Required:**

1. Test file input: `uv run youtube-to-xml example_transcripts/x4-chapters.txt`
   - Should create x4-chapters.xml with empty metadata attributes
   - Check log file for successful processing message
2. Test URL input: `uv run youtube-to-xml https://www.youtube.com/watch?v=Q4gsvJvRJCU`
   - Should create XML file with video title as filename
   - Should include full metadata attributes
   - Check log file for successful processing message
3. Test error handling with invalid file: `uv run youtube-to-xml nonexistent.txt`
   - Should show error message
   - Check log file for error message
4. Test error handling with invalid URL: `uv run youtube-to-xml https://youtube.com/invalidvideo`
   - Should show error message
   - Check log file for error message
5. Verify help text is updated: `uv run youtube-to-xml --help`
6. Run full test suite: `uv run pytest`

**✅ Await confirmation before proceeding to Phase 6**

---

## Phase 6: Cleanup & Integration

**Goal**: Remove script, update tests, polish

### Phase 6 Deliverables

- [ ] Remove `scripts/transcript_auto_fetcher.py`
- [ ] Update integration tests to use new CLI
- [ ] Update all documentation
- [ ] Performance validation
- [ ] Final testing sweep

### Phase 6 Testing

- Full test suite: `uv run pytest`
- Integration tests: `uv run pytest -m integration`
- Manual testing of various YouTube URLs
- Performance test with 15,000 line file

### **🛑 STOP AFTER PHASE 6**

**Manual Verification Required:**

1. Verify script is removed: `ls scripts/` should not show transcript_auto_fetcher.py
2. Run integration tests: `uv run pytest -m integration`
   - Should test both file and URL inputs via CLI
   - Should not reference old script
3. Test both input methods work end-to-end:
   - File: `uv run youtube-to-xml example_transcripts/x4-chapters.txt`
   - URL: `uv run youtube-to-xml https://www.youtube.com/watch?v=Q4gsvJvRJCU`
4. Performance test: Create/use a large transcript file, time the processing
5. Run full test suite: `uv run pytest` - all tests should pass
6. Verify documentation is updated (README.md, CLAUDE.md, etc.)
7. Check that both workflows produce the expected XML structure

**✅ Final verification complete - refactoring finished**

---

## Code Design Principles: Elegant Simplicity over Over-Engineered

**TDD-Driven Design**: Write tests first - this naturally creates better architecture:

- **Pure functions preferred** - no side effects in business logic, easier to test
- **Clear module boundaries** - easier to test and understand
- **Single responsibility** - complex functions are hard to test

**Key Architecture Guidelines**:

- **Layer separation** - CLI → business logic → I/O
- **One module, one purpose** - Each `.py` file has a clear, focused role
- **Handle errors at boundaries** - Catch exceptions in CLI layer, not business logic
- **Type hints required** - All function signatures need type annotations
- **Descriptive naming** - Functions/variables should clearly indicate purpose and be consistent throughout

## TDD Implementation

- Use pytest's `tmp_path` fixture to avoid creating test files
- Avoid mocks as they introduce unnecessary complexity
- Test incrementally: One test should drive one behavior
- Use focused test names that describe what's being tested
- Integration tests use `@pytest.mark.integration` for automated end-to-end validation

## Success Criteria

- [ ] File input works: `uv run youtube-to-xml transcript.txt`
- [ ] URL input works: `uv run youtube-to-xml https://youtube.com/...`
- [ ] Auto-detection correctly identifies input type
- [ ] XML always has metadata attributes (empty for files)
- [ ] Logging captures all successes and failures
- [ ] All existing tests pass
- [ ] Performance <2 seconds for large files
- [ ] No code duplication
- [ ] Clean separation of concerns
- [ ] Ready for API wrapper
- [ ] Adheres to Code Design Principles
- [ ] Adheres to TDD Implementation
