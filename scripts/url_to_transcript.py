"""Convert YouTube videos to XML files with subtitles organized by chapters.

This script downloads YouTube transcripts and creates structured XML files.
The XML structure: <transcript> root with video metadata attributes, containing a
<chapters> element with <chapter> elements that contain individual timestamped subtitles.

Usage:
    uv run scripts/url_to_transcript.py <YouTube_URL>

Example:
    uv run scripts/url_to_transcript.py https://youtu.be/Q4gsvJvRjCU

For a provided YouTube URL, the script will:
1. Fetch the video metadata (title, upload date, duration)
2. Download and parse subtitles (the timestamped text from YouTube's transcript)
3. Assign subtitles to chapters (using YouTube's chapter markers if available)
4. Create and save an XML document with dynamic filename based on video title

Subtitle priority:
1. Manual English subtitles uploaded by the video creator (highest quality)
2. Auto-generated English subtitles (fallback)
No other languages are downloaded - English only.

The output XML contains video metadata (video_title, upload_date, duration, video_url)
and subtitles organised by chapter, with each individual subtitle timestamped.
"""

import contextlib
import json
import math
import os
import re
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError, UnsupportedError

from youtube_to_xml.exceptions import (
    URLBotProtectionError,
    URLIncompleteError,
    URLIsInvalidError,
    URLNotYouTubeError,
    URLRateLimitError,
    URLSubtitlesNotFoundError,
    URLUnknownUnmappedError,
    URLVideoUnavailableError,
    map_yt_dlp_exception,
)
from youtube_to_xml.logging_config import get_logger, setup_logging
from youtube_to_xml.time_utils import (
    MILLISECONDS_PER_SECOND,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    seconds_to_timestamp,
)


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Video metadata needed for XML output."""

    video_title: str
    upload_date: str  # YYYYMMDD format from yt-dlp
    duration: int  # seconds
    video_url: str
    chapters_data: list[dict]


@dataclass(frozen=True, slots=True)
class IndividualSubtitle:
    """A single subtitle entry with timestamp and text."""

    start_time: float  # in seconds
    text: str


@dataclass(frozen=True, slots=True)
class Chapter:
    """A video chapter containing individual subtitles within its time range."""

    title: str
    start_time: float
    end_time: float
    all_chapter_subtitles: list[IndividualSubtitle]

    @property
    def duration(self) -> float:
        """Calculate chapter duration (may be inf for the final open-ended chapter)."""
        return self.end_time - self.start_time

    def format_content(self) -> str:
        """Format individual subtitles as timestamped text for XML output."""
        if not self.all_chapter_subtitles:
            return ""

        lines = []
        for subtitle in self.all_chapter_subtitles:
            lines.append(seconds_to_timestamp(subtitle.start_time))
            lines.append(subtitle.text)

        return "\n      ".join(lines)


def fetch_video_metadata_and_subtitles(
    url: str,
) -> tuple[VideoMetadata, list[IndividualSubtitle]]:
    """Extract video metadata and download subtitles from YouTube using yt-dlp.

    Uses yt-dlp to fetch video information and subtitles, avoiding rate limits
    by using yt-dlp's built-in subtitle handling instead of direct HTTP requests.

    Args:
        url: YouTube video URL

    Returns:
        Tuple of (VideoMetadata object, list of IndividualSubtitle objects)

    Raises:
        URLBotProtectionError: If YouTube requires verification
        URLNotYouTubeError: If URL is not a YouTube video
        URLIncompleteError: If YouTube URL has incomplete video ID
        URLIsInvalidError: If URL format is invalid
        URLVideoUnavailableError: If YouTube video is unavailable
        URLSubtitlesNotFoundError: If no subtitles are available
        URLRateLimitError: If YouTube rate limit is encountered
    """
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-orig"],  # English manual then auto-generated
        "subtitlesformat": "json3",
        "outtmpl": "%(title)s [%(id)s].%(ext)s",
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory for yt-dlp output
        options["outtmpl"] = str(Path(temp_dir) / "%(title)s [%(id)s].%(ext)s")

        # Phase 1: Use yt-dlp to get data for transcript
        with (
            open(os.devnull, "w") as devnull,  # noqa: PTH123 - os.devnull for cross-platform
            contextlib.redirect_stderr(devnull),
            yt_dlp.YoutubeDL(options) as ydl,
        ):
            try:
                # a) get complete video metadata from YouTube
                raw_metadata = ydl.extract_info(url, download=False)
                # b) download subtitle files to temp_dir (.json3 format)
                ydl.process_info(raw_metadata)
            except (DownloadError, ExtractorError, UnsupportedError) as e:
                mapped_exception = map_yt_dlp_exception(e)
                raise mapped_exception from e

        # Phase 2: File processing (outside yt-dlp context)
        # Note: raw_metadata is never None in practice - yt-dlp raises exceptions instead
        assert raw_metadata is not None  # Satisfy Pyright type checker  # noqa: S101

        # a) Locate downloaded subtitle files
        video_id = raw_metadata.get("id", "")
        subtitle_files = [
            p for p in Path(temp_dir).glob("*.json3") if f"[{video_id}]" in p.name
        ]

        # b) Parse subtitle files into structured objects
        subtitles = []
        if subtitle_files:
            subtitle_file = subtitle_files[0]
            # Read JSON3 format from disk
            subtitle_content = json.loads(subtitle_file.read_text(encoding="utf-8"))
            # Extract events → IndividualSubtitle objects
            subtitles = extract_subtitles_from_json3(subtitle_content.get("events", []))
        else:
            raise URLSubtitlesNotFoundError

        # Phase 3: Create structured metadata object from raw_metadata
        metadata = VideoMetadata(
            video_title=raw_metadata.get("title", "Untitled"),
            upload_date=raw_metadata.get("upload_date", ""),
            duration=raw_metadata.get("duration", 0),
            video_url=raw_metadata.get("webpage_url", url),
            chapters_data=raw_metadata.get("chapters", []),
        )

        return metadata, subtitles


def extract_subtitles_from_json3(events: list) -> list[IndividualSubtitle]:
    """Extract individual subtitles from JSON3 event objects.

    Args:
        events: List of JSON3 event objects from YouTube

    Returns:
        List of IndividualSubtitle objects with cleaned text and timestamps
    """
    subtitles = []

    for event in events:
        # Skip events without subtitle data
        if "segs" not in event:
            continue

        # Combine text from all parts
        text_parts = [seg["utf8"] for seg in event["segs"] if "utf8" in seg]
        # Remove line breaks that YouTube adds for display formatting
        text = "".join(text_parts).strip().replace("\n", " ")
        if not text:
            continue

        # Convert milliseconds to seconds
        start_ms = event.get("tStartMs", 0)
        start_seconds = start_ms / MILLISECONDS_PER_SECOND

        subtitles.append(IndividualSubtitle(start_seconds, text))

    return subtitles


def assign_subtitles_to_chapters(
    metadata: VideoMetadata, subtitles: list[IndividualSubtitle]
) -> list[Chapter]:
    """Parse API transcript data into chapters.

    Args:
        metadata: Video metadata including chapter info
        subtitles: List of all individual subtitles

    Returns:
        List of Chapter objects with assigned subtitles
    """
    if not metadata.chapters_data:
        # No chapters - create single chapter with video title
        return [
            Chapter(
                title=metadata.video_title,
                start_time=0,
                end_time=math.inf,
                all_chapter_subtitles=subtitles,
            )
        ]

    chapters = []
    chapter_list = metadata.chapters_data

    for i, chapter_info in enumerate(chapter_list):
        start = float(chapter_info.get("start_time", 0))

        # End time is start of next chapter, or infinity for last chapter
        if i + 1 < len(chapter_list):
            end = float(chapter_list[i + 1]["start_time"])
        else:
            end = math.inf

        # Filter subtitles within this chapter's time range
        chapter_subtitles = [sub for sub in subtitles if start <= sub.start_time < end]

        chapters.append(
            Chapter(
                title=chapter_info.get("title", f"Chapter {i + 1}"),
                start_time=start,
                end_time=end,
                all_chapter_subtitles=chapter_subtitles,
            )
        )

    return chapters


def format_date(date_string: str) -> str:
    """Convert YYYYMMDD to yyyy-mm-dd format."""
    if len(date_string) == len("20250101"):
        try:
            date = datetime.strptime(date_string, "%Y%m%d").replace(tzinfo=None)  # noqa: DTZ007
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return date_string
    return date_string


def format_duration(seconds: int) -> str:
    """Convert seconds to human-readable duration.

    Formatted string like "21m 34s" or "1h 5m 12s"
    """
    if seconds <= 0:
        return "0s"

    hours = seconds // SECONDS_PER_HOUR
    minutes = (seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE
    secs = seconds % SECONDS_PER_MINUTE

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def create_xml_document(metadata: VideoMetadata, chapters: list[Chapter]) -> str:
    """Create the complete XML document with metadata and chapters.

    Args:
        metadata: Video metadata for attributes
        chapters: List of chapters with content

    Returns:
        Pretty-formatted XML string
    """
    # Create root element with metadata attributes
    root = ET.Element("transcript")
    root.set("video_title", metadata.video_title)
    root.set("upload_date", format_date(metadata.upload_date))
    root.set("duration", format_duration(metadata.duration))
    root.set("video_url", metadata.video_url)

    # Add chapters container
    chapters_elem = ET.SubElement(root, "chapters")

    # Add each chapter
    for chapter in chapters:
        chapter_elem = ET.SubElement(chapters_elem, "chapter")
        chapter_elem.set("title", chapter.title)
        chapter_elem.set("start_time", seconds_to_timestamp(chapter.start_time))

        # Add content if available
        content = chapter.format_content()
        if content:
            chapter_elem.text = "\n      " + content + "\n    "

    # Convert to pretty XML string
    return format_xml_output(root)


def format_xml_output(element: ET.Element) -> str:
    """Format XML element with proper indentation."""
    ET.indent(element, space="  ")
    return ET.tostring(element, encoding="unicode", xml_declaration=True) + "\n"


def generate_summary_stats(chapters: list[Chapter]) -> None:
    """Print summary statistics for the processed transcript."""
    total_subtitles = sum(len(ch.all_chapter_subtitles) for ch in chapters)
    print("\n📈 Summary:")
    print(f"   Chapters: {len(chapters)}")
    print(f"   Individual subtitles: {total_subtitles}")


def sanitize_title_for_filename(title: str) -> str:
    """Convert video title to safe filename.

    Args:
        title: Video title string

    Returns:
        Sanitized filename with .xml extension
    """
    # Remove non-alphanumeric characters except spaces and hyphens
    safe_title = re.sub(r"[^\w\s-]", "", title.lower())
    # Replace spaces and multiple hyphens with single hyphen
    safe_title = re.sub(r"[\s_-]+", "-", safe_title).strip("-")
    return f"{safe_title}.xml"


def convert_youtube_to_xml(
    video_url: str, execution_id: str
) -> tuple[str, VideoMetadata]:
    """Convert YouTube video to XML transcript with metadata.

    Core business logic that:
    1. Fetches video metadata and downloads subtitles using yt-dlp
    2. Assigns subtitles to chapters
    3. Creates XML document

    Args:
        video_url: YouTube video URL
        execution_id: Unique identifier for this execution

    Returns:
        Tuple of (XML content as string, VideoMetadata object)
    """
    logger = get_logger(__name__)
    print(f"🎬 Processing: {video_url}")
    logger.info("[%s] Processing video: %s", execution_id, video_url)

    # Step 1: Fetch metadata and download subtitles using yt-dlp
    print("📊 Fetching video metadata...")
    try:
        metadata, subtitles = fetch_video_metadata_and_subtitles(video_url)
        print(f"   Title: {metadata.video_title}")
        print(f"   Duration: {format_duration(metadata.duration)}")
        print(f"📝 Downloaded {len(subtitles)} subtitles")
    except URLSubtitlesNotFoundError:
        logger.warning("[%s] No subtitles available for video", execution_id)
        raise  # Re-raise to prevent file creation (no useless empty files)
    except URLRateLimitError as e:
        print(f"❌ {e}", file=sys.stderr)
        logger.exception("[%s] URLRateLimitError", execution_id)
        raise  # Re-raise to prevent file creation

    # Step 2: Assign subtitles to chapters
    chapters_count = len(metadata.chapters_data) if metadata.chapters_data else 1
    print(f"📑 Organising into {chapters_count} chapter(s)...")
    chapters = assign_subtitles_to_chapters(metadata, subtitles)

    # Step 3: Create XML
    print("🔧 Building XML document...")
    xml_content = create_xml_document(metadata, chapters)

    # Summary statistics
    generate_summary_stats(chapters)

    return xml_content, metadata


def save_transcript(video_url: str, execution_id: str) -> None:
    """Convert YouTube video to XML and save to file.

    Handles the file I/O operation separate from business logic.
    Uses dynamic filename based on video title.

    Args:
        video_url: YouTube video URL
        execution_id: Unique identifier for this execution
    """
    # Generate XML content and get metadata for filename
    xml_content, metadata = convert_youtube_to_xml(video_url, execution_id)
    output_file = sanitize_title_for_filename(metadata.video_title)

    # Save to file
    output_path = Path(output_file)
    output_path.write_text(xml_content, encoding="utf-8")

    logger = get_logger(__name__)
    print(f"✅ Created: {output_path.absolute()}")
    logger.info("[%s] Successfully created: %s", execution_id, output_path.absolute())


def main() -> None:
    """Command-line interface entry point."""
    setup_logging()
    logger = get_logger(__name__)
    execution_id = str(uuid.uuid4())[:8]

    try:
        video_url = sys.argv[1]
    except IndexError:
        print("YouTube URL to XML Converter")
        print("  Usage: include the YouTube URL as an argument")
        print("  E.g.: url_to_transcript.py https://www.youtube.com/watch?v=Q4gsvJvRjCU")
        sys.exit(1)

    logger.info("[%s] Starting script execution for: %s", execution_id, video_url)

    try:
        save_transcript(video_url, execution_id)
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except (
        URLBotProtectionError,
        URLIncompleteError,
        URLIsInvalidError,
        URLNotYouTubeError,
        URLSubtitlesNotFoundError,
        URLRateLimitError,
        URLUnknownUnmappedError,
        URLVideoUnavailableError,
    ) as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except (ValueError, OSError) as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("[%s] Unexpected error", execution_id)
        sys.exit(1)


if __name__ == "__main__":
    main()
