#!/usr/bin/env python3
"""Manual test script to demonstrate XML builder working with parser output."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from youtube_to_xml.parser import parse_transcript
from youtube_to_xml.xml_builder import chapters_to_xml


def main() -> int:
    """Run the XML builder pipeline on a transcript file."""
    # Constants
    required_args = 2  # script name + input file

    # Require input file
    if len(sys.argv) < required_args:
        print("Usage: python test_xml_builder_manual.py <transcript_file>")
        print(
            "Example: python test_xml_builder_manual.py "
            "transcript_files/sample-11-chapters.txt"
        )
        return 1

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File '{input_file}' not found")
        return 1

    print(f"Processing: {input_file}")
    transcript_text = input_file.read_text(encoding="utf-8")

    # Parse transcript
    chapters = parse_transcript(transcript_text)
    print(f"✓ Parsed {len(chapters)} chapters")

    # Build XML
    xml_output = chapters_to_xml(chapters)
    print("✓ Generated XML")

    # Save output
    output_file = input_file.with_suffix(".xml")
    output_file.write_text(xml_output, encoding="utf-8")
    print(f"✓ Saved to: {output_file}")

    # Validate
    try:
        tree = ET.parse(output_file)  # noqa: S314
        parsed_root = tree.getroot()
        chapter_count = len(parsed_root.findall(".//chapter"))
        print(f"✓ XML validated ({chapter_count} chapters)")
    except ET.ParseError as e:
        print(f"✗ XML validation failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
