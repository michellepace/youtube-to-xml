---
description: Create a git commit with template
---

## Context

**CRITICAL:** The commit message must relate ONLY to cached / staged changes. 

- Branch context: `git branch --show-current`
- Files changed: `git diff --cached --name-status`
- Change volume: `git diff --cached --stat`
- Detailed changes: `git diff --cached`

## Your task

Create a git commit message using this template:

**Template:**
[commit_type]: [brief main summary]

[Logical Group Name]:
- [detail about what changed and why]
- [more details as needed]

[Another Group if justified]:
- [etc.]

[Terse statement of benefit/impact: 2-3 sentences, wrap lines ≤90 characters]

**Commit Types:**
- feature: New feature for users (adds functionality)
- fix: Bug fixes (fixes broken functionality)
- docs: Documentation changes only e.g. README.md
- rules: `CLAUDE.md` and files in `.claude/`
- style: Code formatting, white space, semicolons (no logic changes)
- refactor: Code changes that neither fix bugs nor add features
- test: Adding or updating tests
- chore: Development workflow, workspace config, dependency updates, dev tools
- build: Build system changes, compilation process, how code gets packaged
- ci: CI/CD pipeline changes, automated workflows, deployment automation
- perf: Performance improvements

**Guidelines:**
- Group related changes logically
- Main summary should use imperative mood
- Content details
   - Focus on meaningful changes over exhaustive details
   - Provide context that helps understand the project's evolution
   - Give proper explanation for significant changes

**Strict Rules:**
- Wrap terse statement ≤90 characters
- Use British spelling
- Use factual tone, avoid hyperbolic language