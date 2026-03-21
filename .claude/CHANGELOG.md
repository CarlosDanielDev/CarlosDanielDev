# Changelog - Claude Code Agents Template

All notable changes to this template will be documented in this file.

**MANDATORY:** Every update to this template MUST include an entry in this changelog.

Format: `## [Date] - Summary`

---

## [2025-01-13] - Template Sync & Notifications

### Added
- `/setup-notifications` command - Configure desktop and Slack notifications
- `/update-from-template` command - Sync template updates to other projects
- `CHANGELOG.md` - Track all template changes (this file)
- `TEMPLATE-README.md` - Template documentation (moved from root README)
- Notification hooks for desktop (macOS/Linux/Windows) and Slack
- `notifications.conf` configuration file format

### Changed
- Root `README.md` is now a minimal template for projects to customize
- Documentation split: template docs in `.claude/`, project docs in root

### Structure
```
.claude/
  CHANGELOG.md        # NEW - This file
  TEMPLATE-README.md  # NEW - Full template documentation
  commands/
    update-from-template.md  # NEW - Sync command
    setup-notifications.md   # Previously added
```

---

## [2025-01-08] - Initial Template

### Added
- Orchestrator pattern with consultive subagents
- Core subagents: mobile-architect, frontend-architect, backend-architect
- QA subagents: qa-mobile, qa-frontend, qa-backend
- Security and documentation subagents
- `/setup-project` command
- `/create-subagent` command
- MCP server configurations (agent, figma-remote-mcp, context7)
- Two operation modes: Vibe Coding and Subagents Orchestrator
- `directory-tree.md` as single source of truth for structure

---

## Template Update Rules

When updating this template:

1. **Always add a CHANGELOG entry** with:
   - Date in `[YYYY-MM-DD]` format
   - Clear summary of changes
   - Sections: Added, Changed, Fixed, Removed, Structure (if applicable)

2. **Run `/update-from-template`** in downstream projects to propagate changes

3. **Document breaking changes** clearly so users know what to adjust

4. **Update TEMPLATE-README.md** if features are added/changed
