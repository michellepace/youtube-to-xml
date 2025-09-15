# 🏗️ Unified Architecture Design: YouTube-to-XML Converter

## Executive Summary

This design unifies the file-based and YouTube URL-based transcript processing into a single application using the **Adapter Pattern**. The architecture maintains elegant simplicity by recognizing that while data acquisition and parsing differ significantly between sources, they converge to produce identical XML output. This design preserves the clean separation of concerns, testability, and future API readiness identified in the architectural review.

## Core Design Principles

1. **Source Independence**: Each source (file/YouTube) maintains its own acquisition and parsing logic
2. **Unified Output**: Both sources produce identical XML structure with only metadata differences
3. **Clean Boundaries**: Clear separation between CLI, source adapters, parsers, and XML generation
4. **Explicit Over Implicit**: Clear, explicit error types and source selection via CLI flags
5. **Simplicity Through Separation**: Accept duplication where it maintains clarity

## Architecture Overview

```
┌─────────────┐
│     CLI     │  Entry point with --file or --url flags
└──────┬──────┘
       │
┌──────▼──────┐
│   Sources   │  Source selection and orchestration
│  (Adapter)  │
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
┌──▼─┐  ┌──▼──┐
│File│  │ URL │   Independent source implementations
└──┬─┘  └──┬──┘
   │       │
┌──▼─┐  ┌──▼──┐
│File│  │ YT  │   Independent parsers
│Psr │  │ Psr │
└──┬─┘  └──┬──┘
   │       │
   └───┬───┘
       │
┌──────▼──────┐
│ XML Builder │  Unified XML generation
└─────────────┘
```

## Module Structure

```
src/youtube_to_xml/
├── cli.py              # CLI entry point with --file/--url flags
├── sources/            # Source adapters
│   ├── __init__.py
│   ├── base.py         # Base types (Chapter, Metadata)
│   ├── file_source.py  # File source adapter
│   └── youtube_source.py # YouTube source adapter
├── parsers/            # Parsing logic
│   ├── __init__.py
│   ├── file_parser.py  # File transcript parser (renamed from parser.py)
│   └── youtube_parser.py # YouTube transcript parser
├── xml_builder.py      # Unified XML generation
├── exceptions.py       # All exception types
└── logging_config.py   # Logging infrastructure
```

## Data Structures

### Base Types (sources/base.py)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Metadata:
    """Video metadata for XML attributes."""
    video_title: str      # Empty string for file source
    upload_date: str      # Empty string for file source  
    duration: str         # Empty string for file source
    video_url: str        # Empty string for file source

@dataclass(frozen=True)
class Chapter:
    """Chapter with content lines for XML generation."""
    title: str
    start_time: str       # Already formatted as timestamp string
    content_lines: list[str]  # Lines with alternating timestamps and text
```

### Key Design Decision: Unified Chapter Structure

Both sources will convert their data to produce `Chapter` objects with `content_lines` as `list[str]`:
- **File source**: Already in this format (timestamps and text lines)
- **YouTube source**: Converts `IndividualSubtitle` objects to alternating timestamp/text lines

This ensures the XML builder remains unchanged and both sources produce identical output structure.

## Source Adapters

### Base Source Protocol (sources/base.py)

```python
from typing import Protocol

class TranscriptSource(Protocol):
    """Protocol for transcript sources."""
    
    def fetch(self) -> tuple[list[Chapter], Metadata]:
        """Fetch and parse transcript from source.
        
        Returns:
            Tuple of (chapters, metadata)
        """
        ...
```

### File Source (sources/file_source.py)

```python
class FileSource:
    """Adapter for file-based transcripts."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
    
    def fetch(self) -> tuple[list[Chapter], Metadata]:
        """Read file and parse transcript."""
        # 1. Read file content
        raw_content = self._read_file()
        
        # 2. Parse using file_parser
        chapters = parse_transcript(raw_content)
        
        # 3. Create empty metadata
        metadata = Metadata(
            video_title="",
            upload_date="",
            duration="",
            video_url=""
        )
        
        return chapters, metadata
```

### YouTube Source (sources/youtube_source.py)

```python
class YouTubeSource:
    """Adapter for YouTube URL transcripts."""
    
    def __init__(self, url: str):
        self.url = url
    
    def fetch(self) -> tuple[list[Chapter], Metadata]:
        """Download and parse YouTube transcript."""
        # 1. Fetch video metadata and subtitles
        video_data = self._fetch_video_data()
        
        # 2. Parse using youtube_parser
        chapters = parse_youtube_transcript(video_data)
        
        # 3. Create populated metadata
        metadata = Metadata(
            video_title=video_data.title,
            upload_date=format_date(video_data.upload_date),
            duration=format_duration(video_data.duration),
            video_url=video_data.url
        )
        
        return chapters, metadata
```

## Parser Modules

### File Parser (parsers/file_parser.py)
- Renamed from current `parser.py`
- No changes to logic - uses 2-line gap rule for chapter detection
- Returns `list[Chapter]` with content already as `list[str]`

### YouTube Parser (parsers/youtube_parser.py)
- New module extracting parsing logic from experimental script
- Handles subtitle download and chapter assignment
- Converts `IndividualSubtitle` objects to `list[str]` format:

```python
def format_subtitles_as_lines(subtitles: list[IndividualSubtitle]) -> list[str]:
    """Convert individual subtitles to alternating timestamp/text lines."""
    lines = []
    for subtitle in subtitles:
        lines.append(seconds_to_timestamp(subtitle.start_time))
        lines.append(subtitle.text)
    return lines
```

## CLI Updates (cli.py)

```python
def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="youtube-to-xml",
        description="Convert YouTube transcripts to XML format"
    )
    
    # Mutually exclusive source selection
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--file", 
        metavar="PATH",
        help="Path to transcript text file"
    )
    source_group.add_argument(
        "--url",
        metavar="URL", 
        help="YouTube video URL"
    )
    
    return parser.parse_args()

def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    
    # Select source based on arguments
    if args.file:
        source = FileSource(Path(args.file))
        input_identifier = Path(args.file).stem
    else:  # args.url
        source = YouTubeSource(args.url)
        input_identifier = None  # Will use video title
    
    try:
        # Fetch and parse from selected source
        chapters, metadata = source.fetch()
        
        # Generate XML (unchanged)
        xml_content = chapters_to_xml(chapters, metadata)
        
        # Determine output filename
        if metadata.video_title:
            output_name = sanitize_title_for_filename(metadata.video_title)
        else:
            output_name = f"{input_identifier}.xml"
        
        # Save output
        Path(output_name).write_text(xml_content, encoding="utf-8")
        print(f"✅ Created: {output_name}")
        
    except (FileEmptyError, FileInvalidFormatError) as e:
        print(f"❌ File error: {e}")
        sys.exit(1)
    except (URLVideoNotFoundError, URLSubtitlesNotFoundError, URLRateLimitError) as e:
        print(f"❌ YouTube error: {e}")
        sys.exit(1)
```

## XML Builder Updates

```python
def chapters_to_xml(chapters: list[Chapter], metadata: Metadata) -> str:
    """Build XML document from chapters and metadata."""
    root = ET.Element("transcript")
    root.set("video_title", metadata.video_title)
    root.set("upload_date", metadata.upload_date)
    root.set("duration", metadata.duration)
    root.set("video_url", metadata.video_url)
    
    # Rest remains the same...
```

## Migration Plan

### Phase 1: Refactor Existing Code
1. Create `sources/` and `parsers/` directories
2. Move and rename `parser.py` → `parsers/file_parser.py`
3. Create `sources/base.py` with shared types
4. Update imports across the codebase

### Phase 2: Implement YouTube Support
1. Create `parsers/youtube_parser.py` extracting logic from experimental script
2. Create `sources/youtube_source.py` as adapter
3. Add `yt-dlp` to main dependencies in `pyproject.toml`
4. Update `xml_builder.py` to accept metadata parameter

### Phase 3: Update CLI
1. Implement `--file` and `--url` flags
2. Add source selection logic
3. Update error handling for both source types
4. Update help text and documentation

### Phase 4: Testing
1. Update existing tests for renamed modules
2. Add tests for YouTube parser
3. Add tests for source adapters
4. Add integration tests for YouTube URLs

### Phase 5: Cleanup
1. Delete `scripts/transcript_auto_fetcher.py`
2. Update README with new usage examples
3. Update CLAUDE.md with new architecture

## Testing Strategy

```
tests/
├── test_cli.py                    # CLI with both sources
├── test_sources/
│   ├── test_file_source.py        # File source adapter
│   └── test_youtube_source.py     # YouTube source adapter
├── test_parsers/
│   ├── test_file_parser.py        # Renamed from test_parser.py
│   └── test_youtube_parser.py     # YouTube parser tests
├── test_xml_builder.py            # Updated with metadata
├── test_exceptions.py             # Unchanged
└── test_integration.py            # Both file and URL integration
```

## Benefits of This Design

1. **Clean Separation**: Each source maintains independent logic without contamination
2. **Unified Interface**: Simple adapter pattern with `fetch()` method
3. **Testability**: Each component can be tested in isolation
4. **Future API Ready**: Stateless adapters and parsers ready for API endpoints
5. **Maintainability**: Clear module boundaries and single responsibilities
6. **Extensibility**: Easy to add new sources without touching existing code

## Example Usage

```bash
# File source (existing behavior)
uv run youtube-to-xml --file transcript.txt
# Output: transcript.xml (or sanitized title if found)

# YouTube source (new functionality)
uv run youtube-to-xml --url https://www.youtube.com/watch?v=Q4gsvJvRjCU
# Output: how-claude-code-hooks-save-me-hours-daily.xml
```

## Future Considerations

### API Service Adaptation
The source adapters can be directly reused in API endpoints:

```python
@app.post("/convert")
async def convert_transcript(source_type: str, source_data: str):
    if source_type == "file":
        source = FileSource(source_data)  # Would need adjustment for content vs path
    else:
        source = YouTubeSource(source_data)
    
    chapters, metadata = source.fetch()
    return {"xml": chapters_to_xml(chapters, metadata)}
```

### Additional Sources
New sources (e.g., Vimeo) can be added by:
1. Creating a new source adapter in `sources/`
2. Creating a new parser in `parsers/` if needed
3. Adding CLI flag support
4. No changes to XML builder or existing sources

## Conclusion

This design achieves the goal of unifying file and YouTube transcript processing while maintaining the elegant simplicity praised in the architectural review. By accepting that the two sources are fundamentally different in acquisition and parsing, but converge at the Chapter/Metadata level, we create a clean, maintainable, and extensible architecture that serves both current CLI needs and future API ambitions.