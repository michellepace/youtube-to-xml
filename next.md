# Next: Unified Architecture with Shared Models

## Problem Statement

After completing the presentation layer separation in `url_to_transcript.py`, we discovered architectural inconsistency:

- **Two incompatible Chapter classes**: `scripts/url_to_transcript.py` vs `src/youtube_to_xml/file_parser.py`
- **No shared XML builder**: URL script has its own XML generation, can't reuse `xml_builder.py`
- **No VideoMetadata class in main app**: File workflow has no metadata concept - `xml_builder.py` just hardcodes empty strings for `video_title`, `upload_date`, etc.
- **VideoMetadata only exists in URL script**: The URL script defines its own VideoMetadata class that isn't shared

## Solution: Create Shared Models

### 1. Create `src/youtube_to_xml/models.py`

```python
"""Shared data models for YouTube-to-XML conversion."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Video metadata for XML output."""
    
    video_title: str
    upload_date: str  # YYYYMMDD format from yt-dlp (raw)
    duration: int     # seconds (raw integer)
    video_url: str

    @classmethod
    def empty(cls) -> VideoMetadata:
        """Create empty metadata for file-based workflows."""
        return cls(
            video_title="",
            upload_date="",
            duration=0,
            video_url=""
        )


@dataclass(frozen=True, slots=True)
class Chapter:
    """A video chapter with timestamped content."""
    
    title: str
    start_time: float      # seconds
    end_time: float        # seconds (math.inf for final chapter)
    content_lines: list[str]  # formatted text lines ready for XML

    @property
    def duration(self) -> float:
        """Calculate chapter duration."""
        return self.end_time - self.start_time
```

### 2. Update `xml_builder.py`

**Key changes:**
- Add metadata parameter to function signature
- Import VideoMetadata from models.py (not file_parser.py)
- Format raw metadata values for XML output

```python
def chapters_to_xml(chapters: list[Chapter], metadata: VideoMetadata) -> str:
    """Build complete YouTube transcript XML document from chapters."""
    # Create root XML tag element <transcript>
    root = ET.Element("transcript")
    root.set("video_title", metadata.video_title)
    root.set("upload_date", format_date(metadata.upload_date))  # Format YYYYMMDD → yyyy-mm-dd
    root.set("duration", format_duration(metadata.duration))      # Format seconds → "21m 34s"
    root.set("video_url", metadata.video_url)
    
    # ... rest of existing logic
```

**Note:** Move `format_date()` and `format_duration()` from `scripts/url_to_transcript.py` to a shared location (either `xml_builder.py` or `time_utils.py`)

### 3. Convert URL Script to Use Shared Models

**Key changes:**
- Import Chapter and VideoMetadata from `youtube_to_xml.models`
- Convert URL script's Chapter (with `all_chapter_subtitles`) to shared Chapter (with `content_lines`)
- Remove duplicate XML generation code (`create_xml_document()` and `format_xml_output()`)
- Keep `IndividualSubtitle` class local to URL script (internal detail)

**Conversion approach:**
```python
# Convert subtitles to content_lines during chapter creation
def convert_to_shared_chapter(chapter_with_subtitles) -> models.Chapter:
    lines = []
    for subtitle in chapter_with_subtitles.all_chapter_subtitles:
        lines.append(seconds_to_timestamp(subtitle.start_time))
        lines.append(subtitle.text)
    return models.Chapter(...)
```

### 4. Update File Parser Workflow

**Key changes:**
- Import Chapter from `youtube_to_xml.models` (not define locally)
- Update CLI to pass `VideoMetadata.empty()` to `chapters_to_xml()`
- No other changes needed - file parser's Chapter already uses `content_lines`

### 5. Benefits

- ✅ **Eliminates code duplication** - Single Chapter and VideoMetadata definition
- ✅ **Enables rich metadata** - File workflow can be enhanced with metadata later
- ✅ **Shared XML generation** - Both workflows use same xml_builder
- ✅ **Consistent output format** - URL and file workflows produce identical XML structure
- ✅ **Future-proof** - Clean foundation for additional metadata sources

## Implementation Plan

1. **Create `src/youtube_to_xml/models.py`**
   - Define VideoMetadata and Chapter classes
   - Import math for `math.inf` support

2. **Move formatting functions to shared location**
   - Move `format_date()` and `format_duration()` to `time_utils.py`
   - These are needed by xml_builder to format raw metadata

3. **Update `xml_builder.py`**
   - Change import: `from youtube_to_xml.models import Chapter`
   - Add metadata parameter to `chapters_to_xml()` signature
   - Import and use formatting functions for metadata

4. **Update file parser workflow**
   - `file_parser.py`: Import Chapter from models (remove local definition)
   - `cli.py`: Pass `VideoMetadata.empty()` to xml_builder

5. **Refactor URL script**
   - Import shared models
   - Convert internal chapters to shared format
   - Use shared xml_builder instead of local XML generation

6. **Update tests**
   - Import Chapter from models in test files
   - Add metadata parameter to xml_builder test calls
   - Verify both workflows produce identical XML structure

## Testing Strategy

- Run existing test suite to ensure no regressions
- Add tests for new metadata handling in xml_builder
- Verify URL and file workflows produce identical XML structure
- Test empty metadata handling for file-based workflows

## Important Considerations

- **Do NOT include** `chapters_data: list[dict]` in VideoMetadata - it's internal to URL script
- **Store raw data** in models, format at XML generation time
- **IndividualSubtitle** stays in URL script - it's an implementation detail
- **Test both paths** produce identical XML structure for same input

## Estimated Impact

- **Files changed**: 8-10 (models.py creation, time_utils, xml_builder, url_to_transcript, file_parser, cli, multiple test files)
- **Risk level**: Low-Medium (well-defined scope, existing tests provide safety net)
- **Benefits**: High (eliminates duplication, enables metadata in file workflow, unified architecture)