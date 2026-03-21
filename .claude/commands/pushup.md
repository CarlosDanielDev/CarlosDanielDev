# Pushup - Ship It

Finalize the current issue: semantic commit, push, create PR, link issue, and complete all tasks.

## Arguments

`$ARGUMENTS` — (optional) The GitHub issue number (e.g., `#42` or `42`). If not provided, detect it from the current branch name.

## Instructions

Execute all steps below **sequentially**. Do NOT skip any step. If any step fails, STOP and report the error.

### Step 1: Detect the Issue

1. If `$ARGUMENTS` is provided, use it as the issue number (strip `#` if present)
2. If not provided, extract the issue number from the current branch name (e.g., `feat/42-some-feature` → `42`, `fix/issue-15` → `15`)
3. If no issue number can be detected, ask the user

### Step 2: Gather Context

Run these in parallel:
- `git status` — check for uncommitted changes
- `git diff` and `git diff --staged` — see all changes
- `git log --oneline -10` — recent commit style reference
- `gh issue view <number>` — get issue title, body, and task list

### Step 3: Semantic Commit

1. Analyze ALL changes (staged + unstaged)
2. Stage relevant files (`git add` — be specific, never use `-A` or `.` blindly)
3. Determine the semantic commit type from the changes:
   - `feat:` — new feature
   - `fix:` — bug fix
   - `refactor:` — code restructuring
   - `test:` — adding/updating tests
   - `docs:` — documentation only
   - `style:` — formatting, no logic change
   - `chore:` — maintenance, dependencies
   - `perf:` — performance improvement
4. Write a concise commit message (1-2 sentences) focusing on the **why**
5. Include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
6. Create the commit using HEREDOC format
7. Verify with `git status` after commit

**If there are NO changes to commit, skip to Step 4.**

### Step 4: Push

1. Check if the branch tracks a remote: `git rev-parse --abbrev-ref --symbolic-full-name @{u}`
2. Push with `-u` flag if needed: `git push -u origin <branch>` or just `git push`

### Step 5: Create Pull Request

1. Check if a PR already exists for this branch: `gh pr view --json number,url 2>/dev/null`
2. **If PR already exists**, skip to Step 6
3. If no PR exists, create one:

```bash
gh pr create --title "<semantic type>: <concise description>" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points describing what was done>

## Issue
Closes #<issue-number>

## Test plan
<Bulleted checklist of how to verify the changes>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

**Important:**
- The PR title MUST be under 70 characters
- The body MUST include `Closes #<issue-number>` to auto-link and auto-close the issue
- Use the same semantic type prefix as the commit

### Step 6: Complete Tasks in the Issue

1. Fetch the issue body: `gh issue view <number> --json body -q .body`
2. Find all task list items (`- [ ]` checkboxes)
3. Replace all `- [ ]` with `- [x]` in the issue body
4. Update the issue: `gh issue edit <number> --body "<updated body>"`

### Step 7: Complete Tasks in the PR

1. Fetch the PR body: `gh pr view --json body -q .body`
2. Find all task list items (`- [ ]` checkboxes) in the test plan
3. Replace all `- [ ]` with `- [x]` in the PR body
4. Update the PR: `gh pr edit <number> --body "<updated body>"`

### Step 8: Final Report

Output a summary:

```
---
Pushup complete!

  Commit:  <commit hash> <commit message>
  Branch:  <branch name>
  PR:      <PR URL>
  Issue:   #<number> (tasks completed)
---
```

## Error Handling

- **No changes + no existing PR**: Warn the user — nothing to push up
- **PR already exists**: Reuse it, push new commits, update task lists
- **Merge conflicts**: STOP and report — do not force push
- **Hook failures**: Fix the issue and retry with a NEW commit (never amend)
- **gh CLI not authenticated**: Tell the user to run `gh auth login`
