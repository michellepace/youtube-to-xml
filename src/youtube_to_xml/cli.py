"""YouTube to XML converter CLI entry point."""

import argparse
import sys
import uuid
from pathlib import Path

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
)
from youtube_to_xml.file_parser import parse_transcript_document, parse_transcript_file
from youtube_to_xml.logging_config import get_logger, setup_logging
from youtube_to_xml.xml_builder import chapters_to_xml, transcript_to_xml


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
        metavar="transcript.txt",
        type=Path,
        help="YouTube transcript text file to convert",
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy file parser (for compatibility verification)",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for YouTube to XML converter."""
    setup_logging()
    logger = get_logger(__name__)
    execution_id = str(uuid.uuid4())[:8]

    args = parse_arguments()
    transcript_path = args.transcript

    logger.info("[%s] Starting CLI execution for: %s", execution_id, transcript_path)

    # Read the input file
    try:
        raw_transcript_text = transcript_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ We couldn't find your file: {transcript_path}")
        logger.error("[%s] FileNotFoundError: %s", execution_id, transcript_path)
        sys.exit(1)
    except PermissionError:
        print(f"❌ We don't have permission to access: {transcript_path}")
        logger.error("[%s] PermissionError reading: %s", execution_id, transcript_path)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"❌ File is not UTF-8 encoded: {transcript_path}")
        logger.error("[%s] UnicodeDecodeError reading: %s", execution_id, transcript_path)
        sys.exit(1)

    # Parse the transcript and generate XML using dual-path logic
    try:
        if args.legacy:
            chapters = parse_transcript_file(raw_transcript_text)
            xml_output = chapters_to_xml(chapters)
            logger.info("[%s] Used legacy parser path", execution_id)
        else:
            document = parse_transcript_document(raw_transcript_text)
            xml_output = transcript_to_xml(document)
            logger.info("[%s] Used new parser path", execution_id)
    except FileEmptyError:
        print(f"❌ Your file is empty: {transcript_path}")
        logger.error("[%s] FileEmptyError: %s", execution_id, transcript_path)
        sys.exit(1)
    except FileInvalidFormatError:
        print(f"❌ Wrong format in '{transcript_path}' - run 'youtube-to-xml --help'")
        logger.error("[%s] FileInvalidFormatError: %s", execution_id, transcript_path)
        sys.exit(1)

    # Create output file in current directory
    output_filename = transcript_path.stem + ".xml"
    output_path = Path(output_filename)

    try:
        output_path.write_text(xml_output, encoding="utf-8")
    except PermissionError:
        print(f"❌ Cannot write to: {output_path}")
        logger.error("[%s] PermissionError writing: %s", execution_id, output_path)
        sys.exit(1)

    # Success message
    print(f"✅ Created: {output_path}")
    logger.info("[%s] Successfully created: %s", execution_id, output_path)
