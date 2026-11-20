# 0003. Models hold raw values; formatting happens at output

**Status:** Accepted (recorded retroactively, 2026-11-20)

Replaces field comments in `models.py` and `url_parser.py` (`_create_video_metadata`).

## Context

The file and URL parsers both produce a `TranscriptDocument`. yt-dlp gives dates as `YYYYMMDD` and durations as whole seconds. The XML output wants `YYYY-MM-DD`, `2m 43s` and `M:SS`.

## Decision

The models store values exactly as they come in, and only `xml_builder` formats them, using `time_utils`:

| Field | Raw value | File input |
| --- | --- | --- |
| `VideoMetadata.video_published` | `YYYYMMDD` string | `""` |
| `VideoMetadata.video_duration` | whole seconds (`int`) | `0` |
| `TranscriptLine.timestamp`, `Chapter.start_time`, `Chapter.end_time` | seconds (`float`), last chapter ends at `math.inf` | same |

A transcript file has no video metadata, so its `VideoMetadata` is the empty default.

## Consequences

- The parsers can be tested with plain numbers, and arithmetic on times stays simple.
- Display formats change in one place.
- The units are a contract between modules. They are written down here and in the field docstrings, because the types alone (`str`, `int`, `float`) do not say them.
