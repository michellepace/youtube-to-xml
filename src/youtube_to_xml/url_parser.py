"""YouTube URL parser module for extracting transcripts and metadata.

Provides the main interface for parsing YouTube URLs into TranscriptDocument objects.

Public API:
    parse_youtube_url(url: str) -> TranscriptDocument
    is_valid_url(url: str) -> bool
"""

import json
import math
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast
from urllib.parse import urlparse

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError, UnsupportedError

from youtube_to_xml.exceptions import (
    URLIsInvalidError,
    URLNotYouTubeError,
    URLPlaylistNotSupportedError,
    URLTranscriptNotFoundError,
    URLUnmappedError,
    map_yt_dlp_exception,
)
from youtube_to_xml.logging_config import get_logger
from youtube_to_xml.models import (
    Chapter,
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)
from youtube_to_xml.time_utils import MILLISECONDS_PER_SECOND


# Private TypedDict definitions for internal data structures
class _InternalChapterDict(TypedDict):
    """Internal type for YouTube API chapter data."""

    title: str
    start_time: float
    end_time: float


class _YtDlpMetadata(TypedDict, total=False):
    """Internal type for the yt-dlp metadata fields we access."""

    title: str
    upload_date: str
    duration: int
    webpage_url: str
    chapters: list[_InternalChapterDict]
    subtitles: dict[str, object]  # creator-uploaded tracks, keyed by language code
    automatic_captions: dict[str, object]  # YouTube-generated tracks, same keys


class _Json3Seg(TypedDict, total=False):
    """Internal type for JSON3 transcript segment."""

    utf8: str


class _Json3Event(TypedDict, total=False):
    """Internal type for JSON3 transcript event."""

    tStartMs: int
    segs: list[_Json3Seg]


# Subtitle/transcript file extension for yt-dlp
_TRANSCRIPT_FILE_EXT = "json3"

# Base name for the downloaded transcript file (yt-dlp appends ".<lang>.json3")
_TRANSCRIPT_FILE_STEM = "transcript"

_YOUTUBE_DOMAINS = ("youtube.com", "youtu.be", "m.youtube.com", "www.youtube.com")

# Module-level logger
logger = get_logger(__name__)


def _select_transcript_language(
    creator_langs: Iterable[str], auto_langs: Iterable[str]
) -> str | None:
    """Choose the one subtitle language code to download from YouTube.

    Preference order:
    1. Creator-uploaded English: "en", then regional codes such as "en-GB" (A-Z)
    2. YouTube's speech-to-text of English speech: "en-orig"
    3. YouTube's machine translation of foreign speech into English: "en"

    Args:
        creator_langs: Language codes of creator-uploaded subtitles
        auto_langs: Language codes of YouTube's automatic captions

    Returns:
        Language code to download, or None if the video has no English transcript
    """
    creator_english = sorted(
        (lang for lang in creator_langs if lang == "en" or lang.startswith("en-")),
        key=lambda lang: (lang != "en", lang),  # plain "en" first, then A-Z
    )
    if creator_english:
        return creator_english[0]

    available_auto = set(auto_langs)
    for lang in ("en-orig", "en"):
        if lang in available_auto:
            return lang
    return None


def _validate_basic_url_structure(url: str) -> None:
    """Validate basic URL structure before expensive operations.

    Checks scheme, netloc, and TLD presence.
    Rejects obviously invalid URLs instantly, without a network call.

    Args:
        url: URL string to validate

    Raises:
        URLIsInvalidError: If URL lacks scheme, netloc, or TLD
    """
    try:
        parsed = urlparse(url)
        if not (parsed.scheme and parsed.netloc and "." in parsed.netloc):
            raise URLIsInvalidError
    except ValueError:
        raise URLIsInvalidError from None


def is_valid_url(url: str) -> bool:
    """Check if input has valid URL structure (scheme, netloc, TLD)."""
    try:
        _validate_basic_url_structure(url)
    except URLIsInvalidError:
        return False
    else:
        return True


def _create_video_metadata(raw_metadata: _YtDlpMetadata, url: str) -> VideoMetadata:
    """Build VideoMetadata object from raw yt-dlp metadata.

    Args:
        raw_metadata: Raw metadata dictionary from yt-dlp
        url: Original YouTube URL (fallback for webpage_url)

    Returns:
        VideoMetadata object with extracted information
    """
    return VideoMetadata(
        video_title=raw_metadata.get("title", "Untitled"),
        video_published=raw_metadata.get("upload_date", ""),  # Raw YYYYMMDD
        video_duration=int(raw_metadata.get("duration", 0)),  # Raw seconds as int
        video_url=raw_metadata.get("webpage_url", url),
    )


def _validate_is_youtube_url(url: str) -> None:
    """Reject malformed and non-YouTube URLs before any network call.

    Raises:
        URLIsInvalidError: If URL lacks scheme, netloc, or TLD
        URLNotYouTubeError: If URL domain is not YouTube
    """
    _validate_basic_url_structure(url)
    if urlparse(url).netloc.lower() not in _YOUTUBE_DOMAINS:
        raise URLNotYouTubeError


def _validate_is_single_youtube_video(video_info: Mapping[str, Any]) -> None:
    """Reject yt-dlp lookup results that are not a single YouTube video.

    Raises:
        URLIsInvalidError: If yt-dlp returned nothing
        URLNotYouTubeError: If yt-dlp used a non-YouTube extractor (e.g. redirect)
        URLPlaylistNotSupportedError: If URL is a YouTube playlist
    """
    # Stubs say non-None, but yt-dlp can return None at runtime
    if video_info is None:  # type: ignore[reportUnnecessaryComparison]
        raise URLIsInvalidError

    if "youtube" not in video_info.get("extractor", "").lower():
        raise URLNotYouTubeError

    if video_info.get("_type") == "playlist":
        raise URLPlaylistNotSupportedError


def _download_transcript_with_yt_dlp(
    url: str, temp_dir: Path
) -> tuple[_YtDlpMetadata, Path]:
    """Look up a YouTube video once, then download its best English transcript.

    Args:
        url: YouTube video URL
        temp_dir: Temporary directory for downloaded files

    Returns:
        Tuple of (raw metadata dictionary from yt-dlp, downloaded transcript file)

    Raises:
        URLTranscriptNotFoundError: If the video has no English transcript
    """
    _validate_is_youtube_url(url)

    yt_dlp_options = {
        # Core purpose: Download transcripts (language chosen after the lookup)
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": _TRANSCRIPT_FILE_EXT,
        # Download behavior: Skip video, only get transcripts
        "skip_download": True,
        "noplaylist": True,
        # Output formatting: Where to save files
        "outtmpl": str(temp_dir / f"{_TRANSCRIPT_FILE_STEM}.%(ext)s"),
        # UI/UX: Quiet operation for CLI user experience
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }

    with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:  # type: ignore[reportArgumentType]
        try:
            # a) YT-DLP: look up the video once (formats/subtitles not yet processed)
            unprocessed_metadata = ydl.extract_info(url, download=False, process=False)
            _validate_is_single_youtube_video(unprocessed_metadata)
            # A watch URL carrying "&list=" first yields a pointer to the plain
            # video URL, so follow pointers until the actual video lookup comes back
            while unprocessed_metadata.get("_type") == "url":
                pointer_url = unprocessed_metadata.get("url")
                if not pointer_url:
                    raise URLIsInvalidError
                unprocessed_metadata = ydl.extract_info(
                    pointer_url,
                    download=False,
                    process=False,
                    ie_key=unprocessed_metadata.get("ie_key"),
                )
                _validate_is_single_youtube_video(unprocessed_metadata)
            # b) Choose the one language to download from the lookup's caption lists
            transcript_lang = _select_transcript_language(
                creator_langs=unprocessed_metadata.get("subtitles", {}),
                auto_langs=unprocessed_metadata.get("automatic_captions", {}),
            )
            if transcript_lang is None:
                raise URLTranscriptNotFoundError
            logger.info("Selected transcript language: %s", transcript_lang)
            ydl.params["subtitleslangs"] = [transcript_lang]
            # c) YT-DLP: process that same lookup, writing the subtitle file (.json3)
            raw_metadata = ydl.process_ie_result(unprocessed_metadata, download=True)
        except (DownloadError, ExtractorError, UnsupportedError) as e:
            mapped_exception = map_yt_dlp_exception(e)
            raise mapped_exception from e

    # Stubs say non-None, but yt-dlp can return None at runtime
    if raw_metadata is None:  # type: ignore[reportUnnecessaryComparison]
        msg = "Something weird happened, we couldn't get this video's information."
        raise URLUnmappedError(msg)
    transcript_file = (
        temp_dir / f"{_TRANSCRIPT_FILE_STEM}.{transcript_lang}.{_TRANSCRIPT_FILE_EXT}"
    )
    return cast("_YtDlpMetadata", raw_metadata), transcript_file


def _extract_transcript_lines_from_file(transcript_file: Path) -> list[TranscriptLine]:
    """Process the downloaded transcript file into TranscriptLine objects.

    Args:
        transcript_file: JSON3 transcript file written by yt-dlp

    Returns:
        List of TranscriptLine objects

    Raises:
        URLTranscriptNotFoundError: If yt-dlp did not write the transcript file
    """
    if not transcript_file.is_file():
        raise URLTranscriptNotFoundError

    # Read JSON3 format from disk
    transcript_data = json.loads(transcript_file.read_text(encoding="utf-8"))
    # Extract events → TranscriptLine objects
    events = transcript_data.get("events", [])
    return _extract_transcript_lines_from_json3(events)


def _fetch_video_metadata_and_transcript(
    url: str,
) -> tuple[VideoMetadata, list[TranscriptLine], list[_InternalChapterDict]]:
    """Extract video metadata and download transcript from YouTube using yt-dlp.

    Orchestrates the download and processing of YouTube video data by
    coordinating helper functions for downloading and metadata creation.

    Args:
        url: YouTube video URL

    Returns:
        Tuple of (VideoMetadata object, list of TranscriptLine objects,
                 list of _InternalChapterDict objects from YouTube API)
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Phase 1: Download transcript and metadata using yt-dlp
        raw_metadata, transcript_file = _download_transcript_with_yt_dlp(
            url, Path(temp_dir)
        )

        # Phase 2: Process the downloaded transcript file
        transcript_lines = _extract_transcript_lines_from_file(transcript_file)

        # Phase 3: Create structured metadata object
        metadata = _create_video_metadata(raw_metadata, url)

        # Phase 4: Extract raw YouTube chapter data (kept separate from VideoMetadata)
        raw_youtube_chapters = raw_metadata.get("chapters", [])

        return metadata, transcript_lines, raw_youtube_chapters


def _extract_transcript_lines_from_json3(
    events: list[_Json3Event],
) -> list[TranscriptLine]:
    """Extract individual transcript lines from JSON3 event objects.

    Args:
        events: List of JSON3 event objects from YouTube transcript

    Returns:
        List of TranscriptLine objects with cleaned text and timestamps
    """
    transcript_lines: list[TranscriptLine] = []

    for event in events:
        # Skip events without transcript data
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

        transcript_lines.append(TranscriptLine(start_seconds, text))

    return transcript_lines


def _assign_transcript_lines_to_chapters(
    metadata: VideoMetadata,
    transcript_lines: list[TranscriptLine],
    chapter_dicts: list[_InternalChapterDict],
) -> list[Chapter]:
    """Assign transcript lines to chapters based on temporal boundaries.

    Args:
        metadata: Video metadata for title
        transcript_lines: List of all individual transcript lines
        chapter_dicts: List of internal chapter dictionaries

    Returns:
        List of Chapter objects with assigned transcript lines
    """
    if not chapter_dicts:
        # No chapters - create single chapter with video title
        return [
            Chapter(
                title=metadata.video_title,
                start_time=0,
                end_time=math.inf,
                transcript_lines=transcript_lines,
            )
        ]

    chapters: list[Chapter] = []

    for i, youtube_chapter_dict in enumerate(chapter_dicts):
        chapter_start_time = float(youtube_chapter_dict.get("start_time", 0))

        # End time is start of next chapter, or infinity for last chapter
        if i + 1 < len(chapter_dicts):
            chapter_end_time = float(chapter_dicts[i + 1]["start_time"])
        else:
            chapter_end_time = math.inf

        # Filter transcript lines within this chapter's time range
        chapter_transcript_lines = [
            line
            for line in transcript_lines
            if chapter_start_time <= line.timestamp < chapter_end_time
        ]

        chapters.append(
            Chapter(
                title=youtube_chapter_dict.get("title", f"Chapter {i + 1}"),
                start_time=chapter_start_time,
                end_time=chapter_end_time,
                transcript_lines=chapter_transcript_lines,
            )
        )

    return chapters


def parse_youtube_url(url: str) -> TranscriptDocument:
    """Parse YouTube URL and return structured transcript document.

    Main interface function that coordinates the complete URL processing pipeline:
    1. Fetch video metadata and transcript from YouTube (includes JSON3 extraction)
    2. Assign transcript lines to chapters
    3. Return complete TranscriptDocument

    Args:
        url: YouTube video URL

    Returns:
        TranscriptDocument with video metadata and chapters containing transcript lines

    Raises:
        BaseTranscriptError: Domain-level failures (e.g., yt-dlp mapped errors via
            map_yt_dlp_exception(), or URLTranscriptNotFoundError when no transcript
            exists).
    """
    logger.info("Processing video: %s", url)

    # Step 1: Fetch metadata and download transcript using yt-dlp
    metadata, transcript_lines, youtube_chapter_dicts = (
        _fetch_video_metadata_and_transcript(url)
    )

    # Step 2: Assign transcript lines to chapters
    chapters = _assign_transcript_lines_to_chapters(
        metadata, transcript_lines, youtube_chapter_dicts
    )

    # Step 3: Create and return TranscriptDocument
    return TranscriptDocument(metadata=metadata, chapters=chapters)
