# Validate XML Output Consistency Across TWO YouTube Transcript Methods: File-based and URL-based

**Objective:** Verify that these three methods produce near-identical matching XML output files.

**Two Methods to Test:**
1. File-based, run: `uv run youtube-to-xml <file.txt>`
2. URL-based, run: `uv run scripts/url_to_transcript.py <YOUTUBE_URL>`

**Definition: Near Identical Match:**
1. Both methods have:
   - identical XML elements and attributes (values are "" for file-based)
   - identical `<chapters>` content excluding timestamps
3. File-based vs URL-based: timestamp deviations may occur but must be < 2 seconds.

**Test Cases:**

**Test 1: (basic case with reference)**
- Input file: `example_transcripts/how-claude-code-hooks-save-me-hours-daily.txt`
- URL equivalent: `https://www.youtube.com/watch?v=Q4gsvJvRjCU`
- Expected:
   - File-based method matches exactly: `example_transcripts/how-claude-code-hooks-save-me-hours-daily.txt.xml`
   - Url-based method matches exactly: `example_transcripts/how-claude-code-hooks-save-me-hours-daily.xml`
   - URL-based is a near identical match to file-based method

**Test 2 (file-based extensive):**
- Input: All `*.txt` files in `example_transcripts/` excluding rick-astley test file (Test 3 below)
- Expected: Produces matching `.xml` files in same directory

**Test 3 (file-based needs chapters):**
- Input file: `example_transcripts/rick-astley-never-gonna-give-you-up-official-video-4k-remaster.txt`
- URL equivalent: `https://www.youtube.com/watch?v=Qw4wCMpXcQ`
- Expected:
   1. URL method contains "0:01" and "[♪♪♪]".
   2. File-based method throws a "Wrong Format" error

**Implementation Requirements:**
- Create a comparison script that runs all applicable methods
- Use output file renaming in root to avoid conflicts e.g. Test1-file.xml, Test1-url.xml
- Compare outputs and target match files using file diffs
- Report results with clear success/failure indicators using emojis

## Output Format
- Terminal-friendly table or list format
- Clear ✅/❌ indicators for each test
- Show any differences found
- Summary of overall results
- Appendix: verification of "near match" when encounted

Execute this validation and report findings.