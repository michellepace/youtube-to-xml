# 0006. Slow tests run against pinned live YouTube videos

**Status:** Accepted (recorded retroactively, 2026-11-20)

Replaces a comment on `URL_CHAPTERS` in `tests/test_end_to_end.py`.

## Context

The project avoids mocks. The URL path depends on YouTube and yt-dlp, whose behaviour changes without notice.

## Decision

Tests marked `@pytest.mark.slow` call the real CLI against specific public videos. Byte-for-byte comparisons against files in `example_transcripts/` only use videos with **creator-uploaded captions and chapters**, because those stay stable. Auto-generated captions are re-generated over time and would make the reference files drift.

## Consequences

- yt-dlp or YouTube changes are caught by the next `pytest -m slow` (run on pre-push).
- The slow tests need network access and are exposed to rate limiting and bot checks. They are meant to skip rather than fail in that case, but the skip patterns are currently stale ([issue draft 06](../issues/06-slow-test-rate-limit-skip-never-matches.md)).
- If a pinned video is edited or removed, its reference file must be regenerated or the video replaced.
