# Setup Project

Initialize or update Claude Code configuration for this project.

**Usage:** `/setup-project`

---

## What This Command Does

This command has **TWO modes** based on the project state:

### Mode 1: New Project (No `.claude/` directory)
Creates the initial Claude Code structure from the template.

### Mode 2: Existing Project (Has `.claude/` directory)
Updates the configuration based on the project's technology stack.

---

## IMMUTABLE PREMISES - NEVER MODIFY

These rules are **absolute and cannot be changed**:

1. **ORCHESTRATOR IS THE ONLY CODE WRITER**
   - Subagents CANNOT write, edit, or create code files
   - Only exception: `subagent-docs-analyst` can write .md, swagger, and storybook files

2. **SUBAGENTS ARE CONSULTIVE ONLY**
   - They analyze, research, plan, and recommend
   - The orchestrator executes their recommendations

3. **MANDATORY DOCUMENTATION STEP**
   - `subagent-docs-analyst` is called at the end of EVERY implementation
   - Updates `directory-tree.md` with any structural changes

---

## Mode 1: New Project Setup

### When to Use
- Project has NO `.claude/` directory
- First time setting up Claude Code in this project

### Workflow

#### Step 1: Confirm Template Installation

Ask the user:
```
"This project doesn't have Claude Code configured yet.

I will create the following structure:

.claude/
├── CLAUDE.md              # Orchestrator instructions
├── settings.json          # MCP server configuration
├── agents/                # Subagent definitions
│   ├── subagent-docs-analyst.md
│   └── (more as needed)
└── commands/
    ├── setup-project.md   # This command
    └── create-subagent.md # Create new agents

directory-tree.md          # Project structure reference

Should I proceed?"
```

#### Step 2: Create Basic Structure

Create these files:

**`.claude/CLAUDE.md`** - Orchestrator configuration (use template)

**`.claude/settings.json`** - MCP servers:
```json
{
  "mcpServers": {
    "agent": {
      "type": "url",
      "url": "https://agent-mcp.vercel.app/mcp"
    },
    "figma-remote-mcp": {
      "type": "url",
      "url": "https://mcp.figma.com/mcp"
    },
    "context7": {
      "type": "url",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

**`.claude/agents/subagent-docs-analyst.md`** - Documentation agent (MANDATORY)

**`.claude/commands/setup-project.md`** - This file

**`.claude/commands/create-subagent.md`** - Subagent creation command

**`directory-tree.md`** - Project structure (generate based on actual files)

#### Step 3: Detect Technologies and Add Relevant Agents

Scan for technologies and create appropriate subagents:

| Detected | Subagents to Create |
|----------|---------------------|
| React Web | `subagent-frontend-architect`, `subagent-qa-frontend` |
| React Native | `subagent-mobile-architect`, `subagent-qa-mobile` |
| Node.js/Express | `subagent-backend-architect`, `subagent-qa-backend` |
| Any code | `subagent-security-analyst` |

#### Step 4: Update CLAUDE.md with Project Context

Add technology-specific sections based on detected stack.

---

## Mode 2: Existing Project Update

### When to Use
- Project already has `.claude/` directory
- Updating configuration for new technologies
- Refreshing subagents with latest patterns

### Workflow

#### Step 1: Scan Project Technologies

Detect technologies from:

| File | Technology |
|------|------------|
| `package.json` | Node.js, React, dependencies |
| `requirements.txt` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pubspec.yaml` | Flutter/Dart |
| `*.csproj` | .NET |

#### Step 2: Confirm with User

```
"I detected the following technologies:

[List technologies]

Current subagents:
[List existing subagents]

Recommended changes:
- [Add/Update recommendations]

Should I proceed with these updates?"
```

#### Step 3: Update Subagents

Add technology-specific knowledge to existing subagents:

**For Architects:**
```markdown
## [Technology] Architecture Guidelines

### Patterns to Follow
- [Pattern 1]

### Anti-patterns to Avoid
- [Anti-pattern 1]
```

**For QA:**
```markdown
## [Technology] Testing Guidelines

### Unit Testing
- Tool: [tool]
- Patterns: [patterns]

### E2E Testing
- Tool: [tool]
```

**For Security:**
```markdown
## [Technology] Security Considerations

### Common Vulnerabilities
- [Vulnerability]: [mitigation]
```

#### Step 4: Update CLAUDE.md

Add to the Project Technology Stack section:

```markdown
## Project Technology Stack

### Detected Technologies
- [Language]: [version]
- [Framework]: [version]

### Build Commands
| Command | Purpose |
|---------|---------|
| `npm run dev` | Development |
| `npm test` | Run tests |
```

#### Step 5: Update directory-tree.md

Regenerate the directory tree to reflect current project structure.

---

## Technology Templates

### React/Next.js

**Add to `subagent-frontend-architect.md`:**
```markdown
## Next.js Patterns

### Server vs Client Components
- Default to Server Components
- Use 'use client' only for: interactivity, browser APIs, state

### Data Fetching
- Server Components: async/await
- Route Handlers for API endpoints
- Server Actions for mutations
```

### Express/Node.js Backend

**Add to `subagent-backend-architect.md`:**
```markdown
## Express.js Patterns

### Route Structure
- Controllers handle HTTP
- Services contain business logic
- Repositories handle data access

### Validation
- Use Zod schemas
- Validate at controller level
```

### React Native

**Add to `subagent-mobile-architect.md`:**
```markdown
## React Native Patterns

### State Management
- Redux with connect() (NOT hooks)
- mapStateToProps, mapDispatchToProps

### Navigation
- React Navigation
- Typed routes
```

---

## Skills Management

Skills are reusable knowledge bases that subagents consult for **best practices**, **optimization patterns**, and **complete code examples** using **progressive disclosure** to minimize token usage.

### Why Skills?

**Token Optimization through Progressive Disclosure:**
- Subagents load only `SKILL.md` (~100-200 lines) initially
- Detailed guides (~200-500 lines each) loaded only when needed
- **Savings**: ~300-900 tokens per subagent invocation

### Skill Structure

Each skill follows this structure:
```
.claude/skills/{skill-name}/
├── SKILL.md           # Quick reference (< 300 lines, REQUIRED)
├── {topic-1}.md       # Detailed guide (loaded on demand)
├── {topic-2}.md       # Detailed guide (loaded on demand)
└── ...
```

**Critical Rules:**
- Keep `SKILL.md` under 300 lines for optimal performance
- Put detailed examples in separate guide files
- Link from SKILL.md to guides (loaded only when needed)

### Skill Frontmatter Template

```yaml
---
name: skill-name
version: "1.0.0"
description: Brief description when to use this skill (used by Claude for discovery)
allowed-tools: Read, Grep, Glob, WebSearch
---
```

### Technology to Skill Mapping

#### Pattern Skills (NEW - Progressive Disclosure)

| Detected Technology | Skills to Create | Purpose |
|---------------------|------------------|---------|
| React Native | `mobile-patterns` | Redux connect(), component templates, navigation, forms |
| React Web | `web-app-patterns` | Component patterns, hooks, routing, forms |
| Node.js/Express | `api-patterns` | Controllers, services, repositories, REST patterns |
| Any platform | `testing-patterns` | E2E, unit, integration test templates |
| Any code | `security-patterns` | OWASP Top 10, vulnerability detection, remediation |

#### Optimization Skills (Existing)

| Detected Technology | Skills to Create | Purpose |
|---------------------|------------------|---------|
| React Native | `mobile-optimization` | Performance, FlatList, re-renders |
| React Web | `web-app-optimization` | Bundle size, lazy loading, rendering |
| Node.js/Express | `backend-optimization` | MongoDB queries, caching, parallelization |
| TypeScript (any) | `shared-patterns` | TypeScript best practices, async patterns |

### Skill Verification Workflow

#### Step 1: Check Existing Skills
```bash
ls -1 .claude/skills/
```

#### Step 2: Verify Skill Completeness
For each skill, verify:
- [ ] `SKILL.md` exists with proper frontmatter
- [ ] SKILL.md is under 300 lines (for progressive disclosure)
- [ ] All referenced guides exist in the skill folder
- [ ] Version field is present and follows semver
- [ ] Description is clear for Claude's discovery
- [ ] Subagents reference this skill in their instructions

#### Step 3: Create Missing Skills
If a required skill is missing based on detected technology:

1. **Create skill directory**: `.claude/skills/{skill-name}/`
2. **Create SKILL.md** (< 300 lines):
   - Frontmatter with name, version, description, allowed-tools
   - Quick reference section
   - Links to detailed guides
   - When to consult section
3. **Create topic-specific guides** (200-500 lines each):
   - Complete code examples
   - Best practices
   - Anti-patterns to avoid
4. **Update subagent(s)** to reference the skill:
   ```markdown
   # MANDATORY: Consult Pattern Skills

   **BEFORE providing recommendations, read the pattern skills:**

   ## Step 1: Read Skill
   ```
   Use Read tool: .claude/skills/{skill-name}/SKILL.md
   ```

   ## Step 2: Consult Specific Guides (As Needed)
   - Guide 1: `.claude/skills/{skill-name}/guide-1.md`
   - Guide 2: `.claude/skills/{skill-name}/guide-2.md`
   ```
5. **Update CLAUDE.md** with the new skill in the Available Skills table

#### Step 4: Update Existing Skills
If skill exists but needs updates:

1. **Increment version number** in SKILL.md frontmatter
2. **Update content** based on new patterns discovered
3. **Add new guides** if covering new topics
4. **Remove deprecated content** or mark as deprecated
5. **Test with subagents** to ensure proper loading

### When to Create NEW Skills

Create new skills **ONLY** when:

| Criteria | Create Skill? | Reasoning |
|----------|--------------|-----------|
| **New technology domain** not covered | ✅ Yes | Examples: GraphQL patterns, Rust optimization |
| **Specialized patterns** would bloat existing skills | ✅ Yes | Example: Mobile performance has 4+ detailed guides |
| **Multiple subagents** would benefit | ✅ Yes | Example: testing-patterns used by 3 QA agents |
| **Minor library addition** | ❌ No | Add to existing skill as a new section |
| **Single subagent need** | ❌ No | Include directly in subagent |
| **< 200 lines total content** | ❌ No | Not enough to justify separate skill |

**Examples:**

| Domain | Create Skill? | Reasoning |
|--------|--------------|-----------|
| New database (PostgreSQL) | ✅ Yes, `postgres-patterns` | Different patterns from MongoDB |
| New frontend (Vue) | ✅ Yes, `vue-patterns` | Different from React |
| Adding Prisma to existing Node.js | ❌ No | Update `api-patterns` |
| Minor library (lodash) | ❌ No | Add to `shared-patterns` |

### Skill Naming Convention

- **Pattern skills**: `{platform}-{domain}-patterns` (e.g., `mobile-patterns`)
- **Optimization skills**: `{platform}-{domain}-optimization` (e.g., `backend-optimization`)
- **Shared skills**: `{platform}-shared-{topic}` (e.g., `shared-patterns`)

### Skill Versioning

Follow semantic versioning (semver):

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking changes (removed patterns) | Major | 1.0.0 → 2.0.0 |
| New guides added | Minor | 1.0.0 → 1.1.0 |
| Fixes, clarifications | Patch | 1.0.0 → 1.0.1 |

---

## When to Create NEW Subagents

Only create new subagents when:
1. **Domain is vast** (ML/AI, Game Dev)
2. **Specialized knowledge** would bloat existing agents
3. **Frequent use** in the project

| Domain | Create | Reasoning |
|--------|--------|-----------|
| ML/AI (LangChain, PyTorch) | `subagent-ml-engineer` | Complex domain |
| Game Dev (Unity) | `subagent-game-developer` | Specialized |
| Normal web/mobile | NO | Existing agents sufficient |

---

## Final Checklist

### Mode 1 (New Project)
- [ ] `.claude/` directory created
- [ ] `CLAUDE.md` configured
- [ ] `settings.json` with MCP servers
- [ ] `subagent-docs-analyst.md` created (mandatory)
- [ ] Commands created (`setup-project.md`, `create-subagent.md`)
- [ ] Technology-specific subagents created
- [ ] Technology-specific skills created
- [ ] `directory-tree.md` generated

### Mode 2 (Existing Project)
- [ ] Technologies detected
- [ ] User confirmed changes
- [ ] Subagents updated with tech-specific knowledge
- [ ] Skills verified and updated
- [ ] **Subagents updated to reference new/updated skills**
- [ ] `CLAUDE.md` updated with project context and skills table
- [ ] `directory-tree.md` updated

### Skill Management
- [ ] All skills have proper frontmatter with version
- [ ] SKILL.md files are under 300 lines
- [ ] Detailed guides are in separate files
- [ ] Subagents reference skills in their instructions
- [ ] CLAUDE.md Skills table is up-to-date

---

## directory-tree.md Management

**CRITICAL:** The `directory-tree.md` file is the SINGLE SOURCE OF TRUTH for project structure.

### Generation Template

```markdown
# Project Directory Tree

> **Last updated**: [DATE]
>
> This is the **SINGLE SOURCE OF TRUTH** for project structure.
> All documentation should reference this file.

## Structure

\`\`\`
[project-name]/
├── .claude/
│   ├── CLAUDE.md
│   ├── settings.json
│   ├── agents/
│   │   └── *.md
│   └── commands/
│       └── *.md
├── [detected directories]
├── directory-tree.md
└── README.md
\`\`\`

## Quick Reference

| Path | Description |
|------|-------------|
| `.claude/` | Claude Code configuration |
| [other paths] | [descriptions] |
```

### Rules
- ONLY file that contains directory structure
- Other .md files must REFERENCE this file
- Update when files are added/removed/moved
- `subagent-docs-analyst` maintains this file

---

## Example: New React Native Project

```
User: /setup-project

Agent: "This project doesn't have Claude Code configured.

Detected technologies:
- React Native (from package.json)
- TypeScript
- Redux

I will create:
- .claude/CLAUDE.md
- .claude/settings.json
- .claude/agents/subagent-docs-analyst.md
- .claude/agents/subagent-mobile-architect.md
- .claude/agents/subagent-qa-mobile.md
- .claude/agents/subagent-security-analyst.md
- .claude/commands/setup-project.md
- .claude/commands/create-subagent.md
- directory-tree.md

Should I proceed?"

User: Yes

Agent: [Creates all files]
       [Generates directory-tree.md from actual structure]

       "Setup complete! Claude Code is now configured for your React Native project.

        Created subagents:
        - subagent-docs-analyst (documentation)
        - subagent-mobile-architect (React Native architecture)
        - subagent-qa-mobile (Detox testing)
        - subagent-security-analyst (security review)

        Run /setup-project again anytime to update the configuration."
```

---

## Example: Updating Existing Python Project

```
User: /setup-project

Agent: "Project already has Claude Code configured.

Detected technologies:
- Python 3.11
- FastAPI
- PostgreSQL
- Pytest

Current subagents:
- subagent-docs-analyst ✓
- subagent-backend-architect ✓
- subagent-security-analyst ✓

Recommended updates:
1. Add FastAPI patterns to subagent-backend-architect
2. Add Python security concerns to subagent-security-analyst
3. Update CLAUDE.md with Python commands
4. Refresh directory-tree.md

Should I proceed?"

User: Yes

Agent: [Updates subagents with FastAPI knowledge]
       [Updates CLAUDE.md]
       [Regenerates directory-tree.md]

       "Configuration updated for FastAPI!"
```
