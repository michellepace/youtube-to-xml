"""YouTube to XML converter CLI entry point."""

import argparse
import sys
import uuid
from pathlib import Path
from urllib.parse import urlparse

from youtube_to_xml.exceptions import (
    BaseTranscriptError,
    FileEncodingError,
    FileNotExistsError,
    FilePermissionError,
    InvalidInputError,
)
from youtube_to_xml.file_parser import parse_transcript_file
from youtube_to_xml.logging_config import get_logger, setup_logging
from youtube_to_xml.url_parser import parse_youtube_url
from youtube_to_xml.xml_builder import transcript_to_xml

ARGPARSE_ERROR_CODE = 2  # argparse uses exit code 2 for argument errors


def _is_valid_url(input_string: str) -> bool:
    """Check if input is a proper URL with scheme, netloc, and TLD."""
    try:
        parsed = urlparse(input_string)
        return bool(parsed.scheme and parsed.netloc and "." in parsed.netloc)
    except ValueError:
        return False


def _has_txt_extension(input_string: str) -> bool:
    """Check if input has .txt extension."""
    return Path(input_string).suffix.lower() == ".txt"


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
        URL*Error: Various YouTube processing errors (bubbled up from url_parser)
    """
    logger = get_logger(__name__)
    logger.info("[%s] Detected YouTube URL, using URL parser", execution_id)

    print(f"🎬 Processing: {url}")

    # Let all URL processing errors bubble up to main()
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
        FileNotExistsError: If file doesn't exist
        FilePermissionError: If file can't be read due to permissions
        FileEncodingError: If file isn't UTF-8 encoded
        FileEmptyError: If file is empty
        FileInvalidFormatError: If file format is invalid
    """
    logger = get_logger(__name__)
    logger.info("[%s] Detected file path, using file parser", execution_id)

    transcript_file_path = Path(file_path_str)

    # Read file content
    try:
        raw_transcript_text = transcript_file_path.read_text(encoding="utf-8")
    except FileNotFoundError:  # in-built
        raise FileNotExistsError from None
    except PermissionError:  # in-built
        raise FilePermissionError from None
    except UnicodeDecodeError:  # in-built
        raise FileEncodingError from None

    # Parse transcript and generate XML - let parsing errors bubble
    document = parse_transcript_file(raw_transcript_text)

    xml_content = transcript_to_xml(document)
    output_filename = f"{transcript_file_path.stem}.xml"
    return xml_content, output_filename


def _save_xml_output(xml_content: str, output_filename: str, execution_id: str) -> None:
    """Save XML content to file and display success message.

    Args:
        xml_content: XML content to write
        output_filename: Name of output file to create
        execution_id: Unique ID for logging purposes

    Raises:
        PermissionError: If file can't be written due to permissions
        OSError: If file write fails for other reasons
    """
    logger = get_logger(__name__)
    output_file_path = Path(output_filename)

    # Let write errors bubble up to main()
    output_file_path.write_text(xml_content, encoding="utf-8")

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
        metavar="YOUTUBE_URL or yt_transcript.txt",
        help="YouTube transcript text file OR YouTube URL to convert",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for YouTube to XML converter."""
    setup_logging()
    logger = get_logger(__name__)
    execution_id = str(uuid.uuid4())[:8]

    try:
        args = parse_arguments()
        user_input = args.transcript
    except SystemExit as e:
        if e.code == ARGPARSE_ERROR_CODE:
            # Display after argparse's message
            print("\nTry: youtube-to-xml --help", file=sys.stderr)
            sys.exit(1)
        else:
            # Re-raise other SystemExits (like --help which should exit normally)
            raise

    logger.info("[%s] Starting CLI execution for: %s", execution_id, user_input)

    # Main processing with single exception handler
    try:
        if _is_valid_url(user_input):
            xml_content, output_filename = _process_url_input(user_input, execution_id)
        elif _has_txt_extension(user_input):
            xml_content, output_filename = _process_file_input(user_input, execution_id)
        else:
            raise InvalidInputError

        _save_xml_output(xml_content, output_filename, execution_id)

    except BaseTranscriptError as e:
        # All our custom exceptions
        print(f"❌ {e}", file=sys.stderr)
        print("\nTry: youtube-to-xml --help", file=sys.stderr)
        logger.info("[%s] %s: %s", execution_id, type(e).__name__, e)
        sys.exit(1)
    except (PermissionError, OSError) as e:
        # System errors from file operations
        print(f"❌ {e}", file=sys.stderr)
        print("\nTry: youtube-to-xml --help", file=sys.stderr)
        logger.exception("[%s] System error", execution_id)
        sys.exit(1)
