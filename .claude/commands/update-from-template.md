# Update From Template

Sync updates from the Claude Code Agents Template to another local project.

**IMPORTANT:** This command asks MANY questions and confirmations before making any changes. Each project is specialized and must be treated with care.

**NOTE:** This command does NOT execute git commands. The user is responsible for reviewing changes and committing when ready. If something goes wrong, use git to revert.

## Prerequisites

- You must run this command FROM WITHIN the template repository
- The target project must have an existing `.claude/` folder
- The target project should be a git repository (for easy rollback if needed)

## Command Flow

### 1. Verify we are in the template

```bash
# Check if we are in the template
if [[ ! -f ".claude/CHANGELOG.md" ]] || [[ ! -d ".claude/agents" ]]; then
  echo "ERROR: This command must be run FROM WITHIN the claude-code-agents-template repository"
  exit 1
fi
TEMPLATE_PATH=$(pwd)
echo "Template detected at: $TEMPLATE_PATH"
```

### 2. Ask for target project path

Use AskUserQuestion with text input:
```
"What is the ABSOLUTE path of the project you want to update?"

Example: /Users/db/Projects/YourProject/mobile-app
```

Then validate:
```bash
TARGET_PATH="PATH_PROVIDED_BY_USER"

# Check if exists
if [[ ! -d "$TARGET_PATH" ]]; then
  echo "ERROR: Directory not found: $TARGET_PATH"
  exit 1
fi

# Check if has .claude
if [[ ! -d "$TARGET_PATH/.claude" ]]; then
  echo "ERROR: Project does not have .claude/ folder. Run /setup-project first."
  exit 1
fi

echo "Project found: $TARGET_PATH"
```

### 3. Read template CHANGELOG

```bash
echo "=== Template CHANGELOG ==="
cat "$TEMPLATE_PATH/.claude/CHANGELOG.md"
```

Ask the user:
```
"Which updates do you want to apply to $TARGET_PATH?"
- All updates
- Select manually
- Only view differences (do not change anything)
```

### 4. Analyze differences

For each file category, compare and show:

#### 4.1 Subagents (.claude/agents/)

```bash
echo "=== Comparing Subagents ==="
echo ""
echo "In template:"
ls -1 "$TEMPLATE_PATH/.claude/agents/"
echo ""
echo "In project:"
ls -1 "$TARGET_PATH/.claude/agents/" 2>/dev/null || echo "(none)"
echo ""

# New files in template
echo "New in template (do not exist in project):"
comm -23 <(ls "$TEMPLATE_PATH/.claude/agents/" | sort) <(ls "$TARGET_PATH/.claude/agents/" 2>/dev/null | sort)

# Modified files (exist in both)
echo ""
echo "Exist in both (check for differences):"
comm -12 <(ls "$TEMPLATE_PATH/.claude/agents/" | sort) <(ls "$TARGET_PATH/.claude/agents/" 2>/dev/null | sort)
```

#### 4.2 Commands (.claude/commands/)

```bash
echo "=== Comparing Commands ==="
echo ""
echo "In template:"
ls -1 "$TEMPLATE_PATH/.claude/commands/"
echo ""
echo "In project:"
ls -1 "$TARGET_PATH/.claude/commands/" 2>/dev/null || echo "(none)"
```

#### 4.3 Hooks (.claude/hooks/)

```bash
echo "=== Comparing Hooks ==="
echo ""
echo "In template:"
ls -1 "$TEMPLATE_PATH/.claude/hooks/"
echo ""
echo "In project:"
ls -1 "$TARGET_PATH/.claude/hooks/" 2>/dev/null || echo "(none)"
```

#### 4.4 Skills (.claude/skills/)

```bash
echo "=== Comparing Skills ==="
echo ""
echo "In template:"
ls -1 "$TEMPLATE_PATH/.claude/skills/" 2>/dev/null || echo "(none)"
echo ""
echo "In project:"
ls -1 "$TARGET_PATH/.claude/skills/" 2>/dev/null || echo "(none)"
echo ""

# For each skill folder, compare contents and versions
for skill in $(ls "$TEMPLATE_PATH/.claude/skills/" 2>/dev/null); do
  echo "Skill: $skill"
  echo "  Template files:"
  ls -1 "$TEMPLATE_PATH/.claude/skills/$skill/"

  # Extract version from template
  TEMPLATE_VERSION=$(grep "^version:" "$TEMPLATE_PATH/.claude/skills/$skill/SKILL.md" 2>/dev/null | sed 's/version: "\(.*\)"/\1/')
  echo "  Template version: $TEMPLATE_VERSION"

  if [ -d "$TARGET_PATH/.claude/skills/$skill" ]; then
    echo "  Project files:"
    ls -1 "$TARGET_PATH/.claude/skills/$skill/"

    # Extract version from project
    PROJECT_VERSION=$(grep "^version:" "$TARGET_PATH/.claude/skills/$skill/SKILL.md" 2>/dev/null | sed 's/version: "\(.*\)"/\1/')
    echo "  Project version: $PROJECT_VERSION"

    # Compare versions
    if [ "$TEMPLATE_VERSION" != "$PROJECT_VERSION" ]; then
      echo "  ⚠️  VERSION MISMATCH - Update available"
    else
      echo "  ✓ Versions match"
    fi
  else
    echo "  Project: (not installed)"
    echo "  📦 NEW SKILL AVAILABLE"
  fi
  echo ""
done
```

#### 4.5 CLAUDE.md

```bash
echo "=== Comparing CLAUDE.md ==="
if diff -q "$TEMPLATE_PATH/.claude/CLAUDE.md" "$TARGET_PATH/.claude/CLAUDE.md" > /dev/null 2>&1; then
  echo "Files are identical"
else
  echo "Files are DIFFERENT"
  echo ""
  echo "Lines in template: $(wc -l < "$TEMPLATE_PATH/.claude/CLAUDE.md")"
  echo "Lines in project:  $(wc -l < "$TARGET_PATH/.claude/CLAUDE.md")"
fi
```

### 5. Interactive selection

For EACH category, ask separately using AskUserQuestion:

#### 5.1 Subagents

```
"Which SUBAGENTS do you want to update/add?"
(multiSelect: true)
- subagent-mobile-architect.md (NEW)
- subagent-frontend-architect.md (MODIFIED)
- subagent-backend-architect.md (IDENTICAL - skip)
... etc
```

#### 5.2 Commands

```
"Which COMMANDS do you want to update/add?"
(multiSelect: true)
- setup-notifications.md (NEW)
- update-from-template.md (NEW)
- setup-project.md (MODIFIED)
... etc
```

#### 5.3 Hooks

```
"Which HOOKS do you want to update/add?"
(multiSelect: true)
- notify.sh (NEW)
- notify.ps1 (NEW)
... etc
```

#### 5.4 Skills

```
"Which SKILLS do you want to update/add?"
(multiSelect: true)
- mobile-patterns/ (NEW - v1.0.0 - 8 files: patterns, templates, navigation, forms)
- testing-patterns/ (NEW - v1.0.0 - 10 files: detox, playwright, supertest, device matrix)
- security-patterns/ (NEW - v1.0.0 - 4 files: OWASP, detection, remediation)
- api-patterns/ (NEW - v1.0.0 - 7 files: REST, controllers, services, validation)
- mobile-optimization/ (UPDATE - v1.0.0→v1.1.0 - 4 files)
- shared-patterns/ (IDENTICAL - v1.0.0 - skip)
... etc
```

**Important Notes:**
- Skills are installed as **complete folders** (all files within the skill)
- Selecting a skill will **overwrite all files** in that skill folder
- **Version tracking**: Template version vs Project version shown
- **Progressive disclosure benefit**: Reduces token usage by 300-900 per invocation

#### 5.5 CLAUDE.md

```
"The project's CLAUDE.md has been CUSTOMIZED for the project."
"How do you want to proceed?"
- Keep current project version (do not change)
- Replace with template (WILL LOSE customizations)
- View detailed diff before deciding
```

### 6. Final confirmation

Show a summary of what will be done:

```
=== CHANGE SUMMARY ===

Project: /Users/db/Projects/YourProject/mobile-app

Files to ADD:
- .claude/commands/setup-notifications.md
- .claude/hooks/notify.sh

Skills to ADD:
- .claude/skills/shared-patterns/ (3 files)
- .claude/skills/mobile-optimization/ (4 files)
- .claude/skills/web-app-optimization/ (4 files)
- .claude/skills/backend-optimization/ (4 files)

Files to UPDATE:
- .claude/agents/subagent-frontend-architect.md
- .claude/commands/setup-project.md

Files to KEEP (no changes):
- .claude/CLAUDE.md (customized for project)

NOTE: Use git to revert if needed.

Do you want to proceed? (Yes/No)
```

### 7. Execute updates

For each selected file, use the Read tool to get content from template and Write tool to update project:

```
# For each file selected:
1. Read file from template
2. Write file to target project
3. Report: "Updated: filename.md"
```

For each selected skill, copy the entire folder:

```bash
# For each skill selected:
# 1. Create skill directory in target if not exists
mkdir -p "$TARGET_PATH/.claude/skills/$SKILL_NAME"

# 2. Copy all files from template skill folder
for file in $(ls "$TEMPLATE_PATH/.claude/skills/$SKILL_NAME/"); do
  # Read from template and Write to target
  # Report: "Updated: .claude/skills/$SKILL_NAME/$file"
done
```

### 8. Update project CHANGELOG (if exists)

If the project has a CHANGELOG.md, add an entry at the top (after header):

```markdown
## [YYYY-MM-DD] - Sync from Template

### Updated from claude-code-agents-template
- Files synced: [list of files]
- Template version: [date from template CHANGELOG]
```

### 9. Final summary

```
=== UPDATE COMPLETE ===

Files added: X
Files updated: Y
Skills added/updated: W
Files kept: Z

Changes are NOT committed. Review the changes and commit when ready.
To revert all changes: git checkout -- .claude/
```

---

## Expected Behavior

### Be VERY conservative

- ALWAYS ask before changing
- NEVER replace customized files without explicit confirmation
- Show diffs when relevant
- Let user control git

### Respect specializations

Each project may have:
- Customized subagents (do not overwrite)
- CLAUDE.md adapted to the project
- Specific hooks
- Additional commands

### File categories

| Category | Default behavior | Versioning |
|----------|-----------------|------------|
| Generic subagents | Update if newer | Line count comparison |
| Customized subagents | NEVER replace automatically | Manual review only |
| Template commands | Update/add | Compare with template |
| Custom commands | Keep | User-managed |
| Hooks | Always ask | User decision |
| **Skills** | **Update/add (entire folders)** | **Semantic versioning (semver)** |
| CLAUDE.md | NEVER replace without confirmation | Manual review |
| settings.json | Merge (add new MCPs) | - |

**Skills Versioning Rules:**
- Compare version numbers in SKILL.md frontmatter
- Template v1.1.0 > Project v1.0.0 → Suggest update
- Template v1.0.0 = Project v1.0.0 → Skip (identical)
- Template v2.0.0 > Project v1.9.0 → **Breaking change** (warn user)

### Customization detection

A file is considered "customized" if:
- Has project-specific comments
- Mentions the project name
- Has significant differences (>20% different lines)
- User previously marked it as customized

---

## What This Command Does NOT Do

- **Does NOT run git commands** - User controls versioning
- **Does NOT create backups** - Git is the backup
- **Does NOT force any changes** - Everything requires confirmation
- **Does NOT touch files outside .claude/** - Only syncs template files
