# Claude Code Project Index: Complete Analysis 🔍

Hooks and slashes explained in application to this repo and my project here: https://github.com/ericbuess/claude-code-project-index/tree/main

## Your Current Hooks & Slash Commands 📋

### Hooks in `~/.claude/settings.json`

| Hook Event | Command | Purpose | Related to Index? |
|------------|---------|---------|-------------------|
| **UserPromptSubmit** | `i_flag_hook.py` | Detects `-i` and `-ic` flags in prompts, generates/updates PROJECT_INDEX.json | ✅ |
| **Stop** | `stop_hook.py` | Refreshes PROJECT_INDEX.json after each session to capture changes | ✅ |
| **PreToolUse** (Read) | `claude-docs-helper.sh hook-check` | Checks and syncs Claude Code documentation | ❌ |

### Slash Commands in `~/.claude/commands/`

| Command | Purpose | Related to Index? |
|---------|---------|-------------------|
| **/docs** | Access Claude Code documentation mirror (community maintained by Eric Buess) | ❌ |
| **/index** | Manually create or update PROJECT_INDEX.json for current project | ✅ |

## Installation Directory Structure 🏗️

**Location**: `~/.claude-code-project-index/`

### Core Scripts Explained

#### 1. **`project_index.py`** - The Brain 🧠
Main indexer that scans your codebase and generates PROJECT_INDEX.json. It extracts function signatures, class definitions, call graphs, documentation structure, and directory purposes. Supports full parsing for Python, JavaScript/TypeScript, and shell scripts, while tracking other language files by location only.

#### 2. **`i_flag_hook.py`** - The Flag Detector 🚩
UserPromptSubmit hook that detects `-i[number]` or `-ic[number]` flags in your prompts. When found, it triggers project_index.py to generate an index with the specified token size (default 50k), then either adds it to Claude's context or exports to clipboard for external AI tools.

#### 3. **`stop_hook.py`** - The Maintainer 🔄
Stop hook that runs after every Claude Code session ends. If it finds a PROJECT_INDEX.json in your project, it automatically regenerates it to capture any code changes made during the session, ensuring the index stays current without manual intervention.

#### 4. **`index_utils.py`** - The Library 📚
Shared utilities module containing language parsers, directory recognition patterns, and common functions. Defines what to ignore (node_modules, .git, etc.), which languages can be fully parsed, and provides extraction functions for different file types.

#### 5. **`find_python.sh`** - The Python Hunter 🔍
Sophisticated bash script that searches for the newest Python 3.8+ installation on your system. Checks virtual environments, common paths, Homebrew locations, and versioned commands to find the best available Python interpreter for running the indexer.

#### 6. **`run_python.sh`** - The Executor ⚡
Simple wrapper script that reads the saved Python command from installation and executes Python scripts with it. Acts as a consistent interface for running Python code regardless of where Python is installed on the system.

## How Project Index Works: ASCII Flow Diagram 🎨

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     PROJECT INDEX WORKFLOW                          │
└─────────────────────────────────────────────────────────────────────┘

SCENARIO 1: Using -i flag
═════════════════════════

User Input: "refactor the auth system -i75"
    │
    ▼
┌──────────────────────┐
│ UserPromptSubmit Hook│ ◄─── Detects "-i75" flag
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│   i_flag_hook.py     │ ◄─── Parses flag, extracts size (75k)
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│  project_index.py    │ ◄─── Generates PROJECT_INDEX.json
└──────────────────────┘      (max 75k tokens)
    │
    ▼
┌──────────────────────┐
│ PROJECT_INDEX.json   │ ◄─── Saved to project root
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│  Claude's Context    │ ◄─── Index added as additional context
└──────────────────────┘
    │
    ▼
Claude processes prompt with full architectural awareness!


SCENARIO 2: Manual index generation
════════════════════════════════════

User Input: "/index"
    │
    ▼
┌──────────────────────┐
│  index.md command    │ ◄─── Slash command triggered
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│  project_index.py    │ ◄─── Runs with default settings
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ PROJECT_INDEX.json   │ ◄─── Created/updated in project root
└──────────────────────┘


SCENARIO 3: Automatic maintenance
══════════════════════════════════

Claude session ends
    │
    ▼
┌──────────────────────┐
│    Stop Hook         │ ◄─── Triggered on session end
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│   stop_hook.py       │ ◄─── Checks for PROJECT_INDEX.json
└──────────────────────┘
    │
    ├─── [No index found] → Exit
    │
    └─── [Index exists]
            │
            ▼
    ┌──────────────────────┐
    │  project_index.py    │ ◄─── Regenerates index
    └──────────────────────┘
            │
            ▼
    ┌──────────────────────┐
    │ PROJECT_INDEX.json   │ ◄─── Updated with latest changes
    └──────────────────────┘


SCENARIO 4: Clipboard export for external AI
═════════════════════════════════════════════

User Input: "analyze architecture -ic200"
    │
    ▼
┌──────────────────────┐
│ UserPromptSubmit Hook│ ◄─── Detects "-ic200" flag
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│   i_flag_hook.py     │ ◄─── Clipboard mode, 200k tokens
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│  project_index.py    │ ◄─── Generates expanded index
└──────────────────────┘
    │
    ├─── Save to PROJECT_INDEX.json
    │
    └─── Copy to clipboard
            │
            ▼
    ┌──────────────────────┐
    │   System Clipboard   │ ◄─── Ready for external AI
    └──────────────────────┘
            │
            ▼
    Use with Gemini, ChatGPT, or other large-context AI
```

## Testing Your Project Index: Three Commands 🧪

### 1. **Manual Index Generation**
```bash
/index
```
**Expected**: Creates PROJECT_INDEX.json with ~17 code files, ~39 documentation files, directory tree, and Python function signatures.

### 2. **Index-Aware Mode Test**
```bash
explain the xml builder architecture -i
```
**Expected**: Claude will have full awareness of your xml_builder.py module, understanding all classes (TranscriptProcessor, XMLBuilder, Chapter) and their relationships.

### 3. **Clipboard Export Test**
```bash
generate architecture diagram -ic100
```
**Expected**: 
- PROJECT_INDEX.json created/updated
- Index copied to clipboard (check with `pbpaste` on macOS or `xclip -o` on Linux)
- Message about clipboard content being ready

## Verification Checklist ✅

After running the commands above, verify:

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Index exists | `ls -la PROJECT_INDEX.json` | File present in project root |
| Index size | `wc -c PROJECT_INDEX.json` | ~6-10KB for your small project |
| Contains functions | `grep '"f":' PROJECT_INDEX.json \| head -3` | Shows Python function signatures |
| Has directory tree | `grep '"tree":' PROJECT_INDEX.json` | Directory structure present |
| Metadata present | `grep '"last_interactive_size_k"' PROJECT_INDEX.json` | Remembers your -i size preference |

## Your Architectural Change: Is Project Index Useful? 🤔

Looking at your planned refactoring in `docs/plans/05-try-auto-again/2-explore_a_P.md`:

### **For This Specific Task: Limited Benefit** ⚠️

Your project is **very small** (17 Python files), and the architectural change involves:
- Creating adapter pattern for file vs YouTube sources
- Unifying data flow through standardized interfaces
- Refactoring existing modules

**Why limited benefit**:
1. 📏 **Small codebase** - Claude can easily hold your entire project in context
2. 🎯 **Focused refactoring** - You're working on specific modules, not navigating unknown code
3. 📝 **Well-documented plan** - Your architectural points are already clear

### **Where Project Index WOULD Help** ✨

Even in your small project, the index provides value for:

1. **Function dependency tracking** 🔗
   - Shows which functions call `parse_transcript()` or `build_xml()`
   - Helps ensure refactoring doesn't break hidden dependencies

2. **Avoiding duplication** 🚫
   - Prevents Claude from recreating existing utility functions
   - Shows all existing error classes (URLRateLimitError, etc.)

3. **Consistent file placement** 📁
   - Ensures new adapter classes go in the right module
   - Maintains your project's organizational patterns

4. **Quick navigation** 🗺️
   - Claude instantly knows where XMLBuilder, TranscriptProcessor live
   - No need to search for specific implementations

### **Recommendation for Your Task** 💡

```bash
# Use direct reference for this small refactoring
@PROJECT_INDEX.json help me implement the adapter pattern for the unified main application per the plan in @docs/plans/05-try-auto-again/2-explore_a_P.md
```

This gives Claude:
- Complete awareness of existing code structure
- All function signatures to avoid duplication
- Directory organization for proper file placement

**Bottom line**: While not essential for your small project, PROJECT_INDEX provides helpful guardrails to ensure clean, consistent refactoring that respects your existing architecture. Think of it as "architectural insurance" - probably won't need it, but nice to have! 🛡️

## Summary 🎯

The PROJECT_INDEX tool transforms Claude Code from architecturally blind to spatially aware through:
- 🤖 **Two hooks** that automate index generation and maintenance
- ⚡ **One slash command** for manual control
- 🧠 **Six scripts** working together to analyze and index your codebase
- 🔄 **Three modes**: Direct reference, subagent analysis, clipboard export

For your youtube-to-xml project, it's like having architectural X-ray vision - probably overkill for routine work, but invaluable when you need to ensure refactoring respects existing patterns and dependencies! 🚀