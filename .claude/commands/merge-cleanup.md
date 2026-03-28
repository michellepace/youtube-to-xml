---
allowed-tools: Bash(git checkout:*), Bash(git pull:*), Bash(git branch:*), Bash(git fetch:*), Bash(git status:*), Bash(gh:*)
description: Post-merge cleanup: switch to main, pull, delete merged branch, prune
---

## Context

- Current branch: !`git branch --show-current`
- All local branches: !`git branch`
- Remote branches: !`git branch -r`

## Task

Michelle has merged her PR and wants to clean up. Please:

1. Switch to main branch
2. Pull latest changes
3. Delete the previous branch (the one shown above that is not main)
4. Prune stale remote-tracking references: `git fetch --prune`
5. Check both Git and GitHub to ensure clean status
6. Create narrow summary table with emojis to show everything is clean

If already on main with no other branches, just confirm everything is clean.
