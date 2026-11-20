# Issues to file

GitHub Issues is turned off for this repository, so the comment audit ([ADR 0001](../adr/0001-ban-code-comments.md)) left its issues here as drafts. Each one tracks a workaround that an "excuse" comment used to hide.

Once Issues is turned on, file each draft (the first line is the title) and delete the file:

```bash
for f in docs/issues/0*.md; do
  gh issue create --title "$(head -1 "$f" | sed 's/^# //')" --body "$(tail -n +3 "$f")"
done
```

Code links point at commit `31a8828`, the last commit that still had the comments.

| Draft | Area |
|---|---|
| [01](01-file-parser-drops-text-lines.md) | `file_parser`: text lines silently dropped |
| [02](02-console-log-handler-leaks-tracebacks.md) | `logging_config`: tracebacks shown to users |
| [03](03-read-transcript-path-from-yt-dlp.md) | `url_parser`: transcript path guessed from yt-dlp's naming scheme |
| [04](04-yt-dlp-none-guards.md) | `url_parser`: unreachable `None` guards hidden by `type: ignore` |
| [05](05-argparse-systemexit-interception.md) | `cli`: `SystemExit` caught to rewrite the exit code |
| [06](06-slow-test-rate-limit-skip-never-matches.md) | tests: rate-limit skip never matches |
