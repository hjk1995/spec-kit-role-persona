# Constitution Integration with Beast Mode

This guide explains how project constitutions are integrated into Beast Mode chatmodes to ensure AI personas follow project-specific governance principles.

## Overview

When you create or update your project's constitution using the `/constitution` command, the governance principles should be made available to all Beast Mode personas. This ensures that every AI agent operating in Beast Mode understands and follows your project's standards.

## Workflow

### 1. Create/Update Constitution

Run the constitution command in your AI agent:

```
/speckit-constitution

Create a project constitution with these principles:
- Code quality standards
- Security requirements
- Testing requirements
- Documentation standards
```

The AI will:
- Create or update `memory/constitution.md`
- Include persona-specific governance principles if personas are enabled
- Version the constitution appropriately

### 2. Update Beast Mode Chatmodes

After the constitution is written, the AI agent will automatically run:

```bash
specx update-constitution
```

This command:
- Reads `memory/constitution.md`
- Appends/updates constitution in persona definition files (`memory/personas/*.md`)
- Appends/updates constitution in Beast Mode chatmode files (agent directory)
- Makes governance principles immediately available to personas

### 3. Verify Integration

Check that your files now include the constitution:

```bash
# Check persona definition files
tail -50 memory/personas/business-analyst.md

# Check chatmode files (for Copilot)
tail -50 .github/chatmodes/business-analyst.chatmode.md

# Check chatmode files (for Cursor)
tail -50 .cursor/personas/business-analyst.md

# You should see a "## Project Constitution" section at the end of each file
```

## How It Works

### Constitution Injection

The `update_chatmodes_with_constitution()` function:

1. **Updates persona definition files** in `memory/personas/`
   - Injects constitution into source persona files
   - These are used when referencing personas directly
   
2. **Updates Beast Mode chatmode files** in agent-specific directory
   - Injects constitution into generated chatmode files
   - Works with all agent formats (Copilot, Markdown, TOML)

3. **Checks for existing constitution** section
   - If found, replaces with updated version
   - If not found, appends at the end

4. **Preserves existing** file structure and content
   - Only adds/updates the constitution section
   - All other content remains unchanged

### Example Output

A chatmode file after constitution integration:

```markdown
---
description: "Business Analyst (BA) — Transform requirements into testable features"
tools: ['edit', 'search', 'new', ...]
---

# Business Analyst (BA) — Beast Mode Role (Detailed)

## Mission
[Beast Mode mission...]

## Operating Principles
[Beast Mode principles...]

[... rest of Beast Mode content ...]

---

## Project Constitution

# Project Constitution

Version: 1.0.0
Ratified: 2025-11-02
Last Amended: 2025-11-02

## Core Principles

### Principle 1: Code Quality
All code MUST meet our quality standards:
- Test coverage > 80%
- No critical linter errors
- Documented public APIs

### Principle 2: Security First
Security MUST be considered at every phase:
- OWASP Top 10 addressed
- Dependencies regularly updated
- Security review for all features

[... more principles ...]
```

## Benefits

### 1. Consistent Governance
All AI personas automatically follow the same project principles

### 2. Context-Aware Decisions
Personas make decisions aligned with project standards

### 3. Reduced Review Cycles
AI outputs already comply with governance requirements

### 4. Team Alignment
Constitution ensures all AI-assisted work follows team standards

## Manual Update

If you need to manually update chatmodes with constitution:

```bash
# From your project directory
specx update-constitution
```

Output:
```
Updating Beast Mode chatmodes with project constitution...
✓ Updated 3 chatmode file(s) with project constitution
Your AI agent personas now include project-specific governance principles
```

## Constitution Updates

Whenever you update your constitution:

1. Run `/constitution` in your AI agent (or edit `memory/constitution.md` directly)
2. Run `specx update-constitution`
3. All personas will use the updated principles

The constitution section is **replaced** if it already exists, so you always have the latest version.

## Supported Formats

Constitution integration works with all Beast Mode formats:

- **Copilot**: `.github/chatmodes/*.chatmode.md`
- **Claude**: `.claude/personas/*.md`
- **Cursor**: `.cursor/personas/*.md`
- **Windsurf**: `.windsurf/personas/*.md`
- **Gemini**: `.gemini/personas/*.toml`
- **Qwen**: `.qwen/personas/*.toml`

For TOML formats, the constitution is converted to a TOML comment block.

## Best Practices

1. **Update After Changes**: Always run `specx update-constitution` after modifying the constitution
2. **Review Integration**: Check that constitution appears in chatmode files
3. **Version Tracking**: Constitution versions are embedded, making it easy to track changes
4. **Team Communication**: Notify team when constitution is updated

## Troubleshooting

### Constitution Not Appearing

**Problem:** Constitution section not showing in chatmode files

**Solutions:**
1. Verify `memory/constitution.md` exists
2. Run `specx update-constitution` manually
3. Check chatmode files exist: `ls .github/chatmodes/`
4. Regenerate chatmodes: `specx regenerate-chatmodes --force`

### Old Constitution Version

**Problem:** Chatmodes have old constitution content

**Solution:**
```bash
# Update constitution in memory/constitution.md
# Then update chatmodes
specx update-constitution
```

### Constitution Too Long

**Problem:** Constitution makes chatmode files very large

**Solution:**
Keep constitution focused on essential principles. Consider:
- Link to detailed docs instead of embedding everything
- Use concise principle statements
- Remove redundant sections

## See Also

- [Beast Mode Documentation](beast-mode.md)
- [Persona Usage Guide](persona-usage-guide.md)
- [Constitution Template](../memory/constitution.md)
