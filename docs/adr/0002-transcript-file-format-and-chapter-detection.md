# 0002. Transcript file format and the 2-line chapter rule

**Status:** Accepted (recorded retroactively, 2026-11-20)

Replaces comments in `file_parser.py` (`LINES_FOR_CHAPTER_BOUNDARY`) and `time_utils.py` (`TIMESTAMP_PATTERN`).

## Context

A transcript copied from YouTube's transcript panel is plain text with no chapter markup. Each spoken line is a timestamp line followed by a text line. When chapters exist, the panel puts the chapter title on its own line just before the chapter's first timestamp.

## Decision

- **Chapter detection:** a new chapter starts when *exactly two* lines sit between consecutive timestamps. The first is the previous timestamp's text and the second is the new chapter's title. The file's first line is always the first chapter's title.
- **Timestamps** match `TIMESTAMP_PATTERN`: `M:SS`, `MM:SS`, `H:MM:SS`, `HH:MM:SS` or `HHH:MM:SS`, so hours are capped at 999. Seconds, and minutes in the three-part forms, must be `00`–`59`.
- Chapter start times must be strictly increasing, or the file is rejected.

## Consequences

- No markup is needed. A user pastes the panel's text as it is.
- A text line that wraps onto a second line next to a timestamp looks exactly like a chapter title, and nothing can tell them apart.
- In the two-part form the leading field accepts `0`–`99`, so `75:00` parses as 75 minutes. YouTube writes 1:15:00 instead, so this has not mattered.
