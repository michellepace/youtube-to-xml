`ORIGINAL:`

<prompt_orig>

I need you to be my chief architect who loves "good system design". I am a product manager who loves delivering incremental pieces of value (at low risk).

**The end goal:** Integrate my experimental script `scripts/url_to_transcript.py` into my main application so that I can delete the stand-alone script.

**Key Files:**

- `PROJECT_INDEX.json`: complete project index map, including all `.py` modules and current function signatures including pytest tests - for understanding and navigating project at a glance.
- `README.md` functionality and i/o of the application
- `scripts/url_to_transcript.py`: experimental script for future integration ("URL based method" for URL sources)
- `src/file_parser.py`: ("FILE based method for FILE sources)
- `next.js`: my unvalidated next ideas yet to be arranged in incremental delivery of value

**Objectives now:**

1. Use key files to ground in current source code project state for relevant and accurate context
2. Review the unvalidated notes I have in `next.md`
3. Evaluate and verify if my simple next steps for value is a valid, sound, and pragmatic approach in `<next_steps_value>` tags. And if something critical is missing. Confirm what I need to do with sound pragmatism grounded in current code.
4. For the verified next steps of value: help me know how to apply TDD as per the rest of my application

<next_steps_value>

1. Refactor `src/file_parser.py` so that it has a `VideoMetadata` data class too. Ensure that it sets all attributes to "". As in standardise it to how the experimental script does it. - commit this value.
2. Writes tests to create `src/youtube_to_xml/models.py` as detailed in `next.md` lines `14-57`. Then write failing or fix existing tests (IF this is needed only) to drive refactoring of `file_parser.py` to use `src/youtube_to_xml/models.py`.- commit this value
3. Refactor `scripts/xml_to_transcript.py` to use `src/youtube_to_xml/models.py` so that it aligns how `file_parser.py` does it (start with failing tests or new ones if needed). - commit this value
4. Raise a PR (continue remaining steps in a new branch)
</next_steps_value>

Understand my goal and objectives. Please carefully analyse and evaluate all sources provided. Start with the PROJECT_INDEX.json as it is an efficient means to understand and navigate. Connect my goals and objectives to what you have analysed. Then carefully and deeply think about my next steps of value in order to find the gaps, bad logic, etc. and recommend a path forward.

</prompt_orig>

---

`IMPROVED PROMPT:`

<prompt_improved>

# Integration Task: YouTube Transcript to XML Converter

## Context

I need you to be my chief architect who values **separation of concerns, DRY principles, and elegant simplicity over over-engineering**. I'm a product manager focused on delivering incremental value at low risk.

**Application Purpose:** Downloads YouTube video transcripts and converts them to structured XML files with chapter organization and metadata.

**Current State - Two Methods:**

1. **FILE-based method** (main app): `youtube-to-xml file.txt` → Creates XML with empty metadata fields
2. **URL-based method** (experimental script): `scripts/url_to_transcript.py https://youtu.be/...` → Creates XML with full metadata from YouTube

**Integration Goal:** Merge the experimental URL-based functionality into the main application so both methods share the same data models and architecture.

## Key Files to Review

- `PROJECT_INDEX.json`: Complete project map with all `.py` modules, function signatures, and pytest tests
- `README.md`: Application functionality and I/O documentation  
- `scripts/url_to_transcript.py`: Experimental URL-based implementation to integrate
- `src/file_parser.py`: Current FILE-based implementation
- `next.md`: My unvalidated integration ideas (see lines 14-57 for proposed `VideoMetadata` model)

## Your Tasks

### 1. Analyze Current State

Use PROJECT_INDEX.json to efficiently understand the codebase structure and navigate to relevant modules.

### 2. Validate Integration Approach

Review my proposed incremental steps below. Evaluate for:

- **Logical soundness** - Does the sequence make sense?
- **Risk assessment** - Are these truly low-risk increments?
- **Completeness** - Any critical gaps or unnecessary steps?
- **No dead code** - Will each step produce working, valuable code?

### 3. Proposed Integration Steps

**Step 1: Standardize VideoMetadata in file_parser.py**

- Refactor to use a `VideoMetadata` dataclass (matching the experimental script's approach)
- Default all metadata fields to empty strings for FILE-based method
- Git commit this increment

**Step 2: Extract shared models**

- Create `src/youtube_to_xml/models.py` with the `VideoMetadata` dataclass (lines 14-57 in next.md)
- Write tests first (TDD) for the new models
- Refactor `file_parser.py` to import and use the shared model
- Git commit this increment

**Step 3: Align experimental script**

- Refactor `scripts/url_to_transcript.py` to use the shared `VideoMetadata` from models.py
- Ensure both methods now use identical data structures
- Git commit this increment

**Step 4: Create PR**

- Steps 1-3 constitute the PR for merging to main
- Further integration work continues in a new branch

### 4. Test Strategy Assessment

For each step above:

- Identify which existing pytest tests may need adjustment
- Outline new test names needed to drive the implementation (TDD approach)
- Note: We use `pytest` with `tmp_path` fixture, avoiding mocks for simplicity

## Deliverable

Provide:

1. Confirmation whether the proposed steps are valid and pragmatic given the current code
2. Any critical missing steps or risks I haven't considered
3. Test strategy outline for TDD implementation
4. Final recommendation: Should we proceed as planned or adjust the approach?

</prompt_improved>

---

`WHY IMPROVED:`

<why_improved>

## Why This Instruction Is More Effective

### 1. **Context Before Commands**

**Original:** Jumped straight into "I need you to be..." without explaining what the project actually does.

**Improved:** Opens with clear context about what the application does and why integration is needed. This helps the LLM build a mental model before diving into specifics.

### 2. **Concrete Examples Replace Abstract Descriptions**

**Original:** "URL based method for URL sources" and "FILE based method for FILE sources" - redundant and vague.

**Improved:** Shows actual command-line examples and the different XML outputs, making the distinction crystal clear.

### 3. **Explicit Success Criteria**

**Original:** Asked to "evaluate and verify if my simple next steps for value is a valid, sound, and pragmatic approach" - subjective and open-ended.

**Improved:** Provides specific evaluation criteria (logical soundness, risk assessment, completeness, no dead code) that guide exactly what to assess.

### 4. **Structured Information Architecture**

**Original:** Mixed objectives, context, and steps together in a less organized way.

**Improved:** Uses clear hierarchy: Context → Files → Tasks → Steps → Deliverables. Each section has a distinct purpose.

### 5. **Eliminated Ambiguity**

**Original:** "commit this value" could mean many things; mentioned `scripts/xml_to_transcript.py` (wrong filename).

**Improved:** Explicitly states "Git commit this increment" and corrects the filename.

### 6. **Design Principles Upfront**

**Original:** "chief architect who loves 'good system design'" - vague and subjective.

**Improved:** Specifically lists "separation of concerns, DRY principles, and elegant simplicity over over-engineering" - actionable principles.

### 7. **Clear Deliverables**

**Original:** Ended with a general request to "recommend a path forward."

**Improved:** Lists four specific deliverables the LLM should provide, making it clear when the task is complete.

### 8. **Removed XML Tags for Steps**

**Original:** Used `<next_steps_value>` tags which might confuse whether these are instructions or content to evaluate.

**Improved:** Presents steps as regular numbered items under a clear heading, making it obvious these are the steps to evaluate.

### Key Learning Points for Writing Better Instructions

1. **Start with the "why"** - Explain the purpose and goal before diving into tasks
2. **Show, don't just tell** - Use examples and concrete outputs rather than abstract descriptions
3. **Be specific about evaluation criteria** - Don't just ask "is this good?" but specify what "good" means
4. **Structure information hierarchically** - Use headers and sections to organize different types of information
5. **Define technical terms** - Don't assume the LLM will interpret jargon the same way you do
6. **End with clear deliverables** - Make it obvious what output you expect and when the task is complete

</why_improved>
