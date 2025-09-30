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


## REFACTOR TO NAMED TUPLES
"For any new function returning multiple values, use NamedTuple with descriptive field names instead of plain tuples to make the return type self-documenting and enable IDE autocomplete."

**Example:**
```python
# Instead of: -> tuple[str, int]
# Use: -> ProcessResult, where ProcessResult = NamedTuple('ProcessResult', [('content', str), ('count', int)])
```