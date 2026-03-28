---
description: Evaluate CodeRabbit comment and recommend whether to action it
argument-hint: <comment-url>
allowed-tools: Bash(gh api:*), Read, Glob, Grep
---

## 1. Fetch

Parse `$1` to extract owner, repo, and comment ID.

```bash
# strips analysis chain
gh api repos/OWNER/REPO/pulls/comments/COMMENT_ID \
  --jq '.body | gsub("<details>\\s*<summary>🧩 Analysis chain</summary>[\\s\\S]*?</details>\\s*"; "")' \
  > z_rabbit_comment.md
```

**Important:** Write `z_rabbit_comment.md` to the project root (current working directory), not `/tmp/`.

## 2. Evaluate

CodeRabbit AI is not always right.

Evaluate the comment `z_rabbit_comment.md` against the context of our codebase and files it references. Assess:

| Criterion | Question |
|-----------|----------|
| **Contextually valid** | Does it make sense with full codebase context? |
| **Valuable** | Worth doing? Good practice? Or is it over-engineering? |
| **Elegant** | Is the suggested fix pragmatic and clean? |

## 3. Recommend

1. **Summary**: Explain the comment (2-4 simple sentences)

2. **Verdict**: [Action | Skip | Clarify]
    - **Action** - Valid and valuable; implement (or with modifications)
    - **Skip** - Not applicable, over-engineered, or incorrect
    - **Clarify** - Need more information before deciding

3. **Reasoning**: Why this verdict (2-3 sentences)

## Output Format

Well structured, use emojis, if using tables keep width <100 chars for readability.
