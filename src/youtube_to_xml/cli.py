"""YouTube to XML converter CLI entry point."""

import argparse
import sys
from pathlib import Path

from youtube_to_xml.exceptions import (
    EmptyFileError,
    InvalidTranscriptFormatError,
    MissingTimestampError,
)
from youtube_to_xml.parser import parse_transcript
from youtube_to_xml.xml_builder import chapters_to_xml


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
   - 3rd line: (non-timestamp) → first content line of first chapter

💡 Check that your transcript follows this basic pattern
""",
    )
    parser.add_argument(
        "transcript",
        metavar="transcript.txt",
        help="YouTube transcript text file to convert",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for YouTube to XML converter."""
    args = parse_arguments()
    transcript_path = Path(args.transcript)

    # Read the input file
    try:
        raw_content = transcript_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ We couldn't find your file: {transcript_path}")
        sys.exit(1)
    except PermissionError:
        print(f"❌ We don't have permission to access: {transcript_path}")
        sys.exit(1)

    # Parse the transcript
    try:
        chapters = parse_transcript(raw_content)
    except EmptyFileError:
        print(f"❌ Your file is empty: {transcript_path}")
        sys.exit(1)
    except (InvalidTranscriptFormatError, MissingTimestampError):
        print(f"❌ Wrong format in '{transcript_path}' - run 'youtube-to-xml --help'")
        sys.exit(1)

    # Generate XML
    xml_content = chapters_to_xml(chapters)

    # Create output directory and write XML
    output_dir = Path("transcript_files")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_filename = transcript_path.stem + ".xml"
    output_path = output_dir / output_filename

    try:
        output_path.write_text(xml_content, encoding="utf-8")
    except PermissionError:
        print(f"❌ Cannot write to: {output_path}")
        sys.exit(1)

    # Success message
    print(f"✅ Created: {output_path}")
