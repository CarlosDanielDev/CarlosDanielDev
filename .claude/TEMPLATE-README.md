# Claude Code Agents Template

A template for setting up Claude Code with orchestrated subagents. Copy to any project to enable AI-powered development workflow.

**Repository:** [your-org/claude-code-agents-template](https://github.com/your-org/claude-code-agents-template)

## Quick Start

### Option 1: Copy to Existing Project

```bash
# Copy the .claude folder to your project
cp -r .claude your-project/

# Copy the directory-tree template
cp directory-tree.md your-project/

# Run setup to configure for your project
cd your-project
claude
# Then run: /setup-project
```

### Option 2: Use as Template

1. Clone this repository
2. Run `/setup-project` in Claude Code
3. The command will detect your technologies and configure agents

## Project Structure

For the complete directory structure, see [directory-tree.md](../directory-tree.md).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                                │
│                 (The ONLY agent that writes code)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONSULTIVE SUBAGENTS                          │
│              (CANNOT write code - only analyze & recommend)      │
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐             │
│  │   Architects        │    │   Quality & Docs    │             │
│  │                     │    │                     │             │
│  │ - mobile-architect  │    │ - qa-frontend       │             │
│  │ - frontend-architect│    │ - qa-backend        │             │
│  │ - backend-architect │    │ - qa-mobile         │             │
│  │                     │    │ - security-analyst  │             │
│  └─────────────────────┘    │ - docs-analyst*     │             │
│                              └─────────────────────┘             │
│                                                                  │
│  * docs-analyst CAN write .md, swagger, and storybook files     │
└─────────────────────────────────────────────────────────────────┘
```

## Key Principles

1. **Orchestrator writes ALL code** - Subagents provide blueprints, orchestrator executes
2. **Subagents are CONSULTIVE only** - They analyze, research, plan, and recommend
3. **Documentation is MANDATORY** - `subagent-docs-analyst` runs at the end of every task
4. **Single source of truth** - `directory-tree.md` is the only file with project structure

## Modes of Operation

### 🎸 Vibe Coding (Simple)
- Work directly without analysis subagents
- Faster for small tasks
- Only `docs-analyst` at the end

### 🤖 Subagents Orchestrator (Complex)
- Full workflow: Architect → Execute → Security → QA → Docs
- Better for production-quality code
- Recommended for medium/large features

## Commands

| Command | Description |
|---------|-------------|
| `/setup-project` | Initialize or update Claude Code configuration |
| `/create-subagent` | Create a new consultive subagent |
| `/setup-notifications` | Configure desktop and Slack notifications |
| `/update-from-template` | Sync template updates to other projects |

## Notifications

Get notified when Claude Code needs your attention.

### Quick Setup

```bash
/setup-notifications
```

This interactive command allows you to:
- Enable/disable desktop notifications
- Enable/disable Slack notifications
- Configure your Slack User ID
- Choose notification types (permission prompts, idle prompts)

### Configuration File

Settings are stored in `~/.claude/notifications.conf`:

```bash
NOTIFY_DESKTOP=true          # Desktop popup + sound
NOTIFY_SLACK=true            # Slack DM notifications
NOTIFY_PERMISSION_PROMPT=true # When Claude needs approval
NOTIFY_IDLE_PROMPT=true      # When Claude waits for input
SLACK_USER_ID=U0XXXXXXXX     # Your Slack User ID
```

### Desktop Notifications

**Works out of the box on:**
- macOS (native with sound)
- Linux (requires `notify-send`)
- Windows (toast notifications)

### Slack Notifications

Receive DMs when Claude needs your input.

**How to get your Slack User ID:**
1. Open Slack
2. Click your name/photo (top right)
3. Click **Profile**
4. Click the **three dots** (...)
5. Click **Copy member ID**

### Notification Format

Notifications include the **project name** and **context**:

```
⚠️ mobile-app - Permission for bash command
⏳ web-app - Waiting for your response
```

## Included Subagents

### Core (Production Ready)

| Subagent | Purpose |
|----------|---------|
| `subagent-docs-analyst` | Documentation management, directory-tree.md |
| `subagent-mobile-architect` | React Native architecture |
| `subagent-frontend-architect` | React Web architecture |
| `subagent-backend-architect` | Express.js, MongoDB, APIs |
| `subagent-security-analyst` | OWASP, vulnerability detection |
| `subagent-qa-mobile` | Detox, device testing |
| `subagent-qa-frontend` | Playwright, visual regression |
| `subagent-qa-backend` | Supertest, Jest, MongoDB |

### Drafts (In Development)

Located in `drafts/agents/` - copy to `.claude/agents/` when ready.

## MCP Servers

Pre-configured in `.claude/settings.json`:

| Server | Purpose |
|--------|---------|
| `agent` | Internal patterns and checklists |
| `figma-remote-mcp` | Figma design integration |
| `context7` | Library documentation |

### Adding GitHub MCP

```bash
claude mcp add --transport http github \
  https://api.githubcopilot.com/mcp/ \
  -H "Authorization: Bearer YOUR_GITHUB_PAT"
```

## Documentation Management

### directory-tree.md

This file is the **SINGLE SOURCE OF TRUTH** for project structure.

**Rules:**
- Only `directory-tree.md` contains the directory tree
- All other .md files must reference it
- `subagent-docs-analyst` maintains it automatically
- Updated when files are added/removed/moved

**Reference in your docs:**
```markdown
For project structure, see [directory-tree.md](./directory-tree.md).
```

## Keeping Your Project Updated

Use `/update-from-template` to sync new features from the template:

```bash
# Run from the template directory
/update-from-template
```

This command will:
- Ask for your project path
- Show what's new in the template
- Let you select what to update
- Create backups before changes
- Preserve your customizations

## Contributing

### Creating a Subagent

1. Start in `drafts/agents/`:
```bash
touch drafts/agents/subagent-your-name.md
```

2. Follow the template in `/create-subagent`

3. Test thoroughly

4. Move to `.claude/agents/` when ready

### Subagent Rules

- Subagents are **CONSULTIVE ONLY**
- Cannot use Write, Edit, or Bash tools
- Must provide exact file paths, line numbers, and code examples
- Exception: `docs-analyst` can write .md files

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history and updates.

## License

MIT
