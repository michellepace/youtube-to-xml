# ISSUES

## DEBUG LOGGING FOR TRANSCRIPT SELECTION

Add debug logging to show which transcript file was chosen and its priority. This would help diagnose language selection and file picking issues. CodeRabbit suggested adding:

```python
# In url_parser.py around line 171-176
transcript_file = transcript_files[0]
logger.debug(
    "Selected transcript file: %s (priority %d)",
    transcript_file.name,
    _get_youtube_transcript_file_priority(transcript_file),
)
```

## URLS
Does `test_url_parser.py`? The URL detection function should be tested in test_cli.py since it's CLI functionality, but the URL parsing itself is already well-tested in test_url_parser.py.

**Do these work / tested?**
https://www.youtube.com/watch?v=Q4gsvJvRjCU
https://www.youtube.com/live/d6dp_dwgpYQ?si=F1UAT6ks5QqRCO-g
https://youtube.com/shorts/7PaO4eBei44?si=1BUbuyiMCwiXtJOu
https://youtu.be/TTX4Q7vnV9E?si=gLCfdR_YdFE5ZGn6
https://youtu.be/Q4gsvJvRjCU?si=HXoO3rP77S6b5HG2
  

**Duplication**
- URL testing in both `test_cli.py` AND `test_url_parser.py`
- duplicate method: by the `yt-dlp` library (dependable but what about Vimeo links). Catch it early in the CLI first to ensure YouTube?

## REFACTOR TO NAMED TUPLES
"For any new function returning multiple values, use NamedTuple with descriptive field names instead of plain tuples to make the return type self-documenting and enable IDE autocomplete."

**Example:**
```python
# Instead of: -> tuple[str, int]
# Use: -> ProcessResult, where ProcessResult = NamedTuple('ProcessResult', [('content', str), ('count', int)])
```

## Assert Exceptions Thrown

What I am having difficulty with on this `test_exceptions_ytdlp.py` test is: I would like to assert the actual error that is thrown rather than asserting the actual error's message. The latter is brittle. Is there a way to do this elegantly?

Solution options:

<options>
Here's the formatted output with proper line wrapping:

**Looking at your CLI code and test, I see the issue. Currently, your CLI catches the FileInvalidFormatError internally and prints it, so the test can only assert on the printed message. To make this more robust, you have a few elegant options:**

## Option 0 (Michelle):
All default exception messages are in a constant in `exceptions.py`: why not just assert the constant and keep it simple?

## Option 1: Test the Exception Class (Recommended)

Modify your CLI to include the exception class name in the error output:

**In cli.py, line 222-224:**
```python
error = FileInvalidFormatError("Input must be a YouTube URL or .txt file")
print(f"{error.__class__.__name__}: {error}")
print("\nTry: youtube-to-xml --help")
```

Then update your test:

```python
def test_empty_url_raises_invalid_format_error(tmp_path: Path) -> None:
    """Empty URL should be rejected."""
    exit_code, output = run_script("", tmp_path)
    assert exit_code == 1
    assert "FileInvalidFormatError" in output  # Test exception class name
    assert "Try: youtube-to-xml --help" in output
```

## Option 2: Test the Exception Directly (More Elegant)

Create a separate unit test that calls the CLI logic directly:

**In tests/test_cli.py**
```python
from youtube_to_xml.cli import main
from youtube_to_xml.exceptions import FileInvalidFormatError
import pytest
import sys
from unittest.mock import patch

def test_empty_input_raises_file_invalid_format_error():
    """Test that empty input raises FileInvalidFormatError."""
    with patch('sys.argv', ['youtube-to-xml', '']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

# You could also test the exception is created correctly by mocking the error handling
```

The second option allows you to test the exception directly rather than relying on string matching, making your tests more robust and less brittle to changes in error message formatting.
</options>

## Test File Analysis (potentially stale):

**`test_exceptions.py`**:
- ✅ **Complete unit test coverage** for all 15 exceptions
- ✅ Tests exception creation, inheritance, and message handling
- ✅ Tests the `map_yt_dlp_exception()` helper function

**`test_exceptions_ytdlp.py`**:
- ❌ **No exception class testing** - only CLI integration tests
- ℹ️  Tests real YouTube API behavior, but doesn't test specific exception types

## Standardise Noisy URL exceptions like file

See potentially stale info in 
- `fix-url-exceptions.md`
- `test_file.py` and `test_url.py`

## Deal with the "PlayList" scenario
See `test_url.py`:
1. 🔴 Create dedicated issue for playlist URL handling (Make a new Exception?)
2. 🔴 Implement proper playlist rejection with clean error message
3. 🔴 Add playlist URL test coverage
4. 🔴 Update manual testing documentation