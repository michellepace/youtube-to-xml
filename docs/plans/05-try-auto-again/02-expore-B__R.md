# 🏗️ Unified Architecture Design: YouTube-to-XML Integration

## Executive Summary

This design integrates YouTube URL transcript functionality into the main application while maintaining **elegant simplicity** through clear separation of concerns. The architecture uses a lightweight adapter pattern without over-engineering, keeping each component focused and testable while preparing for future API endpoints.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                     CLI Entry                       │
│                   (cli.py)                          │
│         --file <path> | --url <youtube_url>         │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  Source Adapter    │
         │    Selection       │
         └─────────┬──────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────────┐          ┌─────────▼────────┐
│FileSource  │          │ YouTubeSource    │
│            │          │                  │
│ Acquires:  │          │ Acquires:        │
│ • Raw text │          │ • Metadata       │
│            │          │ • Subtitles      │
│            │          │ • Chapters       │
└───┬────────┘          └─────────┬────────┘
    │                             │
┌───▼────────┐          ┌─────────▼────────┐
│file_parser │          │ youtube_parser   │
│    .py     │          │     .py          │
│            │          │                  │
│ Transforms │          │ Transforms       │
│ text →     │          │ subtitles →      │
│ Chapters   │          │ Chapters         │
└───┬────────┘          └─────────┬────────┘
    │                             │
    └──────────────┬──────────────┘
                   │
           ┌───────▼────────┐
           │  xml_builder   │
           │      .py       │
           │                │
           │ Chapters +     │
           │ Metadata →     │
           │ XML string     │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │   File I/O     │
           │  (in cli.py)   │
           └────────────────┘
```

## Core Design Principles

### 1. Separation of Concerns
- **Acquisition**: Each source handles its own data retrieval (file reading vs YouTube API)
- **Transformation**: Separate parsers for each source type maintain independence
- **Generation**: Unified XML builder consumes standardized data structures
- **Orchestration**: CLI coordinates without implementing business logic

### 2. Elegant Simplicity
- No abstract base classes or complex inheritance
- Simple function-based adapter pattern
- Clear, predictable data flow
- Minimal coupling between components

### 3. API-Ready Architecture
- Stateless operations throughout
- Clean input/output contracts
- Source adapters return `tuple[list[Chapter], Metadata]`
- Easy to wrap in REST/gRPC endpoints

## Module Structure

```
src/youtube_to_xml/
├── __init__.py
├── cli.py                 # Enhanced with --file/--url flags
├── exceptions.py          # Existing error types
├── logging_config.py      # Unchanged
├── file_parser.py         # Renamed from parser.py
├── youtube_parser.py      # New: YouTube-specific parsing
├── file_source.py         # New: File acquisition adapter
├── youtube_source.py      # New: YouTube acquisition adapter
├── xml_builder.py         # Enhanced with metadata support
└── metadata.py           # New: Shared metadata dataclass
```

## Component Specifications

### 1. CLI Enhancement (`cli.py`)

```python
def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments with source selection."""
    parser = argparse.ArgumentParser(...)
    
    # Mutually exclusive group for input sources
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--file", 
        metavar="transcript.txt",
        help="Process local transcript file"
    )
    source_group.add_argument(
        "--url",
        metavar="youtube_url", 
        help="Process YouTube video URL"
    )
    
    return parser.parse_args()

def main() -> None:
    """Main entry point with source routing."""
    args = parse_arguments()
    
    # Route to appropriate source adapter
    if args.file:
        chapters, metadata = FileSource().fetch(args.file)
        output_path = Path(args.file).stem + ".xml"
    else:  # args.url
        chapters, metadata = YouTubeSource().fetch(args.url)
        output_path = sanitize_filename(metadata.video_title) + ".xml"
    
    # Generate XML (unified path)
    xml_content = chapters_to_xml(chapters, metadata)
    
    # Write output
    Path(output_path).write_text(xml_content, encoding="utf-8")
```

### 2. Metadata Structure (`metadata.py`)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Metadata:
    """Video metadata for XML attributes."""
    video_title: str
    upload_date: str  
    duration: str
    video_url: str
    
    @classmethod
    def empty(cls) -> "Metadata":
        """Create empty metadata for file sources."""
        return cls(
            video_title="",
            upload_date="",
            duration="",
            video_url=""
        )
```

### 3. File Source Adapter (`file_source.py`)

```python
from pathlib import Path
from youtube_to_xml.file_parser import parse_transcript
from youtube_to_xml.metadata import Metadata

class FileSource:
    """Adapter for file-based transcript sources."""
    
    def fetch(self, file_path: str) -> tuple[list[Chapter], Metadata]:
        """Fetch chapters from file with empty metadata.
        
        Args:
            file_path: Path to transcript file
            
        Returns:
            Tuple of (chapters list, empty metadata)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            FileEmptyError: If file is empty
            FileInvalidFormatError: If format is invalid
        """
        content = Path(file_path).read_text(encoding="utf-8")
        chapters = parse_transcript(content)
        return chapters, Metadata.empty()
```

### 4. YouTube Source Adapter (`youtube_source.py`)

```python
import yt_dlp
from youtube_to_xml.youtube_parser import parse_youtube_subtitles
from youtube_to_xml.metadata import Metadata
from youtube_to_xml.exceptions import (
    URLVideoNotFoundError,
    URLSubtitlesNotFoundError,
    URLRateLimitError
)

class YouTubeSource:
    """Adapter for YouTube URL sources."""
    
    def fetch(self, url: str) -> tuple[list[Chapter], Metadata]:
        """Fetch chapters and metadata from YouTube.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Tuple of (chapters list, populated metadata)
            
        Raises:
            URLVideoNotFoundError: If video not found
            URLSubtitlesNotFoundError: If no subtitles
            URLRateLimitError: If rate limited
        """
        # Fetch video info and subtitles
        video_data = self._fetch_video_data(url)
        subtitles = self._download_subtitles(video_data['subtitle_url'])
        
        # Transform to chapters
        chapters = parse_youtube_subtitles(
            subtitles,
            video_data.get('chapters', [])
        )
        
        # Create metadata
        metadata = Metadata(
            video_title=video_data['title'],
            upload_date=self._format_date(video_data['upload_date']),
            duration=self._format_duration(video_data['duration']),
            video_url=video_data['webpage_url']
        )
        
        return chapters, metadata
    
    def _fetch_video_data(self, url: str) -> dict:
        """Fetch video information using yt-dlp."""
        options = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en.*', 'all'],
            'subtitlesformat': 'json3'
        }
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise URLVideoNotFoundError(f"Cannot extract: {url}")
            return self._extract_required_fields(info)
```

### 5. Parser Separation

#### `file_parser.py` (renamed from `parser.py`)
- Unchanged logic, just renamed for clarity
- Handles manual transcript format with chapter detection rules
- Returns `list[Chapter]` with content_lines

#### `youtube_parser.py` (new)
```python
from youtube_to_xml.parser import Chapter  # Reuse Chapter dataclass

def parse_youtube_subtitles(
    subtitles: list[dict], 
    chapter_markers: list[dict]
) -> list[Chapter]:
    """Transform YouTube subtitles into Chapter objects.
    
    Args:
        subtitles: JSON3 subtitle entries
        chapter_markers: YouTube chapter information
        
    Returns:
        List of Chapter objects with formatted content
    """
    # Group subtitles by chapter boundaries
    chapters = _assign_subtitles_to_chapters(subtitles, chapter_markers)
    
    # Transform to standard Chapter format
    return [
        Chapter(
            title=ch['title'],
            start_time=_format_timestamp(ch['start_time']),
            content_lines=_format_subtitle_lines(ch['subtitles'])
        )
        for ch in chapters
    ]

def _format_subtitle_lines(subtitles: list[dict]) -> list[str]:
    """Format subtitles as alternating timestamp/text lines."""
    lines = []
    for subtitle in subtitles:
        lines.append(_seconds_to_timestamp(subtitle['start']))
        lines.append(subtitle['text'])
    return lines
```

### 6. XML Builder Enhancement (`xml_builder.py`)

```python
def chapters_to_xml(
    chapters: list[Chapter], 
    metadata: Metadata
) -> str:
    """Build XML document with chapters and metadata.
    
    Args:
        chapters: List of Chapter objects
        metadata: Metadata for XML attributes
        
    Returns:
        Formatted XML string
    """
    root = ET.Element("transcript")
    root.set("video_title", metadata.video_title)
    root.set("upload_date", metadata.upload_date)
    root.set("duration", metadata.duration)
    root.set("video_url", metadata.video_url)
    
    # Rest unchanged - build chapters as before
    chapters_elem = ET.SubElement(root, "chapters")
    # ... existing chapter building logic
```

## Data Flow Examples

### File Input Flow
```
$ youtube-to-xml --file transcript.txt

1. CLI parses --file flag
2. FileSource.fetch("transcript.txt")
   - Reads file content
   - Calls file_parser.parse_transcript()
   - Returns (chapters, empty_metadata)
3. xml_builder.chapters_to_xml(chapters, empty_metadata)
   - Creates XML with empty metadata attributes
4. Saves as "transcript.xml"
```

### YouTube URL Flow
```
$ youtube-to-xml --url https://youtube.com/watch?v=...

1. CLI parses --url flag
2. YouTubeSource.fetch(url)
   - Fetches video info via yt-dlp
   - Downloads subtitles
   - Calls youtube_parser.parse_youtube_subtitles()
   - Returns (chapters, populated_metadata)
3. xml_builder.chapters_to_xml(chapters, populated_metadata)
   - Creates XML with full metadata
4. Saves as "sanitized-video-title.xml"
```

## Error Handling Strategy

- **File Source Errors**: Caught and re-raised with user-friendly messages
  - FileNotFoundError → "❌ We couldn't find your file"
  - FileEmptyError → "❌ Your file is empty"
  - FileInvalidFormatError → "❌ Wrong format"

- **YouTube Source Errors**: Specific exceptions for each failure mode
  - URLVideoNotFoundError → "❌ Video not found"
  - URLSubtitlesNotFoundError → "❌ No subtitles available"
  - URLRateLimitError → "❌ Rate limited, try again later"

- **No Retry Logic**: Simple fail-fast approach as specified

## Testing Strategy

### Unit Tests
- `test_file_source.py`: Test file adapter in isolation
- `test_youtube_source.py`: Test YouTube adapter with mocked yt-dlp
- `test_file_parser.py`: Existing tests (renamed)
- `test_youtube_parser.py`: Test subtitle transformation
- `test_xml_builder.py`: Test with both empty and populated metadata

### Integration Tests
- `test_integration.py`: End-to-end flows for both sources
- Mark YouTube tests with `@pytest.mark.integration`
- Use real YouTube URLs for confidence

## Migration Plan

### Phase 1: Refactoring (Non-Breaking)
1. Rename `parser.py` → `file_parser.py`
2. Update all imports
3. Create `metadata.py` with dataclass
4. Ensure all tests pass

### Phase 2: YouTube Integration
1. Add `youtube_parser.py`
2. Add `youtube_source.py` and `file_source.py`
3. Update `xml_builder.py` to accept metadata
4. Add yt-dlp to dependencies

### Phase 3: CLI Enhancement
1. Update `cli.py` with --file/--url flags
2. Maintain backward compatibility temporarily
3. Route to appropriate source adapter

### Phase 4: Cleanup
1. Remove experimental script
2. Update documentation
3. Update README with new usage

## Future API Considerations

The stateless adapter design makes API endpoints trivial:

```python
# Future API endpoint example
@app.post("/convert/file")
async def convert_file(content: str):
    chapters, metadata = FileSource().fetch_from_string(content)
    return {"xml": chapters_to_xml(chapters, metadata)}

@app.post("/convert/youtube")
async def convert_youtube(url: str):
    chapters, metadata = YouTubeSource().fetch(url)
    return {"xml": chapters_to_xml(chapters, metadata)}
```

## Design Decisions

### Why Not Abstract Base Classes?
- **Simplicity wins**: Two sources don't justify the complexity
- **Duck typing**: Python's natural approach
- **Clear contracts**: Return type `tuple[list[Chapter], Metadata]` is sufficient
- **Easy to understand**: No inheritance hierarchy to navigate

### Why Separate Parsers?
- **Different complexity**: File parsing uses regex patterns; YouTube uses JSON transformation
- **Independent evolution**: Each can be optimized without affecting the other
- **Clear responsibilities**: No conditional logic based on source type
- **Better testability**: Mock only what's needed for each parser

### Why Reuse Chapter Dataclass?
- **Proven design**: Already frozen and immutable
- **Consistent interface**: XML builder expects this structure
- **No duplication**: Avoid maintaining two similar classes
- **Natural convergence**: Both sources ultimately produce the same output

## Conclusion

This architecture achieves the **elegant simplicity** goal by:
- Keeping components focused and independent
- Using simple adapter pattern without over-engineering
- Maintaining clear data flow and contracts
- Preparing for future API endpoints without premature optimization
- Preserving all existing functionality while adding new capabilities

The design follows the principle that good architecture emerges from thoughtful separation of concerns rather than complex abstractions. Each component has a single, clear responsibility, making the system easy to understand, test, and extend.