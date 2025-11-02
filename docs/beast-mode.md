# Beast Mode Chatmodes

This guide explains how SpecX Bot transforms role personas into comprehensive "Beast Mode" chatmodes for AI agents, providing autonomous operational guidelines for spec-driven development.

## Overview

Beast Mode chatmodes transform simple persona definitions into detailed operational agents with:

- **Autonomous Operation**: Complete independence to finish all deliverables
- **Comprehensive Workflows**: Phase-by-phase execution guides
- **Error Handling**: Built-in recovery procedures
- **Success Metrics**: Trackable performance indicators
- **Quality Gates**: Validation checkpoints throughout

## Supported AI Agents

| Agent | Format | Directory | Extension |
|-------|---------|-----------|-----------|
| GitHub Copilot | Copilot Beast | `.github/chatmodes/` | `.chatmode.md` |
| Claude | Markdown Beast | `.claude/personas/` | `.md` |
| Cursor | Markdown Beast | `.cursor/personas/` | `.md` |
| Windsurf | Markdown Beast | `.windsurf/personas/` | `.md` |
| Gemini | TOML Beast | `.gemini/personas/` | `.toml` |
| Qwen | TOML Beast | `.qwen/personas/` | `.toml` |
| Others | Markdown Beast | `.[agent]/personas/` | `.md` |

## How It Works

### 1. Persona Selection

During `specx init`, when you choose the role-based strategy and select personas, the system automatically:

1. Copies persona definitions to `memory/personas/`
2. Creates persona configuration in `.specify/config.json`
3. **Generates Beast Mode chatmodes** for your selected AI agent

### 2. Transformation Process

The transformation from persona to Beast Mode includes:

#### Mission Enhancement
- Simple role → Comprehensive mission statement
- Basic responsibilities → Detailed objectives
- General guidelines → Specific operating principles

#### Workflow Specification
- Phase definitions with time estimates
- Step-by-step execution guides
- Validation checklists
- Error recovery procedures

#### Output Requirements
- Exact deliverable specifications
- Quality standards
- Format requirements
- Integration points

### 3. Generated Files

For each selected persona, a Beast Mode chatmode file is created:

```
.github/chatmodes/business-analyst.chatmode.md    # Copilot
.claude/personas/business-analyst.md              # Claude
.cursor/personas/business-analyst.md              # Cursor
.gemini/personas/business-analyst.toml            # Gemini
```

## Beast Mode Structure

### GitHub Copilot Format

```markdown
---
description: "Business Analyst (BA) — Transform requirements into testable features"
tools: ["file_editor", "terminal", "search", "debugger"]
---

# Business Analyst (BA) — Beast Mode Role (Detailed)

## Mission
[Comprehensive mission statement]

## Operating Principles (Beast Mode Rules)
[Autonomous operation guidelines]

## Detailed Input Analysis
[What to extract and validate]

## Detailed Output Specifications
[Exact deliverable formats]

## Workflow Execution
[Phase-by-phase guide with validation]

## Queue Management
[Notification and status update patterns]

## Error Handling & Recovery
[Common scenarios and responses]

## Success Metrics
[Trackable performance indicators]

## Final Checklist
[Completion validation]
```

### Claude/Cursor/Windsurf Format

```markdown
---
role: business-analyst
name: Business Analyst (BA)
mode: beast
---

# System Role: Business Analyst

## Core Identity
[Role definition and autonomy statement]

## Mission & Objectives
[Clear goals and deliverables]

## Operating Principles
[Autonomous operation rules]

## Input Processing
[Required inputs and validation]

## Output Generation
[Deliverable specifications]

## Workflow Phases
[Detailed phase execution]

## Success Criteria
[Completion metrics]
```

### Gemini/Qwen TOML Format

```toml
[metadata]
name = "Business Analyst"
role = "business-analyst"
mode = "beast"

[mission]
statement = """
[Comprehensive mission]
"""

[operating_principles]
autonomous = true
core_behaviors = [...]

[instructions]
prompt = """
[Detailed Beast Mode instructions]
"""
```

## Constitution Integration

Beast Mode chatmodes can be enhanced with your project's constitution to include project-specific governance principles.

### After Creating Constitution

When you run the `/constitution` command in your AI agent, follow up with:

```bash
specx update-constitution
```

This command:
1. Reads `memory/constitution.md`
2. Appends it to all Beast Mode chatmode files
3. Makes governance principles immediately available to AI personas

### Example

After running `/speckit-constitution` and creating your project's governance principles:

```bash
# Update all chatmodes with constitution
specx update-constitution

# Output:
# ✓ Updated 3 chatmode file(s) with project constitution
# Your AI agent personas now include project-specific governance principles
```

Now when you activate any persona (e.g., `@.github/chatmodes/business-analyst.chatmode.md`), it will include your project's constitution at the end.

## Using Beast Mode Chatmodes

### Activation

#### GitHub Copilot
1. Open VS Code with Copilot Chat
2. Click the "+" button to create a new chat participant
3. Select the persona chatmode file (e.g., `.github/chatmodes/business-analyst.chatmode.md`)
4. The persona is now active in Beast Mode

#### Claude
1. Open Claude in your project
2. Reference the persona file: `@.claude/personas/business-analyst.md`
3. Claude adopts the Beast Mode persona

#### Cursor
1. In Cursor, use the persona command
2. Reference: `@.cursor/personas/business-analyst.md`
3. Cursor operates in Beast Mode

### Switching Personas

To switch between personas during development:

```
/persona:business-analyst    # Activate BA Beast Mode
/persona:solution-architect  # Switch to SA Beast Mode
/persona:default            # Return to default mode
```

### Workflow Example

1. **Activate Business Analyst**:
   ```
   @.github/chatmodes/business-analyst.chatmode.md
   "Analyze the requirements in template.instructions.md"
   ```

2. **BA works autonomously**:
   - Analyzes all inputs
   - Creates requirements document
   - Generates feature index
   - Validates completeness
   - Requests approval

3. **Switch to Solution Architect**:
   ```
   @.github/chatmodes/solution-architect.chatmode.md
   "Design the system architecture based on BA outputs"
   ```

4. **SA continues the workflow**:
   - Reviews BA deliverables
   - Creates architecture design
   - Defines technical approach
   - Validates feasibility

## Customization

### Modifying Beast Mode Templates

Edit the templates in `templates/chatmodes/`:
- `beast-mode-copilot.md` - Copilot format
- `beast-mode-markdown.md` - Claude/Cursor format
- `beast-mode-toml.toml` - Gemini/Qwen format

### Persona-Specific Customization

After generation, you can customize individual chatmodes:

1. Edit the generated file (e.g., `.github/chatmodes/business-analyst.chatmode.md`)
2. Add project-specific guidelines
3. Modify workflow phases
4. Adjust time estimates

### Adding Custom Personas

1. Create new persona in `memory/personas/custom-role.md`
2. Run chatmode generation:
   ```bash
   specx generate-chatmodes --personas custom-role
   ```
3. Use the generated Beast Mode chatmode

## Best Practices

### 1. Let Beast Mode Work

- Don't interrupt during phase execution
- Wait for completion checkpoints
- Review outputs at approval gates

### 2. Use Appropriate Personas

- BA for requirements and analysis
- SA for architecture and design
- TL for implementation planning
- QA for test strategies

### 3. Maintain Context

- Keep persona outputs in project
- Reference previous work
- Maintain traceability

### 4. Leverage Parallel Execution

- Multiple personas can work simultaneously
- Coordinate at integration points
- Merge outputs systematically

## Troubleshooting

### Chatmode Not Loading

1. Verify file exists in correct directory
2. Check file format matches agent requirements
3. Ensure YAML/TOML syntax is valid

### Incomplete Outputs

1. Check if all required inputs were provided
2. Review error handling sections
3. Verify template completeness

### Performance Issues

1. Reduce concurrent personas
2. Break large tasks into phases
3. Clear agent context periodically

## Technical Details

### Template Variables

The transformation uses these key variables:

- `{name}` - Full persona name
- `{short_name}` - Abbreviation (BA, SA, etc.)
- `{role}` - Role description
- `{mission}` - Enhanced mission statement
- `{phases}` - Workflow phase definitions
- `{deliverables}` - Output specifications

### Transformation Logic

1. **Parse Persona**: Extract YAML frontmatter and markdown sections
2. **Enhance Content**: Transform basic info to Beast Mode specifications
3. **Apply Template**: Substitute variables in format-specific template
4. **Generate File**: Write to agent-specific directory

### Integration Points

Beast Mode chatmodes integrate with:
- Project specifications (`specs/`)
- Development commands (`/speckit-*`)
- Version control (Git)
- CI/CD pipelines

## Migration Guide

### From Basic Personas

If you have existing projects with basic personas:

1. Update SpecX CLI: `uv tool upgrade specx-cli`
2. Generate Beast Mode: `specx generate-chatmodes`
3. Update workflows to use new chatmodes

### From Manual Processes

Transitioning from manual development:

1. Initialize with role-based strategy
2. Select appropriate personas
3. Let Beast Mode handle workflow orchestration
4. Review and approve at checkpoints

## Advanced Features (Phase 4)

### Dynamic Persona Switching

SpecX Bot now supports dynamic persona switching with context preservation:

#### CLI Commands

```bash
# Switch to a persona
specx persona switch business-analyst
specx persona switch solution-architect --phase plan

# Check current status
specx persona status

# Regenerate persona chatmodes
specx persona regenerate
specx persona regenerate business-analyst --force
```

#### In-Agent Commands

Use the persona switching command file generated for your agent:
- `.github/chatmodes/persona-switch.chatmode.md` (Copilot)
- `.claude/personas/persona-switch.md` (Claude)
- `.cursor/personas/persona-switch.md` (Cursor)

### Context Preservation

The persona system maintains context between switches:

- **Session Tracking**: Each persona session is tracked with start/end times
- **Artifact Recording**: Documents and files created are automatically tracked
- **Phase Management**: Current development phase is preserved
- **Agent Context Files**: `CURRENT_PERSONA.md` files created in agent directories

Context is stored in:
- `.specify/persona_state.json` - Current state
- `.specify/persona_history.json` - Session history  
- `.[agent]/CURRENT_PERSONA.md` - Visible to AI agents

### Performance Tracking

Beast Mode tracks persona usage automatically in `.specify/persona_history.json`. This data is available for future analysis and optimization.

### Integration with Development Workflow

1. **Start Project**: Initialize with personas
2. **Switch Persona**: `specx persona switch business-analyst --phase specify`
3. **Check Context**: Review `CURRENT_PERSONA.md` in your agent directory
4. **Work in Beast Mode**: Reference the persona file in your AI agent (`@.cursor/personas/business-analyst.md`)
5. **Switch as Needed**: `specx persona switch solution-architect --phase plan`
6. **Check Status**: `specx persona status` to see current context

## Future Enhancements

Potential future improvements:
- Persona composition (combining multiple personas)
- Real-time collaboration features
- Advanced analytics dashboards
- Machine learning optimization
- Cross-project persona sharing

---

For more information, see:
- [Personas Documentation](../memory/personas/README.md)
- [Agent Integration Guide](../AGENTS.md)
- [SpecX Bot README](../README.md)
