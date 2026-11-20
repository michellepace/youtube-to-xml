# 0004. One yt-dlp lookup, choose a language, then download JSON3

**Status:** Accepted (recorded retroactively, 2026-11-20)

Replaces the `a)`/`b)`/`c)` step comments in `url_parser._download_transcript_with_yt_dlp` and the newline note in `_extract_transcript_lines_from_json3`.

## Context

Which transcript language to download ([ADR 0005](0005-english-transcript-preference.md)) depends on the caption lists that only a lookup returns. Doing a lookup and then a separate download would contact YouTube twice for the same video.

## Decision

1. Call `extract_info(url, download=False, process=False)` once. This returns the caption lists without processing formats or subtitles.
2. A watch URL with `&list=` first returns a `_type: "url"` pointer to the plain video. Follow pointers, checking each result is a single YouTube video, until the real video comes back.
3. Choose the language from `subtitles` and `automatic_captions`, then set `ydl.params["subtitleslangs"]`.
4. Call `process_ie_result` on **that same lookup result** with `download=True`. This writes only the subtitle file (`skip_download`), in JSON3 format.
5. When parsing JSON3, join each event's `segs` and replace `\n` with a space. YouTube inserts the line breaks for on-screen wrapping, and they are not part of the speech.

## Consequences

- One network lookup per video, and a playlist-style watch URL handles only its single video.
- The code depends on yt-dlp details: `process=False`, `_type: "url"` pointers, and mutating `ydl.params` between the two calls. A yt-dlp upgrade can break this, and the slow tests are what would catch it.
