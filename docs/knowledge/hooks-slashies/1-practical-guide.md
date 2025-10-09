# 🎣 Claude Code Hooks & Slash Commands: Your Automation Superpowers

> **TL;DR**: Hooks are automatic shell scripts that run during Claude's workflow. Slash Commands are reusable prompt templates. Together, they transform Claude Code from an AI assistant into a personalized development environment.

## 🤖 What Are Hooks vs Slash Commands?

### Hooks: The Silent Watchers 👁️

Hooks are **automatic shell commands** that execute at specific points in Claude's lifecycle—think of them as event listeners for your development workflow. They run **deterministically** without Claude having to "remember" to do something.

**Key Characteristics:**

- 🔄 **Automatic execution** - No manual trigger needed
- 🎯 **Event-driven** - Responds to specific Claude actions
- 🚫 **Can block operations** - Prevent unwanted actions
- 📊 **JSON communication** - Receives structured data via stdin

### Slash Commands: The Quick-Draw Templates 📋

Slash Commands are **reusable prompt templates** stored as markdown files. They're like having a library of carefully crafted prompts you can invoke instantly with parameters.

**Key Characteristics:**

- 🏃‍♂️ **Manual execution** - You trigger them with `/command-name`
- 📝 **Template-based** - Markdown files with argument placeholders
- 🔧 **Parameterizable** - Support `$ARGUMENTS`, `$1`, `$2`, etc.
- 🌍 **Scoped** - Project-level or personal

### The Fundamental Contrast

| Aspect | Hooks 🎣 | Slash Commands ⚡ |
|--------|---------|-------------------|
| **Trigger** | Automatic (event-driven) | Manual (user-invoked) |
| **Purpose** | Process control & automation | Prompt templating & workflows |
| **Configuration** | JSON in settings files | Markdown files in directories |
| **Input** | JSON via stdin | Arguments from command line |
| **Scope** | System-wide workflow control | Project/user prompt libraries |

---

## 🎣 Four Hook Scenarios: When Automation Shines

### 1. 🔒 Security & Compliance Guardian

**Scenario**: Prevent accidental commits of secrets or modifications to protected files.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json, sys, re; data=json.load(sys.stdin); path=data.get('tool_input',{}).get('file_path',''); content=str(data.get('tool_input',{}).get('content','')); sys.exit(2) if any(p in path.lower() for p in ['.env', 'secret', 'key']) or re.search(r'(password|api.key|secret)\\s*[=:]', content, re.I) else sys.exit(0)\""
          }
        ]
      }
    ]
  }
}
```

**How it works**: This hook intercepts every file write operation, scans the file path and content for security-sensitive patterns, and blocks the operation (exit code 2) if violations are detected. Claude receives the stderr feedback and can suggest alternatives.

### 2. 🎨 Automatic Code Quality Enforcement

**Scenario**: Ensure consistent formatting and linting across all code changes.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/format-and-lint.sh"
          }
        ]
      }
    ]
  }
}
```

**How it works**: After every file modification, this hook runs a comprehensive formatting and linting script. It automatically applies fixes and reports any remaining issues back to Claude, ensuring code quality without manual intervention.

### 3. 📊 Development Activity Monitoring

**Scenario**: Track development patterns, time spent on tasks, and tool usage statistics.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/activity-tracker.py"
          }
        ]
      }
    ]
  }
}
```

**How it works**: This hook logs every tool invocation with timestamps, tool types, and context. The Python script builds a comprehensive database of development activity, enabling insights into productivity patterns and workflow optimization.

### 4. 🚨 Real-time Notification & Communication

**Scenario**: Integrate with team communication tools and notification systems.

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "curl -X POST $SLACK_WEBHOOK -H 'Content-Type: application/json' -d '{\"text\":\"Claude completed task: $(date)\"}'"
          }
        ]
      }
    ]
  }
}
```

**How it works**: When Claude finishes a task, this hook sends a notification to Slack (or other services). It can include task summaries, completion status, and next steps, keeping the team informed of AI-assisted development progress.

---

## ⚡ Four Slash Command Scenarios: When Templates Save Time

### 1. 🏗️ Architecture & Design Workflows

**Scenario**: Complex system design and architectural review processes.

```markdown
---
description: Analyze system architecture and suggest improvements
argument-hint: [component-name] [complexity-level]
allowed-tools: Read, Grep, Glob
---

# Architecture Review for $1

## Analysis Scope
- **Component**: $1
- **Complexity Level**: $2
- **Current Architecture**: @docs/architecture/

## Your Task
Analyze the architecture of component "$1" considering:
1. Design patterns and SOLID principles
2. Performance implications at $2 complexity
3. Scalability bottlenecks
4. Integration points and dependencies

Provide specific, actionable recommendations with code examples.
```

**How it works**: `/arch-review authentication high` instantly loads relevant architecture docs, sets analysis parameters, and guides Claude through a structured architectural review process with specific complexity considerations.

### 2. 🐛 Debugging & Troubleshooting Workflows

**Scenario**: Systematic debugging with context gathering and solution tracking.

```markdown
---
description: Debug issue with comprehensive context gathering
argument-hint: [issue-description]
allowed-tools: Read, Grep, Bash(grep:*), Bash(find:*), Bash(ps:*), Bash(netstat:*)
---

# Debug Session: $ARGUMENTS

## Environment Context
- **System Info**: !`uname -a && python --version`
- **Process Status**: !`ps aux | grep python | head -10`
- **Network Status**: !`netstat -an | grep LISTEN | head -5`
- **Recent Logs**: !`tail -50 /var/log/app.log 2>/dev/null || echo "No app logs"`

## Issue Analysis
**Problem Statement**: $ARGUMENTS

## Systematic Debugging Approach
1. **Reproduce** the issue with minimal test case
2. **Isolate** the root cause through binary search debugging
3. **Verify** the fix doesn't introduce regressions
4. **Document** the solution for future reference

Focus on:
- Stack traces and error patterns
- Environment-specific configurations
- Recent changes that might have caused the issue
```

**How it works**: `/debug api-timeout-on-large-requests` automatically gathers system context, recent logs, and process information, then guides Claude through a methodical debugging approach with specific focus on the reported issue.

### 3. 📈 Performance Analysis & Optimization

**Scenario**: Comprehensive performance profiling and optimization recommendations.

```markdown
---
description: Analyze performance bottlenecks and suggest optimizations
argument-hint: [target-function] [performance-goal]
allowed-tools: Read, Bash(pytest:*), Bash(python:*), Bash(uv run:*)
---

# Performance Optimization: $1

## Current Performance Baseline
- **Target Function**: $1
- **Performance Goal**: $2
- **Current Tests**: !`uv run pytest -k "test_$1" --durations=10`
- **Profile Data**: !`uv run python -m cProfile -s cumtime src/your_module.py | head -20`

## Analysis Focus
Analyze the performance characteristics of `$1` with goal of $2:

### Code Analysis
Review @src/your_module.py focusing on:
1. **Algorithmic complexity** - Big O analysis
2. **Memory usage patterns** - Object creation/destruction
3. **I/O operations** - Database queries, file operations, network calls
4. **Concurrency opportunities** - Parallelization potential

### Optimization Strategy
Provide specific, measurable optimizations:
- Before/after performance estimates
- Memory usage improvements
- Code examples with explanations
- Risk assessment for each change
```

**How it works**: `/perf-analyze process_video_data "sub-2-second-response"` runs performance profiling, analyzes the target function, and provides structured optimization recommendations with specific performance targets.

### 4. 🔄 Release & Deployment Management

**Scenario**: Structured release preparation with comprehensive checking.

```markdown
---
description: Prepare release with comprehensive pre-deployment checks
argument-hint: [version] [environment]
allowed-tools: Bash(git:*), Bash(uv run:*), Read, Write
---

# Release Preparation: v$1 → $2

## Pre-Release Validation
- **Version**: $1
- **Target Environment**: $2
- **Current Branch**: !`git branch --show-current`
- **Uncommitted Changes**: !`git status --porcelain`
- **Test Status**: !`uv run pytest -x --tb=short`
- **Lint Status**: !`uv run ruff check`

## Release Checklist
### Code Quality
- [ ] All tests passing
- [ ] No linting errors
- [ ] Version numbers updated
- [ ] CHANGELOG.md updated

### Documentation
- [ ] API documentation current
- [ ] README.md reflects changes
- [ ] Migration guides (if needed)

### Deployment Readiness  
- [ ] Environment-specific configs verified
- [ ] Database migrations tested
- [ ] Rollback plan documented

## Your Task
1. **Validate** all checklist items above
2. **Generate** release notes from recent commits
3. **Prepare** deployment commands for $2 environment
4. **Document** any manual steps required

Focus on potential issues specific to $2 environment deployment.
```

**How it works**: `/release 2.1.0 production` executes a comprehensive pre-release checklist, runs all quality checks, and provides environment-specific deployment guidance with automated verification steps.

---

## 🤝 Hooks + Slash Commands: The Power Combo

**Yes, they can absolutely be used together!** This combination creates incredibly sophisticated workflows where manual triggers (slash commands) initiate processes that are then managed and validated by automatic systems (hooks).

### Example: Intelligent Release Pipeline

```markdown
# .claude/commands/deploy.md
---
description: Deploy with automatic validation and rollback protection
argument-hint: [environment] [version]
allowed-tools: Bash(git:*), Bash(docker:*), Bash(kubectl:*)
---

# Deployment: $2 → $1

## Pre-Deployment Context
- **Environment**: $1
- **Version**: $2
- **Current Status**: !`kubectl get deployments -n $1`

Deploy version $2 to $1 environment with full validation.
```

**Combined with Hook:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$TOOL_INPUT\" | jq -r '.command' | grep -q 'kubectl apply'; then python3 ~/.claude/hooks/deployment-validator.py; fi"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$TOOL_INPUT\" | jq -r '.command' | grep -q 'kubectl apply'; then python3 ~/.claude/hooks/deployment-monitor.py; fi"
          }
        ]
      }
    ]
  }
}
```

**How this combo works**:

1. **User runs** `/deploy production v2.1.0`
2. **Slash command** gathers context and prepares deployment
3. **PreToolUse hook** validates deployment safety before any kubectl commands
4. **PostToolUse hook** monitors deployment health and can trigger rollback
5. **Result**: Fully automated, safe deployment with human oversight only when needed

This creates a **fail-safe deployment pipeline** where the slash command provides the workflow template and hooks provide the safety net.

---

## 🎯 How This Project Could Benefit

Looking at your YouTube-to-XML converter project, here are specific opportunities beyond the existing `/commit` command:

### 1. 📺 YouTube Content Analysis Command

```bash
# .claude/commands/analyze-video.md
```

```markdown
---
description: Analyze YouTube video for content patterns and extraction quality
argument-hint: [youtube-url] [analysis-type]
allowed-tools: Bash(yt-dlp:*), Bash(uv run:*), Read, Write
---

# Video Content Analysis: $1

## Video Context
- **URL**: $1
- **Analysis Type**: $2
- **Video Info**: !`yt-dlp --dump-json "$1" | jq '{title, duration, upload_date, view_count}'`

Analyze this YouTube video for $2 focusing on:
- Content structure and segmentation
- Transcript quality and accuracy  
- XML output optimization opportunities
- Performance characteristics for this content type
```

### 2. 🧪 Testing & Quality Hooks

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/auto-test.sh"
          }
        ]
      }
    ]
  }
}
```

**Create** `.claude/hooks/auto-test.sh`:

```bash
#!/bin/bash
# Auto-test modified files
if echo "$1" | jq -r '.tool_input.file_path' | grep -E '\\.(py)$'; then
    file_path=$(echo "$1" | jq -r '.tool_input.file_path')
    echo "🧪 Running tests for modified file: $file_path"
    uv run pytest "tests/test_$(basename "$file_path")" -v 2>/dev/null || echo "ℹ️ No specific tests found, running related test suite"
fi
```

### 3. 📊 Performance Monitoring Command

```markdown
---
description: Profile video processing performance and identify bottlenecks
argument-hint: [test-video-url] [profile-type]
allowed-tools: Bash(uv run:*), Read, Write
---

# Performance Profile: $2 Analysis

## Test Configuration
- **Video URL**: $1
- **Profile Type**: $2
- **Current Performance**: !`uv run python -m cProfile -s cumtime -m youtube_to_xml "$1" 2>&1 | head -20`

Run comprehensive performance analysis focusing on $2 bottlenecks.
```

### 4. 🔍 XML Validation Hook

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$1\" | jq -r '.tool_input.file_path' | grep -q '\\.xml$'; then xmllint --noout \"$(echo \"$1\" | jq -r '.tool_input.file_path')\" && echo '✅ XML is valid' || echo '❌ XML validation failed' >&2; fi"
          }
        ]
      }
    ]
  }
}
```

### 5. 🚀 Integration Testing Command

```markdown
---  
description: Run full integration tests with real YouTube URLs
argument-hint: [test-suite-name]
allowed-tools: Bash(uv run:*), Read
---

# Integration Test Suite: $1

## Test Configuration
- **Suite**: $1
- **Environment**: !`python --version && uv --version`
- **Test URLs**: @tests/integration/test_urls.txt

## Execution
Run integration tests for $1 with real YouTube content:
1. Process various content types (music, talks, tutorials)
2. Validate XML output structure and content
3. Check performance thresholds
4. Verify error handling for edge cases

Focus on real-world scenarios and production-like conditions.
```

## 🎉 The Bottom Line

**Hooks and Slash Commands transform Claude Code from a helpful AI into a personalized development environment**:

- **Hooks** = Your automation layer (the silent guardians)
- **Slash Commands** = Your workflow templates (the quick-draw tools)  
- **Together** = A development environment that adapts to your patterns and enforces your standards

They're not just features—they're **force multipliers** that turn repetitive tasks into automated workflows and complex procedures into simple commands. Your future self will thank you for the time invested in setting these up! 🚀

---

*Created with Claude Code - where AI meets automation* ✨
