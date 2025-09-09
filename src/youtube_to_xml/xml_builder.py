"""XML builder module for YouTube transcript conversion.

Converts parsed Chapter objects into XML format following the specified template.
"""

import xml.etree.ElementTree as ET

from youtube_to_xml.file_parser import Chapter
from youtube_to_xml.time_utils import seconds_to_timestamp


def chapters_to_xml(chapters: list[Chapter]) -> str:
    """Build complete YouTube transcript XML document from chapters."""
    # Create root XML tag element <transcript>
    root = ET.Element("transcript")
    root.set("video_title", "")
    root.set("upload_date", "")
    root.set("duration", "")
    root.set("video_url", "")

    # Add XML container tag element <chapters>
    chapters_elem = ET.SubElement(root, "chapters")

    # Create XML child tag elements <chapter>
    for chapter in chapters:
        chapter_elem = ET.SubElement(chapters_elem, "chapter")
        chapter_elem.set("title", chapter.title)
        chapter_elem.set("start_time", seconds_to_timestamp(chapter.start_time))

        # Add content as text with proper indentation (6 spaces per line)
        if chapter.content_lines:
            indented_lines = [f"      {line}" for line in chapter.content_lines]
            chapter_elem.text = "\n" + "\n".join(indented_lines) + "\n    "

    # Indent XML tag elements recursively (2 spaces per level)
    ET.indent(root, space="  ")

    # Generate formatted XML string with declaration
    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"
