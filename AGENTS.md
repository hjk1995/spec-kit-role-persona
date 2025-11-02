# AGENTS.md

## About SpecX Bot and Specify

**GitHub SpecX Bot** is a comprehensive toolkit for implementing Spec-Driven Development (SDD) - a methodology that emphasizes creating clear specifications before implementation. The toolkit includes templates, scripts, and workflows that guide development teams through a structured approach to building software.

**SpecX CLI** is the command-line interface that bootstraps projects with the SpecX Bot framework. It sets up the necessary directory structures, templates, and AI agent integrations to support the Spec-Driven Development workflow.

The toolkit supports multiple AI coding assistants, allowing teams to use their preferred tools while maintaining consistent project structure and development practices.

---

## General practices

- Any changes to `__init__.py` for the SpecX CLI require a version rev in `pyproject.toml` and addition of entries to `CHANGELOG.md`.

## Adding New Agent Support

This section explains how to add support for new AI agents/assistants to the SpecX CLI. Use this guide as a reference when integrating new AI tools into the Spec-Driven Development workflow.

### Overview

Specify supports multiple AI agents by generating agent-specific command files and directory structures when initializing projects. Each agent has its own conventions for:

- **Command file formats** (Markdown, TOML, etc.)
- **Directory structures** (`.claude/commands/`, `.windsurf/workflows/`, etc.)
- **Command invocation patterns** (slash commands, CLI tools, etc.)
- **Argument passing conventions** (`$ARGUMENTS`, `{{args}}`, etc.)

### Current Supported Agents

| Agent | Directory | Format | CLI Tool | Description |
|-------|-----------|---------|----------|-------------|
| **Claude Code** | `.claude/commands/` | Markdown | `claude` | Anthropic's Claude Code CLI |
| **Gemini CLI** | `.gemini/commands/` | TOML | `gemini` | Google's Gemini CLI |
| **GitHub Copilot** | `.github/prompts/` | Markdown | N/A (IDE-based) | GitHub Copilot in VS Code |
| **Cursor** | `.cursor/commands/` | Markdown | `cursor-agent` | Cursor CLI |
| **Qwen Code** | `.qwen/commands/` | TOML | `qwen` | Alibaba's Qwen Code CLI |
| **opencode** | `.opencode/command/` | Markdown | `opencode` | opencode CLI |
| **Codex CLI** | `.codex/commands/` | Markdown | `codex` | Codex CLI |
| **Windsurf** | `.windsurf/workflows/` | Markdown | N/A (IDE-based) | Windsurf IDE workflows |
| **Kilo Code** | `.kilocode/rules/` | Markdown | N/A (IDE-based) | Kilo Code IDE |
| **Auggie CLI** | `.augment/rules/` | Markdown | `auggie` | Auggie CLI |
| **Roo Code** | `.roo/rules/` | Markdown | N/A (IDE-based) | Roo Code IDE |
| **CodeBuddy CLI** | `.codebuddy/commands/` | Markdown | `codebuddy` | CodeBuddy CLI |
| **Amazon Q Developer CLI** | `.amazonq/prompts/` | Markdown | `q` | Amazon Q Developer CLI |
| **Amp** | `.agents/commands/` | Markdown | `amp` | Amp CLI |

### Step-by-Step Integration Guide

Follow these steps to add a new agent (using a hypothetical new agent as an example):

#### 1. Add to AGENT_CONFIG

**IMPORTANT**: Use the actual CLI tool name as the key, not a shortened version.

Add the new agent to the `AGENT_CONFIG` dictionary in `src/specify_cli/__init__.py`. This is the **single source of truth** for all agent metadata:

```python
AGENT_CONFIG = {
    # ... existing agents ...
    "new-agent-cli": {  # Use the ACTUAL CLI tool name (what users type in terminal)
        "name": "New Agent Display Name",
        "folder": ".newagent/",  # Directory for agent files
        "install_url": "https://example.com/install",  # URL for installation docs (or None if IDE-based)
        "requires_cli": True,  # True if CLI tool required, False for IDE-based agents
    },
}
```

**Key Design Principle**: The dictionary key should match the actual executable name that users install. For example:

- ✅ Use `"cursor-agent"` because the CLI tool is literally called `cursor-agent`
- ❌ Don't use `"cursor"` as a shortcut if the tool is `cursor-agent`

This eliminates the need for special-case mappings throughout the codebase.

**Field Explanations**:

- `name`: Human-readable display name shown to users
- `folder`: Directory where agent-specific files are stored (relative to project root)
- `install_url`: Installation documentation URL (set to `None` for IDE-based agents)
- `requires_cli`: Whether the agent requires a CLI tool check during initialization

#### 2. Update CLI Help Text

Update the `--ai` parameter help text in the `init()` command to include the new agent:

```python
ai_assistant: str = typer.Option(None, "--ai", help="AI assistant to use: claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, new-agent-cli, or q"),
```

Also update any function docstrings, examples, and error messages that list available agents.

#### 3. Update README Documentation

Update the **Supported AI Agents** section in `README.md` to include the new agent:

- Add the new agent to the table with appropriate support level (Full/Partial)
- Include the agent's official website link
- Add any relevant notes about the agent's implementation
- Ensure the table formatting remains aligned and consistent

#### 4. Update Release Package Script

Modify `.github/workflows/scripts/create-release-packages.sh`:

##### Add to ALL_AGENTS array

```bash
ALL_AGENTS=(claude gemini copilot cursor-agent qwen opencode windsurf q)
```

##### Add case statement for directory structure

```bash
case $agent in
  # ... existing cases ...
  windsurf)
    mkdir -p "$base_dir/.windsurf/workflows"
    generate_commands windsurf md "\$ARGUMENTS" "$base_dir/.windsurf/workflows" "$script" ;;
esac
```

#### 4. Update GitHub Release Script

Modify `.github/workflows/scripts/create-github-release.sh` to include the new agent's packages:

```bash
gh release create "$VERSION" \
  # ... existing packages ...
  .genreleases/spec-kit-template-windsurf-sh-"$VERSION".zip \
  .genreleases/spec-kit-template-windsurf-ps-"$VERSION".zip \
  # Add new agent packages here
```

#### 5. Update Agent Context Scripts

##### Bash script (`scripts/bash/update-agent-context.sh`)

Add file variable:

```bash
WINDSURF_FILE="$REPO_ROOT/.windsurf/rules/specify-rules.md"
```

Add to case statement:

```bash
case "$AGENT_TYPE" in
  # ... existing cases ...
  windsurf) update_agent_file "$WINDSURF_FILE" "Windsurf" ;;
  "") 
    # ... existing checks ...
    [ -f "$WINDSURF_FILE" ] && update_agent_file "$WINDSURF_FILE" "Windsurf";
    # Update default creation condition
    ;;
esac
```

##### PowerShell script (`scripts/powershell/update-agent-context.ps1`)

Add file variable:

```powershell
$windsurfFile = Join-Path $repoRoot '.windsurf/rules/specify-rules.md'
```

Add to switch statement:

```powershell
switch ($AgentType) {
    # ... existing cases ...
    'windsurf' { Update-AgentFile $windsurfFile 'Windsurf' }
    '' {
        foreach ($pair in @(
            # ... existing pairs ...
            @{file=$windsurfFile; name='Windsurf'}
        )) {
            if (Test-Path $pair.file) { Update-AgentFile $pair.file $pair.name }
        }
        # Update default creation condition
    }
}
```

#### 6. Update CLI Tool Checks (Optional)

For agents that require CLI tools, add checks in the `check()` command and agent validation:

```python
# In check() command
tracker.add("windsurf", "Windsurf IDE (optional)")
windsurf_ok = check_tool_for_tracker("windsurf", "https://windsurf.com/", tracker)

# In init validation (only if CLI tool required)
elif selected_ai == "windsurf":
    if not check_tool("windsurf", "Install from: https://windsurf.com/"):
        console.print("[red]Error:[/red] Windsurf CLI is required for Windsurf projects")
        agent_tool_missing = True
```

**Note**: CLI tool checks are now handled automatically based on the `requires_cli` field in AGENT_CONFIG. No additional code changes needed in the `check()` or `init()` commands - they automatically loop through AGENT_CONFIG and check tools as needed.

## Important Design Decisions

### Using Actual CLI Tool Names as Keys

**CRITICAL**: When adding a new agent to AGENT_CONFIG, always use the **actual executable name** as the dictionary key, not a shortened or convenient version.

**Why this matters:**

- The `check_tool()` function uses `shutil.which(tool)` to find executables in the system PATH
- If the key doesn't match the actual CLI tool name, you'll need special-case mappings throughout the codebase
- This creates unnecessary complexity and maintenance burden

**Example - The Cursor Lesson:**

❌ **Wrong approach** (requires special-case mapping):

```python
AGENT_CONFIG = {
    "cursor": {  # Shorthand that doesn't match the actual tool
        "name": "Cursor",
        # ...
    }
}

# Then you need special cases everywhere:
cli_tool = agent_key
if agent_key == "cursor":
    cli_tool = "cursor-agent"  # Map to the real tool name
```

✅ **Correct approach** (no mapping needed):

```python
AGENT_CONFIG = {
    "cursor-agent": {  # Matches the actual executable name
        "name": "Cursor",
        # ...
    }
}

# No special cases needed - just use agent_key directly!
```

**Benefits of this approach:**

- Eliminates special-case logic scattered throughout the codebase
- Makes the code more maintainable and easier to understand
- Reduces the chance of bugs when adding new agents
- Tool checking "just works" without additional mappings

#### 7. Update Devcontainer files (Optional)

For agents that have VS Code extensions or require CLI installation, update the devcontainer configuration files:

##### VS Code Extension-based Agents

For agents available as VS Code extensions, add them to `.devcontainer/devcontainer.json`:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        // ... existing extensions ...
        // [New Agent Name]
        "[New Agent Extension ID]"
      ]
    }
  }
}
```

##### CLI-based Agents

For agents that require CLI tools, add installation commands to `.devcontainer/post-create.sh`:

```bash
#!/bin/bash

# Existing installations...

echo -e "\n🤖 Installing [New Agent Name] CLI..."
# run_command "npm install -g [agent-cli-package]@latest" # Example for node-based CLI
# or other installation instructions (must be non-interactive and compatible with Linux Debian "Trixie" or later)...
echo "✅ Done"

```

**Quick Tips:**

- **Extension-based agents**: Add to the `extensions` array in `devcontainer.json`
- **CLI-based agents**: Add installation scripts to `post-create.sh`
- **Hybrid agents**: May require both extension and CLI installation
- **Test thoroughly**: Ensure installations work in the devcontainer environment

## Agent Categories

### CLI-Based Agents

Require a command-line tool to be installed:

- **Claude Code**: `claude` CLI
- **Gemini CLI**: `gemini` CLI  
- **Cursor**: `cursor-agent` CLI
- **Qwen Code**: `qwen` CLI
- **opencode**: `opencode` CLI
- **Amazon Q Developer CLI**: `q` CLI
- **CodeBuddy CLI**: `codebuddy` CLI
- **Amp**: `amp` CLI

### IDE-Based Agents

Work within integrated development environments:

- **GitHub Copilot**: Built into VS Code/compatible editors
- **Windsurf**: Built into Windsurf IDE

## Command File Formats

### Markdown Format

Used by: Claude, Cursor, opencode, Windsurf, Amazon Q Developer, Amp

```markdown
---
description: "Command description"
---

Command content with {SCRIPT} and $ARGUMENTS placeholders.
```

### TOML Format

Used by: Gemini, Qwen

```toml
description = "Command description"

prompt = """
Command content with {SCRIPT} and {{args}} placeholders.
"""
```

## Directory Conventions

- **CLI agents**: Usually `.<agent-name>/commands/`
- **IDE agents**: Follow IDE-specific patterns:
  - Copilot: `.github/prompts/`
  - Cursor: `.cursor/commands/`
  - Windsurf: `.windsurf/workflows/`

## Argument Patterns

Different agents use different argument placeholders:

- **Markdown/prompt-based**: `$ARGUMENTS`
- **TOML-based**: `{{args}}`
- **Script placeholders**: `{SCRIPT}` (replaced with actual script path)
- **Agent placeholders**: `__AGENT__` (replaced with agent name)

## Testing New Agent Integration

1. **Build test**: Run package creation script locally
2. **CLI test**: Test `specx init --ai <agent>` command
3. **File generation**: Verify correct directory structure and files
4. **Command validation**: Ensure generated commands work with the agent
5. **Context update**: Test agent context update scripts

## Common Pitfalls

1. **Using shorthand keys instead of actual CLI tool names**: Always use the actual executable name as the AGENT_CONFIG key (e.g., `"cursor-agent"` not `"cursor"`). This prevents the need for special-case mappings throughout the codebase.
2. **Forgetting update scripts**: Both bash and PowerShell scripts must be updated when adding new agents.
3. **Incorrect `requires_cli` value**: Set to `True` only for agents that actually have CLI tools to check; set to `False` for IDE-based agents.
4. **Wrong argument format**: Use correct placeholder format for each agent type (`$ARGUMENTS` for Markdown, `{{args}}` for TOML).
5. **Directory naming**: Follow agent-specific conventions exactly (check existing agents for patterns).
6. **Help text inconsistency**: Update all user-facing text consistently (help strings, docstrings, README, error messages).

## Role Personas System

### Overview

The Role Personas system is a major feature that brings specialized AI agent profiles to the Spec-Driven Development workflow. Personas act as virtual team members, each contributing domain-specific expertise at appropriate phases of development.

### Architecture

**Components**:

1. **Persona Definitions**: Markdown files with YAML frontmatter in `templates/personas/`
2. **Persona Configuration**: JSON configuration in `.specify/config.json`
3. **Multi-Select UI**: Interactive persona selection during `specx init`
4. **Orchestration**: Main AI agent coordinates multiple persona sub-agents

**File Structure**:

```text
templates/
  personas/
    business-analyst.md
    solution-architect.md
    tech-lead.md
    quality-assurance.md
    devops.md
    security.md
    ux.md
    frontend-developer.md
    backend-developer.md

memory/
  personas/
    README.md              # Persona system documentation
    [copied persona files] # Selected personas copied here during init

.specify/
  config.json             # Persona configuration
```

### Persona Definition Format

Each persona is defined in a Markdown file with YAML frontmatter:

```markdown
---
id: persona-id
name: Full Persona Name
short_name: Abbreviation
role: Brief role description
contributes_to:
  - specify
  - plan
  - tasks
  - implement
  - clarify
  - analyze
  - checklist
  - constitution
phases:
  specify: ["section1", "section2"]
  plan: ["section1", "section2"]
  clarify: ["section1", "section2"]
  analyze: ["section1", "section2"]
  checklist: ["section1", "section2"]
  constitution: ["section1", "section2"]
---

# Persona Name

## Role Description
[Detailed description]

## Core Responsibilities
[Phase-specific responsibilities]

## Contribution Guidelines
[What to focus on and avoid]

## Quality Checklist
[Validation items]

[Additional domain-specific sections]
```

### Configuration Schema

The `.specify/config.json` file stores persona settings:

```json
{
  "version": "1.0",
  "personas": {
    "enabled": ["business-analyst", "solution-architect", "tech-lead"],
    "available": ["business-analyst", "solution-architect", "tech-lead", "quality-assurance", "devops", "security", "ux", "frontend-developer", "backend-developer"]
  },
  "orchestration": {
    "parallel_execution": true,
    "max_concurrent_personas": 3
  }
}
```

### Available Personas

| Persona ID | Name | Short Name | Default | Focus |
|------------|------|------------|---------|-------|
| `business-analyst` | Business Analyst | BA | ✅ | Requirements, user stories, acceptance criteria |
| `solution-architect` | Solution Architect | SA | ✅ | Technical architecture, system design, integration |
| `tech-lead` | Tech Lead | TL | ✅ | Implementation strategy, code organization, best practices |
| `quality-assurance` | Quality Assurance | QA | ❌ | Test strategies, quality gates, validation |
| `devops` | DevOps Engineer | DevOps | ❌ | Infrastructure, deployment, CI/CD, monitoring |
| `security` | Security Engineer | Security | ❌ | Security requirements, threat modeling, compliance |
| `ux` | UX Designer | UX | ❌ | User experience, accessibility, usability |
| `frontend-developer` | Frontend Developer | FE | ❌ | UI implementation, component design, state management |
| `backend-developer` | Backend Developer | BE | ❌ | API design, database design, business logic |

### Integration with Spec Commands

Personas contribute at different phases:

**`/speckit.specify`**:
- BA: User stories, functional requirements, acceptance criteria
- SA: Technical feasibility, system constraints
- Security: Security and compliance requirements
- UX: User experience and accessibility requirements
- QA: Test scenarios and quality criteria

**`/speckit.plan`**:
- SA: Architecture, technology stack, data models, API contracts
- TL: Implementation strategy, code organization, development workflow
- DevOps: Infrastructure, deployment strategy, monitoring
- Security: Security architecture, authentication/authorization
- UX: Interaction design, UI patterns, responsive design
- FE: Frontend architecture, component design, state management
- BE: Backend architecture, API design, database schema

**`/speckit.tasks`**:
- TL: Task breakdown, dependency management, estimation
- QA: Testing tasks, validation checkpoints
- FE: UI implementation tasks
- BE: API and database tasks
- DevOps: Infrastructure and CI/CD tasks

**`/speckit.implement`**:
- TL: Code review, best practices enforcement, quality gates
- QA: Test execution, quality validation, defect identification
- DevOps: Deployment validation, monitoring setup, operational readiness
- Security: Security validation, vulnerability assessment, penetration testing
- UX: UX validation, accessibility testing, usability testing
- FE: UI implementation, frontend validation, cross-browser testing
- BE: API implementation, backend validation, performance optimization

**`/speckit.clarify`**:
- BA: Functional requirements clarification, user story ambiguity resolution, acceptance criteria refinement
- SA: Technical feasibility clarification, architecture constraint validation, integration point clarification
- TL: Implementation approach clarification, technical constraint validation, best practices alignment
- QA: Test scenario clarification, edge case identification, quality criteria refinement
- DevOps: Infrastructure requirement clarification, deployment constraint validation, operational readiness
- Security: Security requirement clarification, threat model validation, compliance constraint identification
- UX: User experience clarification, accessibility requirement refinement, usability criteria validation
- FE: Frontend requirement clarification, UI specification refinement, component design validation
- BE: Backend requirement clarification, API specification refinement, data model validation

**`/speckit.analyze`**:
- BA: Requirements completeness, user story coverage, acceptance criteria validation
- SA: Architecture consistency, technical feasibility validation, integration point verification
- TL: Implementation task coverage, code organization alignment, best practices adherence
- QA: Test coverage validation, quality gate verification, edge case identification
- DevOps: Infrastructure task coverage, deployment readiness, operational considerations
- Security: Security requirement coverage, threat model validation, compliance verification
- UX: User experience requirement coverage, accessibility validation, usability criteria
- FE: Frontend task coverage, UI requirement completeness, component consistency
- BE: Backend task coverage, API requirement completeness, data model consistency

**`/speckit.checklist`**:
- BA: Requirements quality validation, acceptance criteria completeness
- SA: Architecture requirement clarity, technical constraint validation
- TL: Implementation requirement completeness, best practices validation
- QA: Test scenario coverage, quality criteria validation, edge case identification
- DevOps: Infrastructure requirement completeness, deployment criteria validation
- Security: Security requirement coverage, compliance validation, threat model completeness
- UX: User experience requirement quality, accessibility criteria validation, usability completeness
- FE: Frontend requirement clarity, UI specification completeness
- BE: Backend requirement clarity, API specification completeness

**`/speckit.constitution`**:
- BA: Requirements governance principles, acceptance criteria standards, user story quality guidelines
- SA: Architecture governance principles, technical standards, integration guidelines
- TL: Code quality principles, best practices standards, implementation guidelines
- QA: Testing standards, quality gate principles, validation guidelines
- DevOps: Infrastructure governance, deployment standards, operational principles
- Security: Security governance principles, compliance standards, threat modeling guidelines
- UX: User experience principles, accessibility standards, usability guidelines
- FE: Frontend standards, UI consistency principles, component guidelines
- BE: Backend standards, API governance principles, data integrity guidelines

### Implementation in `__init__.py`

**Key Components**:

1. **PERSONA_CONFIG Dictionary**: Defines all available personas with metadata
   ```python
   PERSONA_CONFIG = {
       "business-analyst": {
           "name": "Business Analyst (BA)",
           "description": "Requirements gathering, user stories, acceptance criteria",
           "default": True,
       },
       # ... other personas
   }
   ```

2. **multi_select_with_arrows()**: Interactive multi-select UI function
   - Arrow keys to navigate
   - Space bar to toggle selection
   - Enter to confirm
   - Shows selected count in real-time

3. **create_persona_config()**: Creates `.specify/config.json`
   - Stores enabled personas
   - Sets orchestration configuration
   - Maintains available personas list

4. **copy_persona_files()**: Copies persona definitions to project
   - Copies selected persona `.md` files
   - Copies `README.md` for documentation
   - Creates `memory/personas/` directory

5. **Integration in init() command**:
   - Persona selection after script type selection
   - Tracker step for persona setup
   - Error handling for persona configuration

### Sub-Agent Orchestration

The persona system enables sub-agent orchestration where the main AI agent acts as a coordinator:

**Orchestration Pattern**:
1. Main agent reads persona definitions from `memory/personas/`
2. Main agent reads persona configuration from `.specify/config.json`
3. For each command phase, main agent identifies relevant personas
4. Main agent invokes personas as sub-agents with appropriate context
5. Personas contribute their specialized sections in parallel
6. Main agent merges contributions into cohesive artifacts
7. Main agent resolves any conflicts between persona recommendations

**Parallel Execution**:
- Independent personas can work simultaneously
- Configurable concurrency limit (default: 3)
- Dependency-aware sequencing (e.g., BA before SA, SA before TL)
- Progress tracking for multi-persona execution
- Graceful handling of partial failures

### Customization

Users can customize personas in several ways:

1. **Edit Existing Personas**: Modify files in `memory/personas/` to add project-specific guidelines
2. **Create Custom Personas**: Add new persona definition files following the standard format
3. **Disable Personas**: Update `.specify/config.json` to change enabled personas
4. **Adjust Orchestration**: Configure parallel execution and concurrency limits

### Backward Compatibility

The persona system is designed to be fully backward compatible:

- Persona system is opt-in during `specx init`
- Existing projects without personas continue to work normally
- Commands gracefully handle missing persona configurations
- Default behavior (no personas) matches pre-persona functionality

### Testing Persona Integration

When testing the persona system:

1. **Selection UI**: Test multi-select interface with various selections
2. **File Copying**: Verify correct persona files are copied
3. **Configuration**: Check `.specify/config.json` is created correctly
4. **Command Integration**: Test persona contributions in each command phase
5. **Orchestration**: Verify parallel execution and conflict resolution
6. **Customization**: Test editing and adding custom personas
7. **Backward Compatibility**: Ensure existing projects work without personas

### Best Practices

**For Users**:
- Start with core trio (BA, SA, TL) for most projects
- Add specialized personas as needed (QA, DevOps, Security)
- Customize personas for project-specific requirements
- Review and adjust orchestration settings based on project complexity

**For Contributors**:
- Follow the standard persona definition format
- Ensure persona contributions are phase-appropriate
- Document persona expertise and guidelines clearly
- Test persona integration with multiple AI agents
- Maintain backward compatibility

## Future Considerations

When adding new agents:

- Consider the agent's native command/workflow patterns
- Ensure compatibility with the Spec-Driven Development process
- Ensure compatibility with the Role Personas system
- Document any special requirements or limitations
- Update this guide with lessons learned
- Verify the actual CLI tool name before adding to AGENT_CONFIG

When adding new personas:

- Follow the standard persona definition format
- Ensure persona contributes at appropriate phases
- Document persona expertise and quality checklists
- Test persona with multiple AI agents
- Update PERSONA_CONFIG in `__init__.py`
- Update documentation in README.md and memory/personas/README.md

---

*This documentation should be updated whenever new agents or personas are added to maintain accuracy and completeness.*
