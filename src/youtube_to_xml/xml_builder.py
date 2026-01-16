"""XML builder module for YouTube transcript conversion.

Converts parsed Chapter objects into XML format following the specified template.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from youtube_to_xml.time_utils import (
    format_video_duration,
    format_video_published,
    seconds_to_timestamp,
)

if TYPE_CHECKING:
    from youtube_to_xml.models import TranscriptDocument


def _create_transcript_root_element(
    title: str = "", published: str = "", duration: str = "", url: str = ""
) -> ET.Element:
    """Create root transcript element with metadata attributes."""
    root = ET.Element("transcript")
    root.set("video_title", title)
    root.set("video_published", published)
    root.set("video_duration", duration)
    root.set("video_url", url)
    return root


def _create_chapter_element(
    parent: ET.Element, title: str, start_time: float
) -> ET.Element:
    """Create chapter element with title and formatted start time."""
    chapter_elem = ET.SubElement(parent, "chapter")
    chapter_elem.set("title", title)
    chapter_elem.set("start_time", seconds_to_timestamp(start_time))
    return chapter_elem


def _format_transcript_lines(transcript_lines: list) -> list[str]:
    """Format TranscriptLine objects as alternating timestamp/text pairs."""
    lines = []
    for line in transcript_lines:
        lines.append(seconds_to_timestamp(line.timestamp))
        lines.append(line.text)
    return lines


def _add_indented_content(element: ET.Element, lines: list[str]) -> None:
    """Add indented text content to XML element."""
    if lines:
        indented = [f"      {line}" for line in lines]
        element.text = "\n" + "\n".join(indented) + "\n    "


def _finalise_xml(root: ET.Element) -> str:
    """Apply indentation and convert to XML string with declaration."""
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"


def transcript_to_xml(document: TranscriptDocument) -> str:
    """Build XML from TranscriptDocument with formatted metadata.

    This is the new interface that both parsers will use.
    Formats metadata using time_utils and handles TranscriptLine objects.
    """
    transcript_root = _create_transcript_root_element(
        document.metadata.video_title,
        format_video_published(document.metadata.video_published),
        format_video_duration(document.metadata.video_duration),
        document.metadata.video_url,
    )
    chapters_elem = ET.SubElement(transcript_root, "chapters")

    for chapter in document.chapters:
        chapter_elem = _create_chapter_element(
            chapters_elem, chapter.title, chapter.start_time
        )
        if chapter.transcript_lines:
            formatted_lines = _format_transcript_lines(chapter.transcript_lines)
            _add_indented_content(chapter_elem, formatted_lines)

    return _finalise_xml(transcript_root)
