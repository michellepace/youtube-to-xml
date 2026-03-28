# Refactor: inline timestamps on same line as text - ✅ Done

## What

Change the XML output format so that each transcript line is prefixed with its timestamp on the **same line**, instead of the current format where timestamps and text alternate on separate lines.

### Current format (separate lines)

```xml
<chapter title="Intro" start_time="0:00">
  0:00
  Hooks are hands down one of the best
  0:02
  features in Claude Code and for some
  0:03
  reason a lot of people don't know about
</chapter>
```

### Target format (inline timestamps)

```xml
<chapter title="Intro" start_time="0:00">
  0:00 Hooks are hands down one of the best
  0:02 features in Claude Code and for some
  0:03 reason a lot of people don't know about
</chapter>
```

Each line becomes: `{timestamp} {text}` — one line per transcript segment. No blank lines between entries. Indentation within chapters stays the same.

## Why

The primary consumer of these transcripts is an LLM agent (Claude Code) that navigates large files using `grep` and line-range reads. When timestamps and text share a line, every `grep` hit is a self-contained record — the agent gets the timestamp and content in one tool call, with no follow-up read or off-by-one risk. See the Mermaid diagram in the README appendix for a visual explanation.

Token count impact is negligible (~3% reduction from fewer newlines).

## Scope

This change affects **output formatting only**. The data model (`TranscriptDoc`, chapters, metadata) and the parsing logic (URL parser, file parser) should not need structural changes. The change is in how transcript lines are serialised into XML text content — most likely in `xml_builder.py`.

### Modules likely affected

- `xml_builder.py` — where chapter content is written into XML elements
- Any helper that joins timestamp + text into the chapter body string

### Modules likely unaffected

- `url_parser.py` — extracts raw data from YouTube, returns structured objects
- `file_parser.py` — parses input `.txt` files into structured objects
- `models.py` — data classes shouldn't change
- `cli.py` — no format logic here

Verify this assumption by reading the code before making changes.

## How to implement

1. Read `CLAUDE.md`, `xml_builder.py`, and `models.py` to understand how chapter content is currently assembled.
2. Identify where the alternating `timestamp\ntext` pattern is produced.
3. Change it to produce `timestamp text` on a single line.
4. The `<chapter>` element attributes (`title`, `start_time`) are unchanged.
5. The `<transcript>` element attributes (`video_title`, `video_published`, `video_duration`, `video_url`) are unchanged.

## Verification

### 1. TDD — write/update tests first

- Write a test that asserts the new inline format before changing production code.
- The test should verify that within a chapter's text content, each non-empty line matches the pattern `^\s*\d+:\d{2}\s+.+` (timestamp followed by space followed by text, on one line).
- The test should verify there are **no** lines that contain only a bare timestamp (i.e. `^\s*\d+:\d{2}\s*$` should match nothing).

### 2. Existing tests must pass

Run the full test suite before and after:

```bash
uv run pytest -m "not slow"
```

All 105 unit tests must pass. Update test fixtures/expected outputs that assert the old format — they now need to assert the new format. Do not delete tests; update their expectations.

### 3. Slow tests (if internet available)

```bash
uv run pytest -m "slow"
```

These hit YouTube. If any assert specific output formatting, update them too.

### 4. Linting and formatting

```bash
uv run ruff check --fix
uv run ruff format
```

Zero errors.

### 5. Manual verification with a real URL

Run the CLI against a real video and inspect the output:

```bash
youtube-to-xml https://youtu.be/Q4gsvJvRjCU
```

Open the output XML and confirm:

- Every transcript line has its timestamp and text on the same line.
- No bare timestamp lines exist.
- Chapter `title` and `start_time` attributes are correct.
- Video metadata attributes are correct.
- The file is valid XML (`python -c "import xml.etree.ElementTree as ET; ET.parse('output.xml')"` should not raise).

### 6. Manual verification with a file input

Create a test `.txt` file in YouTube copy-paste format and run:

```bash
youtube-to-xml test_input.txt
```

Confirm the same inline timestamp format in the output.

## Assumptions

- The repo uses the terminology defined in `docs/terminology.md` — a "transcript line" is one timestamp + text pair.
- The data model already stores timestamp and text as associated pairs. The change is purely at the serialisation layer.
- If the data model stores them separately and the pairing happens during XML writing, the pairing logic itself doesn't need to change — only how the paired result is formatted as a string.
