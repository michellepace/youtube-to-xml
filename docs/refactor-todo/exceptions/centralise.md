# 🧠 **Centralising Exception Messages: Current State Analysis & High Level Steps**

## 🎯 **Problem Statement**

**Issue**: Exception messages are hardcoded across 14 exception classes and 184 test assertions spanning 9 test files, creating brittle code that's difficult to maintain when updating user-facing error messages.

**Goal**: Centralise exception messages in `exceptions.py` using a `MESSAGES` constant, enabling single-source-of-truth message management while maintaining existing functionality and test coverage.


## 📊 **Current Exception Testing Landscape**

**Current Message Hardcoding Problem**:
- 📍 **Exception classes**: Default messages in `__init__` methods (14 classes)
- 📍 **CLI formatting**: `"❌ {e}"` and `"Try: youtube-to-xml --help"` in cli.py
- 📍 **Hardcoded default exception messages (excluding `exceptions.py`)**:
   - Across 1 file in `src/`
   - Across 5 files in `tests/`

**All Occurrences of Hardcoded Exception Messages**

Summary Table:

| File | Exception Type | Exception Message | Lines |
|---|---|---|---|
| **SRC DIRECTORY** | | | |
| src/url_parser.py | URLNotYouTubeError | URL is not a YouTube video | 317 |
| **TESTS DIRECTORY** | | | |
| tests/test_cli.py | FileEmptyError | Your file is empty | [155, 163] |
| tests/test_cli.py | FileInvalidFormatError | Wrong format in transcript file | 175 |
| tests/test_cli.py | FileNotExistsError | We couldn't find your file | 151 |
| tests/test_cli.py | InvalidInputError | Input must be a YouTube URL or .txt file | [111, 125, 137] |
| tests/test_end_to_end.py | FileInvalidFormatError | Wrong format in transcript file | 135 |
| tests/test_exceptions.py | BaseTranscriptError | Custom error message | 48 |
| tests/test_exceptions.py | BaseTranscriptError | Test message | 54 |
| tests/test_exceptions_url.py | URLIncompleteError | YouTube URL is incomplete | 55 |
| tests/test_exceptions_url.py | URLIsInvalidError | Invalid URL format | 65 |
| tests/test_exceptions_url.py | URLNotYouTubeError | URL is not a YouTube video | 38 |
| tests/test_exceptions_url.py | URLTranscriptNotFoundError | This video doesn't have a transcript available | 95 |
| tests/test_exceptions_url.py | URLVideoUnavailableError | YouTube video unavailable | 74 |
| tests/test_file_parser.py | FileInvalidFormatError | Wrong format in transcript file | [351, 352] |

**CLI Formatting Patterns (in cli.py)**:
- `"❌ {e}"` formatting on lines 198, 204
- `"Try: youtube-to-xml --help"` help hints on lines 177, 199, 205


## 🚀 **High-Level Steps**

### **Step 1: Centralise Exception Messages**
Add `EXCEPTION_MESSAGES` constant to `src/youtube_to_xml/exceptions.py` containing all exception messages. Update all exception classes to reference `EXCEPTION_MESSAGES["key"]` instead of hardcoded defaults.

**Key design decisions**:
- **Message keys**: Use snake_case matching exception class names (e.g., `URLIsInvalidError` → `"url_is_invalid_error"`)
- **Pure messages only**: No CLI formatting (❌, help hints) in exception messages - keep exceptions framework-agnostic for potential API usage
- **Scope**: Replace hardcoded exception messages with constants

### **Step 2: Update Tests to Use Message Constants**
Update test assertions across 9 test files to import and reference `EXCEPTION_MESSAGES["key"]` instead of hardcoded strings. Focus on exception message assertions only - leave XML/timestamp validation strings unchanged.

### **Benefits**
- **Single source of truth**: Change messages in one place
- **Maintainable**: Update user-facing messages without breaking tests
- **Simple**: No architectural changes, just centralised constants
- **Testing clarity**: CLI tests focus on user experience (message content), unit tests focus on business logic (exception types)

**Why This Approach?**: This approach preserves test architecture separation - CLI tests verify what users see via message constants, while unit tests verify internal behaviour via exception types. No need to assert exception types in CLI tests as that would break the subprocess-based testing pattern and mix concerns.

---

## 🔬 **Future Investigation: 

### **Exception Granularity**

**Problem**: Some exceptions may be handling multiple distinct scenarios, potentially creating confusing user experiences where different underlying issues show the same error message.

**Examples of potential concerns**:
- `URLIsInvalidError` used for both malformed URLs and non-existent videos
- `URLUnmappedError` combining network failures, private videos, and unknown errors

**What to investigate**:
- Review exception pattern matching logic for overlapping or incorrect mappings
- Assess whether current exception types provide sufficient granularity for different error scenarios
- Evaluate if new exception types are needed for better user experience differentiation

**Approach**: Complete message centralisation first, then analyse actual usage patterns in production to determine if exception refinement is needed.

### **Exception or Error?**

**Problem**: Codebase uses `Error` suffix (FileEmptyError) in `exceptions.py` file. Question whether to standardise on `Exception` suffix for filename consistency or keep `Error` for stdlib pattern matching.