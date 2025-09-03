---
description: Create a git commit with template
---

## Context

- Current git status: !`git status --porcelain`
- Staged changes: !`git diff --cached --stat`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Create a git commit message using this template:

**Template:**
[commit_type]: [brief main summary]

[Logical Group Name]:
- [detail about what changed and why]
- [more details as needed]

[Another Group if justified]:
- [etc.]

[1-3 concise simple sentences to explain the benefit / impact.]

**Commit Types:**
- feature: New feature for users (adds functionality)
- fix: Bug fixes (fixes broken functionality)
- docs: Documentation changes only e.g. README.md
- rules: `CLAUDE.md` and files in `.claude/`
- style: Code formatting, whitespace, semicolons (no logic changes)
- refactor: Code changes that neither fix bugs nor add features
- test: Adding or updating tests
- chore: Development workflow, workspace config, dependency updates, dev tools
- build: Build system changes, compilation process, how code gets packaged
- ci: CI/CD pipeline changes, automated workflows, deployment automation
- perf: Performance improvements

**Guidelines:**
- Group related changes logically
- Main summary should be present tense
- Line length: 90 characters maximum (summary and body)
- Content/details
   - Meaningful over exhaustive: not every detail
   - Historically useful: Ai can piece together project's evolution
   - Appropriately detailed: Significant changes get proper explanation

**Hard Rule:**
- Use British spelling always
- Don't write like you're a sales person