# 0005. Prefer creator-uploaded English over YouTube's captions

**Status:** Accepted (recorded retroactively, 2026-11-20)

Replaces field comments on `_YtDlpMetadata.subtitles` and `automatic_captions` in `url_parser.py`.

## Context

yt-dlp reports two caption lists, both keyed by language code:

- `subtitles`: tracks the creator uploaded. These are usually hand-checked, with punctuation, music cues and speaker changes.
- `automatic_captions`: tracks YouTube generated. `en-orig` is speech-to-text of English speech. `en` there is often a machine translation of another language.

## Decision

Download exactly one track, chosen in this order (`_select_transcript_language`):

1. Creator-uploaded `en`, then regional English (`en-GB`, `en-US`, …) in A–Z order.
2. YouTube's `en-orig`.
3. YouTube's `en` (machine translation).

If none of these exist, raise `URLTranscriptNotFoundError`.

## Consequences

- The best available English text is used, and the output is deterministic for a given video.
- The CLI cannot produce a transcript in another language.
