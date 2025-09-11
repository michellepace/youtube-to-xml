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
- [Signifiant changes and impact over minor details]
- ["Just enough detail" for collective project evolution]

[Logical Group Name n (if needed)]:
- [etc.]

[2-3 terse sentences of why / benefit / impact. Strictly wrap each line at 90 characters
for readability in any IDE]
</template>

<main_prefix>
- `feature:` New feature for users (adds functionality)
- `fix:` Bug fixes (fixes broken functionality)
- `docs:` Documentation changes only e.g. README.md
- `rules: `CLAUDE.md` and files in `.claude/`
- `style:` Code formatting, white space, semicolons (no logic changes)
- `refactor:` Code changes that neither fix bugs nor add features
- `test:` Adding or updating tests
- `chore:` Development workflow, workspace config, dependency updates, dev tools
- `build:` Build system changes, compilation process, how code gets packaged
- `ci:` CI/CD pipeline changes, automated workflows, deployment automation
- `perf:` Performance improvements
</main_prefix>

<rules>
- Wrap terse statement ≤90 characters per line
- Use British spelling
- Use factual tone, avoid hyperbolic language
- Use fitting amount of detail proportional to commit scope
</rules>

Process
1. Analyse staged changes with commands in `<commit_context>` tags
2. Apply commit template `<template>` with appropriate `<main_prefix>`
2. Adhere to rules in `<rules>` tags 