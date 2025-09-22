"""Convert YouTube videos to XML files with transcript lines organized by chapters.

This script downloads YouTube transcripts and creates structured XML files using
shared models and xml_builder infrastructure.

Usage:
    uv run scripts/url_to_transcript.py <YouTube_URL>

Example:
    uv run scripts/url_to_transcript.py https://youtu.be/Q4gsvJvRjCU

For a provided YouTube URL, the script will:
1. Fetch the video metadata (title, published date, duration)
2. Download and parse transcript lines (the timestamped text from YouTube's transcript)
3. Assign transcript lines to chapters (using YouTube's chapter markers if available)
4. Create TranscriptDocument and generate XML using shared xml_builder

Transcript priority:
1. Manual English transcript uploaded by the video creator (highest quality)
2. Auto-generated English transcript (fallback)
No other languages are downloaded - English only.
"""

import re
import sys
from pathlib import Path

from youtube_to_xml.exceptions import (
    URLBotProtectionError,
    URLIncompleteError,
    URLIsInvalidError,
    URLNotYouTubeError,
    URLRateLimitError,
    URLTranscriptNotFoundError,
    URLUnmappedError,
    URLVideoUnavailableError,
)
from youtube_to_xml.logging_config import get_logger, setup_logging
from youtube_to_xml.url_parser import parse_youtube_url
from youtube_to_xml.xml_builder import transcript_to_xml

# Module-level logger
logger = get_logger(__name__)


def sanitise_title_for_filename(title: str) -> str:
    """Convert video title to safe filename by sanitising characters.

    Removes non-alphanumeric characters and normalises spacing/hyphens.
    Adds .xml extension to the sanitised title.
    """
    # Remove non-alphanumeric characters except spaces and hyphens
    safe_title = re.sub(r"[^\w\s-]", "", title.lower())
    # Replace spaces and multiple hyphens with single hyphen
    safe_title = re.sub(r"[\s_-]+", "-", safe_title).strip("-")
    return f"{safe_title}.xml"


def convert_youtube_to_xml(video_url: str) -> tuple[str, int]:
    """Convert YouTube video to XML transcript with metadata.

    Core business logic that uses url_parser module to get structured transcript
    and generates XML using shared xml_builder.

    Args:
        video_url: YouTube video URL

    Returns:
        Tuple of (XML content as string, transcript lines count)
    """
    # Step 1: Parse URL and get structured transcript document
    try:
        document = parse_youtube_url(video_url)
    except URLTranscriptNotFoundError:
        logger.warning("No transcript available for video: %s", video_url)
        raise  # Re-raise to prevent file creation (no useless empty files)
    except URLRateLimitError:
        logger.exception("Rate limit hit for video: %s", video_url)
        raise  # Re-raise to prevent file creation

    # Step 2: Generate XML using shared xml_builder
    xml_output = transcript_to_xml(document)

    # Calculate total transcript lines for logging
    transcript_lines_count = sum(
        len(chapter.transcript_lines) for chapter in document.chapters
    )

    return xml_output, transcript_lines_count


def convert_and_save_youtube_xml(video_url: str) -> Path:
    """Convert YouTube video to XML and save to file.

    Handles the file I/O operation separate from business logic.
    Uses dynamic filename based on video title.

    Args:
        video_url: YouTube video URL

    Returns:
        Output file path
    """
    # Generate XML content and get transcript lines count
    xml_output, transcript_lines_count = convert_youtube_to_xml(video_url)

    # Parse document again to get metadata for filename and logging
    # (This is slightly inefficient but keeps the interface clean)
    document = parse_youtube_url(video_url)

    # Log processing results for operational visibility
    logger.info(
        "Generated XML with %d chapters and %d transcript lines for video: %s",
        len(document.chapters),
        transcript_lines_count,
        video_url,
    )

    # Save to file
    output_filename = sanitise_title_for_filename(document.metadata.video_title)
    if output_filename == ".xml":
        output_filename = "transcript-untitled.xml"
    output_path = Path(output_filename)
    output_path.write_text(xml_output, encoding="utf-8")

    logger.info("Successfully created: %s for video: %s", output_path.name, video_url)

    return output_path


def main() -> None:
    """Command-line interface entry point."""
    setup_logging()

    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:  # noqa: PLR2004
        print("YouTube URL to XML Converter")
        print("  Usage: include the YouTube URL as an argument")
        print("  E.g.: url_to_transcript.py https://www.youtube.com/watch?v=Q4gsvJvRjCU")
        sys.exit(1)

    video_url = sys.argv[1]

    try:
        print(f"🎬 Processing: {video_url}")
        output_path = convert_and_save_youtube_xml(video_url)

        print(f"✅ Created: {output_path.name}")
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except (
        URLBotProtectionError,
        URLIncompleteError,
        URLIsInvalidError,
        URLNotYouTubeError,
        URLTranscriptNotFoundError,
        URLRateLimitError,
        URLUnmappedError,
        URLVideoUnavailableError,
    ) as e:
        logger.info(
            "Processing failed for video: %s - %s: %s", video_url, type(e).__name__, e
        )
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except (ValueError, OSError) as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception(
            "Unexpected error for video: %s - %s", video_url, type(e).__name__
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
