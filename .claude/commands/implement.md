# Implement Issue

Fetch a GitHub issue and implement it using the orchestrator workflow.

## Arguments

`$ARGUMENTS` — The GitHub issue number (e.g., `#42` or `42`) followed by optional flags.

### Flags

Flags bypass the mandatory startup questions:

**Language flags (bypass language selection):**
| Flag | Short | Language |
|------|-------|----------|
| `--english` | `-e` | English |
| `--portuguese` | `-pt` | Portugues do Brasil |
| `--spanish` | `-s` | Espanol |

**Mode flags (bypass mode selection):**
| Flag | Short | Mode |
|------|-------|------|
| `--orchestrator` | `-o` | Subagents Orchestrator |
| `--vibe-coding` | `-vc` | Vibe Coding |

### Examples

```
/implement #42                     # Ask both questions
/implement 42 -e -o                # English + Orchestrator
/implement #15 --portuguese -vc    # Portuguese + Vibe Coding
/implement 7 -pt -o               # Portuguese + Orchestrator
/implement #3 -e                   # English + ask mode
/implement 10 -o                   # Orchestrator + ask language
```

## Instructions

### Step 1: Parse Arguments

1. Extract the issue number from `$ARGUMENTS` (strip `#` if present)
2. Parse flags from `$ARGUMENTS`:
   - Language: `--english`/`-e`, `--portuguese`/`-pt`, `--spanish`/`-s`
   - Mode: `--orchestrator`/`-o`, `--vibe-coding`/`-vc`
3. If no issue number is found, ask the user for it

### Step 2: Language Selection

- If a language flag was provided, use it (skip the question)
- If NO language flag, ask the user using AskUserQuestion:
  ```
  "What is your preferred language for this conversation?"
  - Portugues do Brasil
  - English
  - Espanol
  - Other
  ```

### Step 3: Mode Selection

- If a mode flag was provided, use it (skip the question)
- If NO mode flag, ask the user using AskUserQuestion:
  ```
  "What mode do you want to work in?"

  Vibe Coding (Simple)
  - You work directly without calling analysis subagents
  - Faster for small tasks
  - WARNING: May overflow context window on complex tasks

  Subagents Orchestrator (Complex)
  - Full orchestrated workflow with specialized subagents
  - Mandatory flow: Architect -> Execution -> Security -> QA -> Documentation
  - Recommended for production-quality code
  ```

**Note:** Training Mode is NOT available for `/implement` since it modifies project code.

### Step 4: Fetch Issue Context

Run these commands to gather issue details:

```bash
gh issue view <number>
gh issue view <number> --json title,body,labels,assignees,milestone
```

Read the issue carefully. Extract:
- **Title**: What needs to be done
- **Description**: Detailed requirements
- **Labels**: May indicate type (bug, feature, enhancement)
- **Task list**: Checkboxes with specific deliverables

### Step 5: Create Feature Branch

1. Check current branch: `git branch --show-current`
2. If NOT already on a feature branch for this issue:
   - Determine branch prefix from issue labels/title:
     - `feat/` for features and enhancements
     - `fix/` for bugs
     - `refactor/` for refactoring
     - `chore/` for maintenance
   - Create and switch to branch: `git checkout -b <prefix>/<issue-number>-<short-description>`
3. If already on a relevant branch, stay on it

### Step 6: Execute Based on Mode

**Follow the selected mode's workflow as defined in CLAUDE.md:**

#### If Vibe Coding:
1. Warn about context window limitations
2. Analyze the issue requirements yourself
3. Follow TDD: RED -> GREEN -> REFACTOR
4. Call `subagent-docs-analyst` at the end

#### If Subagents Orchestrator:
1. Delegate to the appropriate architect(s) with the full issue context
2. Receive blueprint
3. Follow TDD: RED -> GREEN -> REFACTOR
4. Delegate to `subagent-security-analyst`
5. Delegate to appropriate QA subagent
6. Call `subagent-docs-analyst` at the end

### Step 7: Summary

After implementation is complete, output:

```
---
Implementation complete!

  Issue:    #<number> - <title>
  Branch:   <branch name>
  Mode:     <mode used>
  Status:   Ready for /pushup
---
```

Remind the user they can run `/pushup #<number>` to commit, push, create PR, and close the issue.

## Error Handling

- **Issue not found**: Tell user the issue number is invalid
- **gh CLI not authenticated**: Tell user to run `gh auth login`
- **Issue is closed**: Warn user and ask if they want to proceed anyway
- **No issue number provided**: Ask the user for it
- **Invalid flags**: Ignore unknown flags and proceed, warn the user
