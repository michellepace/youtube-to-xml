# Phased Implementation Plan: Exception Handling Alignment

## Context & Assessment Summary

### Project Context
The `scripts/url_to_transcript.py` script will soon be integrated into the main YouTube-to-XML application. As a pre-step, we are improving exceptions and alignment now to smoothen future integration. Some work has already been done to smooth integration (e.g., the script uses `src/exceptions.py` has test coverage in `tests/` modules). The script will be deleted when the integration is done. The main application is a CLI now, but there are future aspirations for it to be an API service too for a Next.js app on Vercel.

### Current Issues Identified
1. **Error Boundary Mix**: Print statements mixed with business logic prevent clean integration
2. **Inconsistent Patterns**: Script error handling differs from CLI approach
3. **🚨 IMMEDIATE BUG**: URLUnknownUnmappedError not caught in main() - will crash on unmapped yt-dlp errors

### Key Files
- `PROJECT_INDEX.json`: project index very useful, includes full function signatures, call relationships, directory structure - navigation and architecture analysis
- `scripts/url_to_transcript.py` - Main script needing fixes
- `src/youtube_to_xml/exceptions.py` - Custom exception hierarchy and mapping
- `tests/test_exceptions.py` - Exception unit tests
- `tests/test_exceptions_ytdlp.py` - Integration for script `yt-dlp` specfic

---

## Phase 1: Clean Error Boundaries ❌ INCOMPLETE

**Goal:** Move error presentation out of business logic to application boundary

**Current Status:** Multiple print statements still exist in `convert_youtube_to_xml()` function mixing progress messages with business logic.

### Steps:
1. **Test Review & Planning**
   - Review `test_end_to_end.py` - tests check stdout/stderr for error messages
   - Identify: Moving prints won't break tests if exceptions still raised properly

2. **TDD: Refactor Safety**
   - No new tests needed - existing tests verify error messages appear
   - Tests will confirm refactoring doesn't break functionality

3. **Implementation**
   - ❌ TODO: Remove print statements from `convert_youtube_to_xml()` function (progress messages like "🎬 Processing:", "📊 Fetching video metadata...", "📝 Downloaded X subtitles")
   - ❌ TODO: Move progress/status messages to `main()` function
   - ❌ TODO: Ensure all error presentation happens in `main()` function
   - ✅ Keep logging statements for debugging

4. **Quality Check**
   - Run: `uv run ruff check --fix && uv run ruff format`
   - Run: `uv run pytest tests/test_end_to_end.py::test_url_no_subtitles_error -v`
   - Run: `uv run pytest tests/test_end_to_end.py -m integration -v`

5. 🛑 **Halt:** Assess implementation of phase 3 for completeness, elegance of approach, practical test coverage, code quality. Evaluate if error boundary separation is clean and maintains all functionality. Provide summarised report. Recommend if a git commit is justified as a standalone "chunk of value" or if additional tweaks are needed. Awaiting confirmation from Michelle.

---

## Phase 4: Integration Readiness Verification

**Goal:** Ensure complete consistency and test coverage for integration

### Steps:
1. **Test Review & Planning**
   - Review all integration tests in `test_end_to_end.py`
   - Verify main() in script handles all exception types
   - URLBotProtectionError already added to main() exception handling

2. **TDD: Coverage Verification**
   - URLBotProtectionError already in exception tuple in main()
   - **CRITICAL BUG:** URLUnknownUnmappedError is NOT imported or caught in main() - unmapped yt-dlp errors will crash the script
   - Most custom exceptions are caught

3. **Implementation**
   - URLBotProtectionError already in main() exception handling
   - Consistent exit codes (always 1 for errors) 
   - **IMMEDIATE FIX NEEDED:** Add URLUnknownUnmappedError to imports and exception tuple in main()
   - Document error handling patterns for integration

4. **Final Quality Check**
   - Run: `uv run ruff check --fix && uv run ruff format`
   - Run: `uv run pytest tests/ -v` (full test suite)
   - Verify no regressions

5. 🛑 **Halt:** Assess implementation of phase 4 for completeness, elegance of approach, practical test coverage, code quality. Evaluate if the complete exception handling system is consistent and integration-ready. Provide summarised report. Recommend if a git commit is justified as a standalone "chunk of value" or if additional tweaks are needed. Awaiting confirmation from Michelle.

---

## TDD Quality Standards for Each Phase

### Before Implementation
- Always run: `uv run ruff check --fix && uv run ruff format`
- Review existing tests for potential conflicts
- Identify which tests will change behavior

### Test-Driven Process
1. Update/add tests first
2. Run tests (should fail initially)
3. Implement minimal solution
4. Run tests (should pass)
5. Refactor for elegance

### Critical Files & Functions
- `scripts/url_to_transcript.py::fetch_video_metadata_and_subtitles()` - yt-dlp exception handling
- `scripts/url_to_transcript.py::main()` - exception catching and user messages
- `scripts/url_to_transcript.py::convert_youtube_to_xml()` - print statements to move
- `src/youtube_to_xml/exceptions.py` - custom exception hierarchy
- `tests/test_exceptions.py` - exception test coverage

## Summary

Each phase is independently valuable and committable, following TDD principles and maintaining code quality throughout.