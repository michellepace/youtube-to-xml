"""YouTube to XML converter CLI entry point."""

import argparse
import sys
import uuid
from pathlib import Path

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
    URLBotProtectionError,
    URLIncompleteError,
    URLIsInvalidError,
    URLNotYouTubeError,
    URLRateLimitError,
    URLTranscriptNotFoundError,
    URLUnmappedError,
    URLVideoUnavailableError,
)
from youtube_to_xml.file_parser import parse_transcript_file
from youtube_to_xml.logging_config import get_logger, setup_logging
from youtube_to_xml.url_parser import parse_youtube_url
from youtube_to_xml.xml_builder import transcript_to_xml


def is_youtube_url(input_string: str) -> bool:
    """Detect if input is a YouTube URL."""
    youtube_patterns = ["youtube.com", "youtu.be"]
    return any(pattern in input_string.lower() for pattern in youtube_patterns)


def _sanitize_video_title_for_filename(video_title: str) -> str:
    """Convert video title to safe filename by removing special characters."""
    sanitized = video_title.lower()
    sanitized = "".join(c if c.isalnum() or c in " -" else "" for c in sanitized)
    sanitized = sanitized.replace(" ", "-").strip("-")
    return f"{sanitized}.xml" if sanitized else "transcript.xml"


def _process_url_input(url: str, execution_id: str) -> tuple[str, str]:
    """Process YouTube URL input and return XML content and output filename.

    Args:
        url: YouTube URL to process
        execution_id: Unique ID for logging purposes

    Returns:
        Tuple of (xml_content, output_filename)

    Raises:
        URL*Error: Various YouTube processing errors
    """
    logger = get_logger(__name__)
    logger.info("[%s] Detected YouTube URL, using URL parser", execution_id)

    print(f"🎬 Processing: {url}")
    document = parse_youtube_url(url)
    xml_content = transcript_to_xml(document)
    output_filename = _sanitize_video_title_for_filename(document.metadata.video_title)

    return xml_content, output_filename


def _process_file_input(file_path_str: str, execution_id: str) -> tuple[str, str]:
    """Process transcript file input and return XML content and output filename.

    Args:
        file_path_str: Path to transcript file as string
        execution_id: Unique ID for logging purposes

    Returns:
        Tuple of (xml_content, output_filename)

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
        UnicodeDecodeError: If file isn't UTF-8 encoded
        FileEmptyError: If file is empty
        FileInvalidFormatError: If file format is invalid
    """
    logger = get_logger(__name__)
    logger.info("[%s] Detected file path, using file parser", execution_id)

    transcript_file_path = Path(file_path_str)

    # Read file content
    try:
        raw_transcript_text = transcript_file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ We couldn't find your file: {transcript_file_path}")
        logger.error("[%s] FileNotFoundError: %s", execution_id, transcript_file_path)
        sys.exit(1)
    except PermissionError:
        print(f"❌ We don't have permission to access: {transcript_file_path}")
        logger.error(
            "[%s] PermissionError reading: %s", execution_id, transcript_file_path
        )
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"❌ File is not UTF-8 encoded: {transcript_file_path}")
        logger.error(
            "[%s] UnicodeDecodeError reading: %s", execution_id, transcript_file_path
        )
        sys.exit(1)

    # Parse transcript and generate XML
    try:
        document = parse_transcript_file(raw_transcript_text)
        xml_content = transcript_to_xml(document)
        output_filename = f"{transcript_file_path.stem}.xml"
    except FileEmptyError:
        print(f"❌ Your file is empty: {transcript_file_path}")
        logger.error("[%s] FileEmptyError: %s", execution_id, transcript_file_path)
        sys.exit(1)
    except FileInvalidFormatError:
        print(
            f"❌ Wrong format in '{transcript_file_path}' - run 'youtube-to-xml --help'"
        )
        logger.error(
            "[%s] FileInvalidFormatError: %s", execution_id, transcript_file_path
        )
        sys.exit(1)

    return xml_content, output_filename


def _save_xml_output(xml_content: str, output_filename: str, execution_id: str) -> None:
    """Save XML content to file and display success message.

    Args:
        xml_content: XML content to write
        output_filename: Name of output file to create
        execution_id: Unique ID for logging purposes

    Raises:
        SystemExit: If file write fails
    """
    logger = get_logger(__name__)
    output_file_path = Path(output_filename)

    try:
        output_file_path.write_text(xml_content, encoding="utf-8")
    except (PermissionError, OSError):
        print(f"❌ Cannot write to: {output_file_path}")
        logger.exception("[%s] Write failed: %s", execution_id, output_file_path)
        sys.exit(1)

    # Success message
    print(f"✅ Created: {output_file_path}")
    logger.info("[%s] Successfully created: %s", execution_id, output_file_path)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="youtube-to-xml",
        description="Convert YouTube transcripts to XML format with chapter detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""✅ Example YouTube Transcript

📋 EXPECTED FORMAT:
   ┌─────────────────────────────────────────
   │ Introduction to Bret Taylor
   │ 00:04
   │ You're CTO of Meta and and co-CEO of...
   └─────────────────────────────────────────

🔧 REQUIREMENTS:
   - 1st line: (non-timestamp) → becomes first chapter
   - 2nd line: (timestamp e.g. "0:03") → becomes start_time for first chapter
   - 3rd line: (non-timestamp) → first transcript line of first chapter

💡 Check that your transcript follows this basic pattern
""",
    )
    parser.add_argument(
        "transcript",
        metavar="transcript.txt|URL",
        help="YouTube transcript text file OR YouTube URL to convert",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for YouTube to XML converter."""
    setup_logging()
    logger = get_logger(__name__)
    execution_id = str(uuid.uuid4())[:8]

    args = parse_arguments()
    user_input = args.transcript

    logger.info("[%s] Starting CLI execution for: %s", execution_id, user_input)

    # Route based on input type and process accordingly
    try:
        if is_youtube_url(user_input):
            xml_content, output_filename = _process_url_input(user_input, execution_id)
        else:
            xml_content, output_filename = _process_file_input(user_input, execution_id)

        _save_xml_output(xml_content, output_filename, execution_id)

    except (
        URLBotProtectionError,
        URLIncompleteError,
        URLIsInvalidError,
        URLNotYouTubeError,
        URLRateLimitError,
        URLTranscriptNotFoundError,
        URLUnmappedError,
        URLVideoUnavailableError,
    ) as url_error:
        print(f"❌ Error processing URL: {url_error}")
        logger.error("[%s] URL processing failed: %s", execution_id, url_error)
        sys.exit(1)
