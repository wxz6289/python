# Git hooks

## commit-msg

Removes `Co-authored-by: Cursor <cursoragent@cursor.com>` from commit messages before they are recorded.

Install (from repository root):

```bash
cp scripts/git-hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```
