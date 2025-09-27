---
description: Create a git commit with template
---

Create a useful and representative commit message:

<commit_context>
- Branch context: `git branch --show-current`
- Files changed: `git diff --cached --name-status`
- Change volume: `git diff --cached --stat`
- Detailed changes: `git diff --cached`
</commit_context>

<template>
[main_prefix]: [brief main summary in imperative mood]

[Logical Group Name 1]:
- [Significant changes and impact over minor details]
- ["Just enough detail" for collective project evolution]

[Logical Group Name n (if needed)]:
- [etc.]

[2-3 terse sentences of why / benefit / impact. Wrap at 90 characters]
</template>

<main_prefix>
- `rules:` Claude configuration e.g. `**/CLAUDE.md`, `.claude/**/*`
- `test:` Adding or updating tests e.g. `tests/**/*`
- `ci:` CI/CD pipeline changes, automated workflows, deployment automation
- `build:` Build system changes, compilation process, how code gets packaged
- `perf:` Performance improvements
- `fix:` Bug fixes (fixes broken functionality)
- `refactor:` Code changes that neither fix bugs nor add features
- `style:` Code formatting, visual consistency, linting fixes; no functional change
- `chore:` Dev workflow, workspace config, dependency updates, dev tools e.g. `.vscode/**/*`, `pyproject.toml`, `.gitignore`
- `docs:` Documentation changes only e.g. `README.md`, `docs/**/*.md`
- `feature:` New feature for users (adds functionality)
</main_prefix>

<rules>
- Use British spelling
- Use factual tone, avoid hyperbolic language
- Avoid marketing adjectives (comprehensive, complete, enhanced, improved, etc.)
- Use fitting amount of detail proportional to commit scope
- Wrap the terse sentences so that no line exceeds 90 characters
</rules>

Process
1. Analyse staged changes with commands in `<commit_context>` tags
2. Apply commit template `<template>` with appropriate `<main_prefix>`
3. Adhere to rules in `<rules>` tags 