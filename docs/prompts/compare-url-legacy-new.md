**Task: Validate XML Output Consistency Across Three YouTube Transcript Methods**

**Objective:** Verify that these three methods produce near-identical matching XML output files.

**Three Methods to Test:**
1. File-based new: `uv run youtube-to-xml <file.txt>`
2. File-based legacy: `uv run youtube-to-xml --legacy <file.txt>`
3. URL-based: `uv run scripts/url_to_transcript.xml`

**Definition: Near Identical Match:**
1. File-based methods always match eachother exactly
2. All methods have
   - identical XML elements and attributes (vales are "" for file-based)
   - identical `<chapter>` content excluding timestamps
3. File-based vs URL-based: timestamp deviations may occure but always <2 seconds

**Test Cases:**

**Test 1: (basic case with reference)**
- Input file: `example_transcripts/how-claude-code-hooks-save-me-hours-daily.txt`
- URL equivalent: `https://www.youtube.com/watch?v=Q4gsvJvRjCU`
- Expected:
   - File-based methods match: `example_transcripts/how-claude-code-hooks-save-me-hours-daily.txt.xml`
   - URL-based is a near identical match 

**Test 2 (file-based extensive):**
- Input: All `*.txt` files in `example_transcripts/` excluding rick-astley test file (Test 3 below)
- Expected: Both methods produce matching `.xml` files in same directory

**Test 3 (file-based needs chapters):**
- Input file: `example_transcripts/rick-astley-never-gonna-give-you-up-official-video-4k-remaster.txt`
- URL equivalent: `https://www.youtube.com/watch?v=Qw4wCMpXcQ`
- Expected:
   1. URL method contains "0:01" and "[♪♪♪]".
   2. File-based methods throw the same "Wrong Format" error

**Implementation Requirements:**
- Create a comparison script that runs all applicable methods
- Use output file renaming in root to avoid conflicts e.g. Test1-new.xml, Test1-leg.xml, test1-url.xml
- Compare outputs using file diffs
- Report results with clear success/failure indicators using emojis

**Output Format:**
- Terminal-friendly table or list format
- Clear ✅/❌ indicators for each test
- Show any differences found
- Summary of overall results
- Appendix: verification of "near match" when encounted

Execute this validation and report findings.