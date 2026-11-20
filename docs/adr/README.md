# Architecture Decision Records

Decisions that are important and not obvious from the code live here, not in code comments ([ADR 0001](0001-ban-code-comments.md)).

| ADR | Decision |
| --- | --- |
| [0001](0001-ban-code-comments.md) | Ban code comments; record decisions as ADRs |
| [0002](0002-transcript-file-format-and-chapter-detection.md) | Transcript file format and the 2-line chapter rule |
| [0003](0003-models-hold-raw-values.md) | Models hold raw values; formatting happens at output |
| [0004](0004-one-yt-dlp-lookup-then-json3-download.md) | One yt-dlp lookup, choose a language, then download JSON3 |
| [0005](0005-english-transcript-preference.md) | Prefer creator-uploaded English over YouTube's captions |
| [0006](0006-slow-tests-use-pinned-live-videos.md) | Slow tests run against pinned live YouTube videos |

## Adding an ADR

Copy the headings of an existing ADR, take the next number, and add a row above. Keep it short: what was decided, why, and what it costs. An ADR is never edited to reverse it. Write a new one that supersedes it and set the old one's status to `Superseded by NNNN`.
