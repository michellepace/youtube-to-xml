# Phased Implementation Plan: Exception Handling Alignment

## Context & Assessment Summary

### Project Context
The `scripts/url_to_transcript.py` script will soon be integrated into the main YouTube-to-XML application. As a pre-step, we are improving exceptions and alignment now to smoothen future integration. Some work has already been done to smooth integration (e.g., the script uses `src/exceptions.py` already and `tests/end_to_end.py`). The script will be deleted when the integration is done.

### Current Issues Identified
1. ~~**Critical Crashes**: Invalid URLs cause unhandled yt-dlp exceptions~~ ✅ FIXED
2. ~~**Bot Protection**: "Sign in to confirm you're not a bot" errors~~ ✅ FIXED
3. **Error Boundary Mix**: Print statements mixed with business logic prevent clean integration
4. **Inconsistent Patterns**: Script error handling differs from CLI approach
5. **🚨 IMMEDIATE BUG**: URLUnknownUnmappedError not caught in main() - will crash on unmapped yt-dlp errors

### Test Results (2025-09-10)
- ~~Bot protection scenario currently not reproducible~~ ✅ FIXED: Bot protection handled via mapping
- ~~Invalid URL scenarios crash with stack traces~~ ✅ FIXED: All URL errors mapped to custom exceptions
- URLSubtitlesNotFoundError works correctly for genuine no-transcript cases
- ~~All yt-dlp exceptions (ExtractorError, DownloadError, UnsupportedError) are unhandled~~ ✅ FIXED: All mapped via map_yt_dlp_exception()
- ✅ VERIFIED: All integration tests passing including `test_url_invalid_format_error`
- ✅ VERIFIED: Comprehensive exception mapping tests in `TestYtDlpExceptionMapping` class

### Key Files
- `PROJECT_INDEX.json`: project index very useful, includes full function signatures, call relationships, directory structure - navigation and architecture analysis
- `docs/knowledge/api-yt_dlp/2.error.analysis.md`: manual testing scenarios to determine `yt-dlp` errors
- `scripts/url_to_transcript.py` - Main script needing fixes
- `src/youtube_to_xml/exceptions.py` - Custom exception hierarchy
- `tests/test_end_to_end.py` - Integration tests including `test_url_invalid_format_error`
- `tests/test_exceptions.py` - Exception unit tests

---

## Phase 1: Fix Critical Crashes - Handle yt-dlp Exceptions ✅ COMPLETE

**Goal:** Prevent unhandled crashes for invalid URLs and bot protection by catching and mapping yt-dlp exceptions

### Steps:
1. **Test Review & Planning**
   - Review `test_end_to_end.py::test_url_invalid_format_error` - ✅ NOW PASSES (no longer crashes)
   - Review `test_exceptions.py` - ✅ URLVideoUnavailableError exists and has good default message
   - Result: test_url_invalid_format_error passes with proper exception handling

2. **TDD: Add Unit Test**
   - ✅ IMPLEMENTED: `test_exceptions.py` verifies yt-dlp exception mapping 
   - ✅ IMPLEMENTED: All exception classes exist with user-friendly default messages
   - ✅ IMPLEMENTED: Semantic correctness tests for different error types

3. **Implementation**
   - ✅ IMPLEMENTED: `scripts/url_to_transcript.py::fetch_video_metadata_and_subtitles` function
   - ✅ IMPLEMENTED: extract_info() and process_info() wrapped with try/except for yt-dlp exceptions
   - ✅ IMPLEMENTED: Map specific error patterns to semantically correct custom exceptions:
     - "429" → URLRateLimitError (for HTTP rate limiting)
     - "Sign in to confirm you're not a bot" → URLBotProtectionError (specific exception)
     - "Unsupported URL" → URLNotYouTubeError (for non-YouTube URLs)
     - "Incomplete YouTube ID" → URLIncompleteError (for truncated URLs)
     - "is not a valid URL" → URLIsInvalidError (for empty URLs)
     - "[youtube] invalid-url:" → URLIsInvalidError (for malformed URLs)
     - "Video unavailable" → URLVideoUnavailableError (for unavailable videos)
     - Fallback → URLUnknownUnmappedError (for unmapped yt-dlp errors)
   - ✅ IMPLEMENTED: Use exception default messages (no custom technical messages)
   - ✅ IMPLEMENTED: `map_yt_dlp_exception()` function handles all mappings

4. **Quality Check**
   - Run: `uv run ruff check --fix && uv run ruff format`
   - Run: `uv run pytest tests/test_end_to_end.py::test_url_invalid_format_error -v`

5. 🛑 **Halt:** Assess implementation of phase 1 for completeness, elegance of approach, practical test coverage, code quality. Provide summarised report. Recommend if a git commit is justified as a standalone "chunk of value" or if additional tweaks are needed. Awaiting confirmation from Michelle.

**✅ Phase 1 Status: COMPLETED**

---

## Phase 2: ~~Add Bot Protection Detection~~ ✅ COMPLETE (Already Implemented)

**Goal:** ~~Properly handle YouTube bot protection scenarios~~ Already achieved in Phase 1

### Implementation Status:
- ✅ URLBotProtectionError exists in `src/youtube_to_xml/exceptions.py`
- ✅ Added to ALL_EXCEPTION_CLASSES in `test_exceptions.py`
- ✅ Mapping pattern "sign in to confirm you're not a bot" → URLBotProtectionError
- ✅ Exception handled in main() function
- ✅ User-friendly default message: "YouTube requires verification - try switching networks"

**✅ Phase 2 Status: COMPLETED (Was implemented as part of Phase 1)**

---

## Phase 3: Clean Error Boundaries ❌ INCOMPLETE

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
   - ✅ Review all integration tests in `test_end_to_end.py`
   - ✅ Verify main() in script handles all exception types
   - ✅ URLBotProtectionError already added to main() exception handling

2. **TDD: Coverage Verification**
   - ✅ URLBotProtectionError already in exception tuple in main()
   - ❌ **CRITICAL BUG:** URLUnknownUnmappedError is NOT imported or caught in main() - unmapped yt-dlp errors will crash the script
   - ✅ Most custom exceptions are caught

3. **Implementation**
   - ✅ URLBotProtectionError already in main() exception handling
   - ✅ Consistent exit codes (always 1 for errors) 
   - ❌ **IMMEDIATE FIX NEEDED:** Add URLUnknownUnmappedError to imports and exception tuple in main()
   - Document error handling patterns for integration

4. **Final Quality Check**
   - Run: `uv run ruff check --fix && uv run ruff format`
   - Run: `uv run pytest tests/ -v` (full test suite)
   - Verify no regressions

5. 🛑 **Halt:** Assess implementation of phase 4 for completeness, elegance of approach, practical test coverage, code quality. Evaluate if the complete exception handling system is consistent and integration-ready. Provide summarised report. Recommend if a git commit is justified as a standalone "chunk of value" or if additional tweaks are needed. Awaiting confirmation from Michelle.

---

## Phase 5: ~~User-Friendly Error Messages~~ ✅ COMPLETE

**Goal:** ~~Ensure all error messages are user-friendly~~ Already achieved - messages are clear and actionable

### Implementation Status:
- ✅ **Current messages are already user-friendly:**
  - URLIsInvalidError: "Invalid URL format"
  - URLVideoUnavailableError: "YouTube video unavailable" 
  - URLSubtitlesNotFoundError: "This video doesn't have subtitles available"
  - URLRateLimitError: "YouTube is temporarily limiting requests - try again later"
  - URLNotYouTubeError: "URL is not a YouTube video"
  - URLIncompleteError: "YouTube URL is incomplete"
  - URLBotProtectionError: "YouTube requires verification - try switching networks"
  - URLUnknownUnmappedError: "YouTube processing failed - unmapped error"

- ✅ **Code already uses exception defaults (non-brittle pattern)**:
  - Script uses `raise URLSubtitlesNotFoundError` (no custom message)
  - Exception mapping uses default messages from exception classes
  - No technical jargon or yt-dlp internals exposed to users

- ✅ **Messages are clear and actionable**:
  - All error messages provide clear guidance
  - No developer jargon present
  - Consistent user-facing language achieved

**✅ Phase 5 Status: COMPLETED (Messages already user-friendly and using non-brittle patterns)**

---

## Completed But Undocumented Work

### Exception Testing Infrastructure ✅ COMPLETE
**What was done:**
- Comprehensive test coverage in `test_exceptions.py` including `TestYtDlpExceptionMapping` class
- All exception classes included in `ALL_EXCEPTION_CLASSES` for systematic testing
- Pattern matching tests verify correct mapping of yt-dlp error messages to custom exceptions
- Integration tests verify end-to-end exception handling

### Scenario Documentation ✅ COMPLETE  
**What was done:**
- Created `scenario.results.md` with 7 documented error scenarios including:
  - Empty URL, Incomplete URL, Non-YouTube URL, Malformed URL
  - Unavailable Video, Bot Protection, No Transcript Available
- Independent verification script created and tested against raw yt-dlp API
- Verified that all mapping patterns work correctly in practice

### Code Quality Improvements ✅ COMPLETE
**What was done:**
- Pyright compatibility: Added assert for metadata None check in `fetch_video_metadata_and_subtitles()`
- Exception chaining: Uses `raise mapped_exception from e` pattern for proper error context
- Non-brittle patterns: All exceptions use default messages rather than custom ones

### Integration Test Verification ✅ COMPLETE
**What was done:**
- `test_url_invalid_format_error` now passes (previously crashed)
- All integration tests in `test_end_to_end.py` are working correctly
- Exception handling verified in real-world scenarios

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
This plan delivers incremental value:
- **Phase 1:** Fixes crashes (immediate production stability)
- **Phase 2:** Handles bot protection (improved user experience)
- **Phase 3:** Clean architecture (integration ready)
- **Phase 4:** Complete verification (production ready)
- **Phase 5:** User-friendly messages (polished user experience)

Each phase is independently valuable and committable, following TDD principles and maintaining code quality throughout.