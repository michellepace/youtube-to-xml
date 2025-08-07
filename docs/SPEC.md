# 🎯 SPEC — YouTube Transcript to XML Converter

**A UV Packaged Application with CLI entry point** that converts YouTube transcript text files into structured XML format with chapter elements.

## User Context

**Problem**: Raw YouTube transcripts are difficult for LLMs to parse effectively due to lack of structure degrading AI Chat responses.

**Solution**: Convert transcripts to XML with chapter elements for improved AI comprehension.

**Primary Users**: 
- Students following 5 hours+ YouTube tutorials
- Researchers analysing video content

## Project Architecture

**UV Project Type**: UV Packaged Application (created with `uv init --package youtube-to-xml`)

**Key Features of Packaged Structure**:
- Professional Structure: `src/` layout with proper module organisation
- Build System: `[build-system]` for distribution in `pyproject.toml`
- Entry Point: `[project.scripts]` configuration in `pyproject.toml`
- Usage: `youtube-to-xml transcript.txt` and `youtube-to-xml --help`

**Entry Point Flow**: CLI command `youtube-to-xml` → `convert_transcript()` in `main.py` → `parse_transcript()` from `parser.py` → `generate_xml()` from `xml_generator.py`

## Design Principles

**TDD-Driven Design**: Write tests first - this naturally creates:
- Pure, testable functions (no side effects in business logic)
- Clear module boundaries (easier to mock dependencies)
- Single responsibility (complex functions are hard to test)

**Key Guidelines**:
- Separate layers: CLI → business logic → I/O
- Pure functions preferred: Core logic functions should be easy to test without setup
- Handle errors at boundaries: Catch exceptions in CLI layer, not business logic
- One module, one purpose: Each `.py` file has a clear role
- Type hints required: All function signatures need type annotations
- Descriptive naming: Functions/variables should clearly indicate purpose

**TDD Guidelines `pytest`**
- Use pytest's `tmp_path` fixture to avoid creating test files
- Avoid mocks as they introduce unnecessary complexity

## Python Tech Stack

**Language:** Python 3.13+ (as pinned in `.python-version`)

**Approach:** Test-Driven Development (TDD)

**Required Libraries:**
- `argparse` (command-line arguments and `--help`)
- `pathlib` (file operations)
- `re` (regex pattern matching)
- `xml.etree.ElementTree` (XML parsing/validation)
- `pytest` (test driven development)
- `subprocess` and `shutil` (CLI integration testing)

## Example: Raw Transcript → XML Format

Valid raw YouTube transcript files start with one line of text (not a timestamp) and have one or more chapters as shown in `<transcript_raw>` tags. For this `<transcript_raw>` example, the required XML output is shown in `<transcript_processed>`.

<transcript_raw>
Introduction
0:00
Welcome to today's session
2:28
Let's dive into the topic
15:45
First point about methodology
23:30
Second point here
Getting Started Guide  
1:15:30
Download the software
2:45:12
Configure it , erm, how "you" like it
Advanced Features & Tips
10:15:30
Final thoughts on implementation
</transcript_raw>

<transcript_processed>
```xml
<transcript>
  <chapters>
    <chapter name="Introduction" start="0:00">
      0:00
      Welcome to today's session
      2:28
      Let's dive into the topic
      15:45
      First point about methodology
      23:30
      Second point here
    </chapter>
    <chapter name="Getting Started Guide" start="1:15:30">
      1:15:30
      Download the software
      2:45:12
      Configure it , erm, how &quot;you&quot; like it
    </chapter>
    <chapter name="Advanced Features &amp; Tips" start="10:15:30">
      10:15:30
      Final thoughts on implementation
    </chapter>
  </chapters>
</transcript>
```
</transcript_processed>

## Detection Rules

- **Timestamp Pattern**: Lines containing only timestamp formats (M:SS, MM:SS, H:MM:SS, or HH:MM:SS)
- **First Chapter**: First line of text file
- **Subsequent Chapters**: When exactly 2 lines exist between consecutive timestamps, the second line (non-timestamp) is a chapter name
- **Reference Implementation (parsing)**: Use timestamp and chapter detection logic from `scripts/transcript_reporter.py` (functions: `find_timestamps()`, `find_chapters()`, `TIMESTAMP_PATTERN`). Also consider `read_file()` for file I/O. Adapt the proven parsing patterns for transcript content extraction.


## XML Generation Rules and Required Template

- **Use ElementTree API**: Build XML with `ET.Element()`, `ET.SubElement()`, `.set()` for attributes, assign content with `.text`, and format with `ET.indent()`
- **XML Serialisation**: Use `ET.ElementTree(root).write(filename, encoding="utf-8", xml_declaration=True)` for automatic XML declaration and proper encoding
- **Parse Requirement**: Must parse successfully using `xml.etree.ElementTree.parse()`
- **Template Compliance**: Must exactly follow XML template shown between `<xml_template>` tags

<xml_template>
```xml
<transcript>
  <chapters>
    <chapter name="Chapter name 1" start="[start timestamp]">
      Content first chapter... (timestamps AND non-timestamp lines with proper indentation)
    </chapter>
    <chapter name="Chapter name 2" start="[start timestamp]">
      Content second chapter... (timestamps AND non-timestamp lines with proper indentation)
    </chapter>

    <!-- Additional chapters as needed -->
  </chapters>
</transcript>
```
</xml_template>

## File I/O Requirements

- **Execution**: CLI command `youtube-to-xml filename.txt`
- **Input**: Text file containing YouTube transcript in the specified format
- **Output**: XML file matches input files name and is saved to `transcript_files/` directory (create if it does not exist). Example: `filename99.txt` → `transcript_files/filename99.xml`
- **Argparse `--help`**: the help message in between `<argparse_help>` tags is shown

<argparse_help>

usage: youtube-to-xml [-h] transcript.txt

Convert YouTube transcripts to XML format with chapter detection

positional arguments:
  transcript.txt  YouTube transcript text file to convert

options:
  -h, --help      show this help message and exit

✅ Example YouTube Transcript

📋 EXPECTED FORMAT:
   ┌─────────────────────────────────────────
   │ Introduction to Bret Taylor
   │ 00:04
   │ You're CTO of Meta and and co-CEO of...
   └─────────────────────────────────────────

🔧 REQUIREMENTS:
   - Must start with a chapter name (non-timestamp line)
   - Second line must be a timestamp
   - Third line must be content (non-timestamp line)

💡 Check that your transcript follows this basic pattern

</argparse_help>

## Error Handling & Validation

**File System Errors**
- File not found: `f"❌ We couldn't find your file: {filename}"`
- Permission denied: `f"❌ We don't have permission to access: {filename}"`

**Content Validation Errors**
- Empty file: `f"❌ Your file is empty: {filename}"`
- Invalid transcript format: `f"❌ Wrong format in '{filename}' - run 'youtube-to-xml --help'"`

- **Input Validation**: 
  - File must start with non-timestamp line (chapter name)
  - Must contain at least one timestamp
  - Must have detectable chapter structure per detection rules

## Success Criteria

- [ ] Produces exact XML output format matching the provided template `<xml_template>`
- [ ] Correctly identifies chapter names vs content including all edge cases
- [ ] Generates valid XML that parses successfully with `xml.etree.ElementTree.parse()`
- [ ] Validates input files and provides clear error messages for invalid formats
- [ ] Test driven development used resulting in coverage and good design (avoid mocks)
- [ ] Clean project structure following Python best practices
- [ ] Performance handles transcripts up to 15,000 lines in less than 2 seconds

---

## Key References

**Python Documentation**
- ElementTree XML API: https://docs.python.org/3/library/xml.etree.elementtree.html
- Pytest `tmp_path` fixture: https://docs.pytest.org/en/stable/how-to/tmp_path.html

**UV Package Manager**
- UV Workflows and Rules: `.cursor.rules/uv-workflows.mdc`
- Project Layout: https://docs.astral.sh/uv/concepts/projects/layout/
- Packaged Applications: https://docs.astral.sh/uv/concepts/projects/packaging/
