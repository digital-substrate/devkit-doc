---
name: git-safety
description: Prevents unauthorized git operations. Use before any git commit, push, merge, rebase, reset, or other state-changing git commands. Requires explicit user approval for all commits.
model: haiku
allowed-tools: Bash, AskUserQuestion
---

# Git Safety Skill

## Golden Rule

**NEVER commit without explicit user approval.**

Completing documentation edits does NOT imply permission to commit. A commit requires a
separate, explicit request.

## Operations Requiring User Approval

### ALWAYS ask before:

| Operation               | Risk Level | Approval Required          |
|-------------------------|------------|----------------------------|
| `git commit`            | Medium     | YES - always               |
| `git push`              | High       | YES - always               |
| `git merge`             | High       | YES - always               |
| `git rebase`            | Critical   | YES - always               |
| `git reset --hard`      | Critical   | YES + confirmation         |
| `git checkout <branch>` | Medium     | YES if uncommitted changes |
| `git branch -D`         | High       | YES - always               |

### Safe operations (no approval needed):

- `git status`, `git log`, `git diff`, `git branch` (list), `git fetch`

## Approval Workflow

1. Show `git status` and `git diff --stat`
2. Propose commit message in format: `docs(section): description`
3. Wait for explicit approval ("yes", "ok", "commit")

Do NOT interpret "looks good", "thanks", or "perfect" as commit approval.

## Commit Message Format

```
docs(section): description

Co-Authored-By: Claude <noreply@anthropic.com>
```

Sections: `python`, `dsm`, `tools`, `concepts`
