# Phased Implementation Plan: Exception Handling Alignment

## Context & Assessment Summary

### Project Context
The `scripts/url_to_transcript.py` script will soon be integrated into the main YouTube-to-XML application. As a pre-step, we are improving exceptions and alignment now to smoothen future integration. Some work has already been done to smooth integration (e.g., the script uses `src/exceptions.py` already and `tests/end_to_end.py`). The script will be deleted when the integration is done.

### Current Issues Identified
1. **Critical Crashes**: Invalid URLs cause unhandled yt-dlp exceptions (ExtractorError, DownloadError)
2. **Bot Protection**: "Sign in to confirm you're not a bot" errors need proper handling
3. **Error Boundary Mix**: Print statements mixed with business logic prevent clean integration
4. **Inconsistent Patterns**: Script error handling differs from CLI approach

### Test Results (2025-09-09)
- Bot protection scenario currently not reproducible but documented as intermittent
- Invalid URL scenarios crash with stack traces instead of proper error messages
- URLSubtitlesNotFoundError works correctly for genuine no-transcript cases
- All yt-dlp exceptions (ExtractorError, DownloadError, UnsupportedError) are unhandled

### Key Files
- `PROJECT_INDEX.json`: project index very useful, includes full function signatures, call relationships, directory structure - navigation and architecture analysis
- `docs/knowledge/api-yt_dlp/2-error-explore.md`: manual testing scenarios to determine `yt-dlp` errors
- `scripts/url_to_transcript.py` - Main script needing fixes
- `src/youtube_to_xml/exceptions.py` - Custom exception hierarchy
- `tests/test_end_to_end.py` - Integration tests (line 202: test_url_invalid_format_error)
- `tests/test_exceptions.py` - Exception unit tests

---

## Phase 1: Fix Critical Crashes - Handle yt-dlp Exceptions (Including Bot Protection) ✅ COMPLETE

**Goal:** Prevent unhandled crashes for invalid URLs and bot protection by catching and mapping yt-dlp exceptions

### Steps:
1. **Test Review & Planning**
   - Review `test_end_to_end.py::test_url_invalid_format_error` (line 202) - currently expects error handling but gets crashes
   - Review `test_exceptions.py` - confirm URLVideoNotFoundError exists and has good default message
   - Identify: test_url_invalid_format_error will start passing once we handle yt-dlp exceptions

2. **TDD: Add Unit Test**
   - Add test to verify yt-dlp exception mapping to specific exception types
   - Test that new exception classes exist and have user-friendly default messages
   - Test semantic correctness: different error types map to different exceptions

3. **Implementation**
   - In `scripts/url_to_transcript.py::fetch_video_metadata_and_subtitles` (lines 143-159)
   - Wrap extract_info() with try/except for yt-dlp exceptions
   - Map specific error patterns to semantically correct custom exceptions:
     - "Sign in to confirm you're not a bot" → URLBotProtectionError (specific exception)
     - "Unsupported URL" → URLNotYouTubeError (for non-YouTube URLs)
     - "Incomplete YouTube ID" → URLIncompleteError (for truncated URLs)
     - "is not a valid URL" → URLIsInvalidError (for empty URLs)
     - "[youtube] invalid-url:" → URLIsInvalidError (for malformed URLs)
     - "Video unavailable" → URLVideoUnavailableError (for unavailable videos)
   - Use exception default messages (no custom technical messages)
   - Note: HTTP 429 detection remains in process_info() for genuine rate limiting

4. **Quality Check**
   - Run: `uv run ruff check --fix && uv run ruff format`
   - Run: `uv run pytest tests/test_end_to_end.py::test_url_invalid_format_error -v`

5. 🛑 **Halt:** Assess implementation of phase 1 for completeness, elegance of approach, practical test coverage, code quality. Provide summarised report. Recommend if a git commit is justified as a standalone "chunk of value" or if additional tweaks are needed. Awaiting confirmation from Michelle.

**✅ Phase 1 Status: COMPLETED**

---

## Phase 2: Add Bot Protection Detection

**Goal:** Properly handle YouTube bot protection scenarios when they occur

### Steps:
1. **Test Review & Planning**
   - Review `test_exceptions.py` - need to add URLBotProtectionError to ALL_EXCEPTION_CLASSES
   - Review `test_end_to_end.py` - no specific bot protection test (can't reproduce reliably)
   - Identify: Need new exception class and tests for it

2. **TDD: Exception & Tests**
   - Add URLBotProtectionError to `src/youtube_to_xml/exceptions.py`
   - Update `test_exceptions.py` to include URLBotProtectionError in ALL_EXCEPTION_CLASSES
   - Add specific test for bot protection error message preservation

3. **Implementation**
   - Add URLBotProtectionError class after URLRateLimitError
   - In `scripts/url_to_transcript.py::fetch_video_metadata_and_subtitles`
   - Check for "Sign in to confirm you're not a bot" in error messages
   - Raise URLBotProtectionError with helpful message about switching networks

4. **Quality Check**
   - Run: `uv run ruff check --fix && uv run ruff format`
   - Run: `uv run pytest tests/test_exceptions.py -v`

5. 🛑 **Halt:** Assess implementation of phase 2 for completeness, elegance of approach, practical test coverage, code quality. Evaluate if bot protection detection is robust and user-friendly. Provide summarised report. Recommend if a git commit is justified as a standalone "chunk of value" or if additional tweaks are needed. Awaiting confirmation from Michelle.

---

## Phase 3: Clean Error Boundaries

**Goal:** Move error presentation out of business logic to application boundary

### Steps:
1. **Test Review & Planning**
   - Review `test_end_to_end.py` - tests check stdout/stderr for error messages
   - Identify: Moving prints won't break tests if exceptions still raised properly

2. **TDD: Refactor Safety**
   - No new tests needed - existing tests verify error messages appear
   - Tests will confirm refactoring doesn't break functionality

3. **Implementation**
   - Remove print statements from `fetch_video_metadata_and_subtitles` (line 174)
   - Remove print statements from `convert_youtube_to_xml` 
   - Ensure all error presentation happens in `main()` function
   - Keep logging statements for debugging

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
   - Check URLBotProtectionError added to main() exception handling

2. **TDD: Coverage Verification**
   - Add URLBotProtectionError to exception tuple in main() (lines 464-468)
   - Verify all custom exceptions are caught

3. **Implementation**
   - Update main() exception handling to include URLBotProtectionError
   - Ensure consistent exit codes (always 1 for errors)
   - Document error handling patterns for integration

4. **Final Quality Check**
   - Run: `uv run ruff check --fix && uv run ruff format`
   - Run: `uv run pytest tests/ -v` (full test suite)
   - Verify no regressions

5. 🛑 **Halt:** Assess implementation of phase 4 for completeness, elegance of approach, practical test coverage, code quality. Evaluate if the complete exception handling system is consistent and integration-ready. Provide summarised report. Recommend if a git commit is justified as a standalone "chunk of value" or if additional tweaks are needed. Awaiting confirmation from Michelle.

---

## Phase 5: User-Friendly Error Messages

**Goal:** Ensure all error messages are user-friendly and actionable, eliminating technical jargon while making code less brittle through consistent use of exception defaults

### Steps:
1. **Test Review & Planning**
   - Review current error message outputs from all scenarios (Phase 1 testing results)
   - Identify messages containing technical yt-dlp internals or developer jargon
   - Audit all `raise Exception("custom message")` calls throughout codebase for brittle patterns
   - Review `test_end_to_end.py` - tests may expect specific error message patterns
   - Identify: Tests checking error message content will need updates

2. **TDD: Message Content Tests**
   - Update exception default messages in `src/youtube_to_xml/exceptions.py` to be user-friendly
   - Add tests validating new default messages are preserved
   - Update integration tests to expect new user-friendly error patterns
   - Test that all scenarios produce clear, actionable guidance

3. **Implementation**
   - Update exception default messages to be user-friendly:
     - URLVideoNotFoundError: "Invalid YouTube URL or video not available (tbc)"
     - URLSubtitlesNotFoundError: "This video doesn't have subtitles available (tbc)"
     - URLRateLimitError: "YouTube is temporarily limiting requests - try again later (tbc)"
     - URLBotProtectionError: "YouTube requires verification - try switching networks (tbc)"
   - **Make code less brittle**: Replace hard-coded error messages with exception defaults throughout codebase
     - Change `raise URLVideoNotFoundError("custom message")` to `raise URLVideoNotFoundError()`
     - Change `raise URLSubtitlesNotFoundError("custom message")` to `raise URLSubtitlesNotFoundError()`
     - Only keep custom messages when they add specific contextual value (e.g., bot protection guidance)
   - Centralize all message content in exception class definitions
   - Ensure consistent user-facing language across all error scenarios

4. **Quality Check**
   - Run: `uv run ruff check --fix && uv run ruff format`
   - Run: `uv run pytest tests/ -v` (verify updated message expectations)
   - Test all error scenarios manually to validate user-friendly output
   - Verify no technical jargon appears in user-facing messages
   - Confirm code is less brittle with centralized message management

5. 🛑 **Halt:** Assess implementation of phase 5 for completeness, elegance of approach, practical test coverage, code quality. Evaluate if all error messages provide clear, actionable guidance without technical jargon. Assess if the codebase is less brittle through consistent use of exception defaults. Provide summarised report. Recommend if a git commit is justified as a standalone "chunk of value" or if additional tweaks are needed. Awaiting confirmation from Michelle.

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

### Critical Files & Lines
- `scripts/url_to_transcript.py:137-141` - extract_info() exception handling
- `scripts/url_to_transcript.py:464-468` - main() exception catching
- `scripts/url_to_transcript.py:174` - print statement in business logic
- `src/youtube_to_xml/exceptions.py:58+` - add URLBotProtectionError
- `tests/test_exceptions.py:15-23` - ALL_EXCEPTION_CLASSES list

## Summary
This plan delivers incremental value:
- **Phase 1:** Fixes crashes (immediate production stability)
- **Phase 2:** Handles bot protection (improved user experience)
- **Phase 3:** Clean architecture (integration ready)
- **Phase 4:** Complete verification (production ready)
- **Phase 5:** User-friendly messages (polished user experience)

Each phase is independently valuable and committable, following TDD principles and maintaining code quality throughout.