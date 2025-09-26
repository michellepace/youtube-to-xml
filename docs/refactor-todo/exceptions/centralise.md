# 🧠 **UNVALIDATED THOUGHTS: Exception Testing Architecture & Strategy**

## 🎯 **Problem Statement**

**Issue**: Exception messages are hardcoded across 14 exception classes and 184 test assertions spanning 9 test files, creating brittle code that's difficult to maintain when updating user-facing error messages.

**Goal**: Centralise exception messages in `exceptions.py` using a `MESSAGES` constant, enabling single-source-of-truth message management while maintaining existing functionality and test coverage.


## 📊 **Current Exception Testing Landscape**

**Exception Sources & Responsibilities**:
```
src/youtube_to_xml/exceptions.py → 14 custom exception classes with default messages (1 base + 13 specific)
tests/test_exceptions.py       → Unit tests: inheritance, default messages, yt-dlp mapping
tests/test_cli.py              → CLI-level: file processing errors + input validation
tests/test_exceptions_url.py   → Slow tests: URL processing errors hitting yt-dlp API
tests/test_end_to_end.py       → E2E: Success scenarios + format validation
tests/test_file_parser.py      → Unit: File parsing logic exceptions
```

**Current Message Hardcoding Problem**:
- 📍 **Exception classes**: Default messages in `__init__` methods (14 classes)
- 📍 **CLI formatting**: `"❌ {e}"` and `"Try: youtube-to-xml --help"` in cli.py
- 📍 **Duplication**: CLI error formatting pattern tested in `test_cli.py`, ❌ symbol appears in assertions across multiple files
- 📍 **Test assertions**: Hardcoded expected messages across 9 test files (184 total string assertions):
  - `test_xml_builder.py`: 48 assertions (XML structure validation)
  - `test_time_utils.py`: 40 assertions (timestamp formatting)
  - `test_file_parser.py`: 28 assertions (file parsing validation)
  - `test_end_to_end.py`: 16 assertions (E2E workflow validation)
  - `test_url_parser.py`: 16 assertions (URL parsing validation)
  - `test_models.py`: 14 assertions (data structure validation)
  - `test_cli.py`: 11 assertions (CLI behavior & error messages)
  - `test_exceptions_url.py`: 8 assertions (URL error scenarios)
  - `test_exceptions.py`: 3 assertions (exception inheritance)


## 🚀 **Implementation Plan**

### **Step 1: Centralise Exception Messages**
Add `MESSAGES` constant to `src/youtube_to_xml/exceptions.py` containing all exception messages. Update all exception classes to reference `MESSAGES["key"]` instead of hardcoded defaults.

**Key design decisions**:
- **Message keys**: Use snake_case matching exception class names (e.g., `URLIsInvalidError` → `"url_is_invalid_error"`)
- **Pure messages only**: No CLI formatting (❌, help hints) in exception messages - keep exceptions framework-agnostic for potential API usage
- **Scope**: Replace hardcoded exception messages with constants

### **Step 2: Update Tests to Use Message Constants**
Update test assertions across 9 test files to import and reference `MESSAGES["key"]` instead of hardcoded strings. Focus on exception message assertions only - leave XML/timestamp validation strings unchanged.

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