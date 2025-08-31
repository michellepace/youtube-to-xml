"""Convert YouTube videos to XML files with subtitles organized by chapters.

This script downloads YouTube transcripts and creates structured XML files.
The XML structure: <transcript> root with video metadata, containing <chapters>
with individual timestamped subtitles.

Usage:
    uv run scripts/transcript_auto_fetcher.py <YouTube_URL> [output_file]

Example:
    uv run scripts/transcript_auto_fetcher.py https://youtu.be/Q4gsvJvRjCU output.xml

For a provided YouTube URL, the script will:
1. Fetch the video metadata (title, upload date, duration)
2. Download and parse subtitles (the timestamped text from YouTube's transcript)
3. Assign subtitles to chapters (using YouTube's chapter markers if available)
4. Create and save an XML document with all the structured data "video_transcript.xml"

Subtitle priority:
1. Manual subtitles uploaded by the video creator (highest quality)
2. Auto-generated English subtitles (fallback)
3. Any available subtitles (last resort)

The output XML contains video metadata (video_title, upload_date, duration, video_url)
and subtitles organised by chapter, with each individual subtitle timestamped.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

import yt_dlp

# Constants
DEFAULT_OUTPUT_FILE = "video_transcript.xml"
MILLISECONDS_PER_SECOND = 1000.0
SUBTITLE_LANGS = ["en.*", "all"]  # English preferred, any fallback
YYYYMMDD_LENGTH = 8
MIN_ARGS_REQUIRED = 2
OUTPUT_ARG_INDEX = 2
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60


def seconds_to_timestamp(seconds: float, *, show_hours_if_zero: bool = False) -> str:
    """Convert seconds to H:MM:SS or M:SS format."""
    total_seconds = int(seconds)
    hours = total_seconds // SECONDS_PER_HOUR
    minutes = (total_seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE
    secs = total_seconds % SECONDS_PER_MINUTE

    if hours > 0 or show_hours_if_zero:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


@dataclass
class VideoMetadata:
    """Video metadata needed for XML output."""

    video_title: str
    upload_date: str  # YYYYMMDD format from yt-dlp
    duration: int  # seconds
    video_url: str
    chapters_data: list[dict]
    subtitle_url: str | None


@dataclass
class IndividualSubtitle:
    """A single subtitle entry with timestamp and text."""

    start_time: float  # in seconds
    text: str


@dataclass
class Chapter:
    """A video chapter containing individual subtitles within its time range."""

    title: str
    start_time: float
    end_time: float
    all_chapter_subtitles: list[IndividualSubtitle]

    def format_content(self) -> str:
        """Format individual subtitles as timestamped text for XML output."""
        if not self.all_chapter_subtitles:
            return ""

        lines = []
        for subtitle in self.all_chapter_subtitles:
            lines.append(seconds_to_timestamp(subtitle.start_time))
            lines.append(subtitle.text)

        return "\n      ".join(lines)


def fetch_video_metadata(url: str) -> VideoMetadata:
    """Extract video metadata and subtitle URL from YouTube.

    Uses yt-dlp to fetch video information without downloading.
    Prioritizes English subtitles but falls back to any available.

    Args:
        url: YouTube video URL

    Returns:
        VideoMetadata object with video info and subtitle URL

    Raises:
        ValueError: If video info cannot be extracted
    """
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": SUBTITLE_LANGS,
        "subtitlesformat": "json3",
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

        if not info:
            msg = f"Could not extract video info from {url}"
            raise ValueError(msg)

        # Extract subtitle URL from available options
        subtitle_url = extract_subtitle_url(info)

        return VideoMetadata(
            video_title=info.get("title", "Untitled"),
            upload_date=info.get("upload_date", ""),
            duration=info.get("duration", 0),
            video_url=info.get("webpage_url", url),
            chapters_data=info.get("chapters", []),
            subtitle_url=subtitle_url,
        )


def extract_subtitle_url(info: dict) -> str | None:
    """Extract subtitle URL from yt-dlp video info dictionary.

    yt-dlp automatically prioritizes manual subtitles (uploaded by creator)
    over auto-generated subtitles when both are available.

    Args:
        info: Video info dictionary from yt-dlp

    Returns:
        URL to JSON3 subtitle file, or None if no subtitles available
    """
    requested = info.get("requested_subtitles", {})
    if requested:
        first_lang = next(iter(requested))
        subtitle_info = requested[first_lang]
        return subtitle_info.get("url") if subtitle_info else None
    return None


def download_and_parse_subtitles(url: str) -> list[IndividualSubtitle]:
    """Download and parse JSON3 subtitle data from YouTube.

    Args:
        url: URL to JSON3 subtitle file

    Returns:
        List of IndividualSubtitle objects parsed from JSON3 format
    """
    if not url:
        return []

    try:
        with urlopen(url) as response:  # noqa: S310
            json_text = response.read().decode("utf-8")

        data = json.loads(json_text)
        return extract_subtitles_from_json3(data.get("events", []))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Could not fetch subtitles: {e}")
        return []


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
    """Assign individual subtitles to their respective chapters.

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
                end_time=float("inf"),
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
            end = float("inf")

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
    """Convert YYYYMMDD to yyyy-mm-dd format.

    Args:
        date_string: Date in YYYYMMDD format from yt-dlp

    Returns:
        Formatted date like "2024-07-23", or original string if invalid
    """
    if len(date_string) == YYYYMMDD_LENGTH:
        try:
            date = datetime.strptime(date_string, "%Y%m%d").replace(tzinfo=None)  # noqa: DTZ007
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return date_string
    return date_string


def format_duration(seconds: int) -> str:
    """Convert seconds to human-readable duration.

    Args:
        seconds: Duration in seconds

    Returns:
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
    """Format XML element with proper indentation.

    Args:
        element: XML Element to format

    Returns:
        Pretty-printed XML string with declaration
    """
    ET.indent(element, space="  ")
    return ET.tostring(element, encoding="unicode", xml_declaration=True) + "\n"


def fetch_and_parse_subtitles(metadata: VideoMetadata) -> list[IndividualSubtitle]:
    """Download and parse subtitles if available.

    Wrapper function that handles console output for subtitle downloading.

    Args:
        metadata: Video metadata containing subtitle URL

    Returns:
        List of individual subtitles, empty if none available
    """
    if metadata.subtitle_url:
        print("📝 Downloading subtitles...")
        subtitles = download_and_parse_subtitles(metadata.subtitle_url)
        print(f"   Parsed {len(subtitles)} subtitles")
        return subtitles
    print("⚠️  No subtitles available")
    return []


def generate_summary_stats(chapters: list[Chapter]) -> None:
    """Print summary statistics for the processed transcript.

    Args:
        chapters: List of chapters with subtitles
    """
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


def convert_youtube_to_xml(video_url: str) -> str:
    """Convert YouTube video to XML transcript with metadata.

    Core business logic that:
    1. Fetches video metadata
    2. Downloads and parses subtitles
    3. Assigns subtitles to chapters
    4. Creates XML document

    Args:
        video_url: YouTube video URL

    Returns:
        XML content as string
    """
    print(f"🎬 Processing: {video_url}")

    # Step 1: Fetch all metadata
    print("📊 Fetching video metadata...")
    metadata = fetch_video_metadata(video_url)
    print(f"   Title: {metadata.video_title}")
    print(f"   Duration: {format_duration(metadata.duration)}")

    # Step 2: Download and parse subtitles
    subtitles = fetch_and_parse_subtitles(metadata)

    # Step 3: Assign subtitles to chapters
    chapters_count = len(metadata.chapters_data) if metadata.chapters_data else 1
    print(f"📑 Organising into {chapters_count} chapter(s)...")
    chapters = assign_subtitles_to_chapters(metadata, subtitles)

    # Step 4: Create XML
    print("🔧 Building XML document...")
    xml_content = create_xml_document(metadata, chapters)

    # Summary statistics
    generate_summary_stats(chapters)

    return xml_content


def save_transcript(video_url: str, output_file: str) -> None:
    """Convert YouTube video to XML and save to file.

    Handles the file I/O operation separate from business logic.

    Args:
        video_url: YouTube video URL
        output_file: Path for output XML file
    """
    # Fetch metadata to get title for filename generation
    metadata = fetch_video_metadata(video_url)

    # Use dynamic filename if default was provided
    if output_file == DEFAULT_OUTPUT_FILE:
        output_file = sanitize_title_for_filename(metadata.video_title)

    # Generate XML content
    xml_content = convert_youtube_to_xml(video_url)

    # Save to file
    output_path = Path(output_file)
    output_path.write_text(xml_content, encoding="utf-8")

    print(f"✅ Saved to: {output_path.absolute()}")


def parse_arguments(args: list[str]) -> tuple[str, str] | None:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (typically sys.argv)

    Returns:
        Tuple of (video_url, output_file) if valid, None if invalid
    """
    if len(args) < MIN_ARGS_REQUIRED:
        return None

    video_url = args[1]
    output_file = (
        args[OUTPUT_ARG_INDEX] if len(args) > OUTPUT_ARG_INDEX else DEFAULT_OUTPUT_FILE
    )
    return video_url, output_file


def main() -> None:
    """Command-line interface entry point."""
    result = parse_arguments(sys.argv)
    if result is None:
        print("YouTube to XML Converter with Metadata")
        print(
            "Usage: uv run scripts/transcript_auto_fetcher.py <YouTube_URL> [output_file]"
        )
        print(
            "Example: uv run scripts/transcript_auto_fetcher.py "
            "https://youtu.be/VIDEO_ID output.xml"
        )
        sys.exit(1)

    video_url, output_file = result

    try:
        save_transcript(video_url, output_file)
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except (ValueError, OSError) as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
