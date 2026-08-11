# Co-Author Attribution & Execution Ladder in git-agent

`git-agent` automatically handles model co-author attribution and commit generation.

## 1. Automatic Model Resolution

`git-agent` automatically inspects environment variables (`PI_MODEL`, `CLAUDE_CODE_MODEL`, `CODEX_MODEL`, `MODEL`) to infer the active model identity and attach standard `Co-Authored-By` trailers.

Manual `--co-author` flags may still be passed to override or append specific co-authors:
```bash
git-agent commit --intent "<intent>" --co-author "<co-author>"
```

To suppress co-author trailers entirely:
```bash
git-agent commit --no-attribution
```

---

## 2. Binary Unavailable

If `git-agent` binary is unavailable or fails due to network/auth issues:

1. **Auth / Gateway Retry**: Retry with `--free`:
   ```bash
   git-agent commit --free --intent "<intent>"
   ```
2. If `--free` also fails, report the error and ask the user to install git-agent or run git commands manually.
