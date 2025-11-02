# Changelog

All notable changes to SpecX Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### 🎉 Major Release: SpecX Bot

This release represents a complete rebranding and major enhancement of the original GitHub Spec Kit project.

### Breaking Changes

- **Project Renamed**: `spec-kit` → `specx-bot`
- **Package Renamed**: `specify-cli` → `specx-cli`
- **Module Renamed**: `specify_cli` → `specx_cli`
- **Executable Renamed**: `specify-role` → `specx`
- **Command Prefix Changed**: `/speckit.*` → `/specx-*`
- **Repository URL**: Now at `https://github.com/hjk1995/spec-kit-role-persona`

### Migration Guide

**Old Installation:**
```bash
uv tool install specify-cli --from git+https://github.com/hjk1995/spec-kit-role-persona.git
specify-role init myproject
```

**New Installation:**
```bash
uv tool install specx-cli --from git+https://github.com/hjk1995/spec-kit-role-persona.git
specx init myproject
```

**Command Changes:**
- `/speckit.specify` → `/specx-specify`
- `/speckit.plan` → `/specx-plan`
- `/speckit.tasks` → `/specx-tasks`
- `/speckit.implement` → `/specx-implement`
- `/speckit.clarify` → `/specx-clarify`
- `/speckit.analyze` → `/specx-analyze`
- `/speckit.checklist` → `/specx-checklist`
- `/speckit.constitution` → `/specx-constitution`

### Added

- **Development Strategy Selection**: Users can now choose between Role-Based and Traditional development approaches during `specx init`
  - **Role-Based (Recommended)**: Use specialized AI personas for comprehensive, team-oriented development
  - **Dynamic Command Display**: Next Steps and Enhancement Commands now display with the selected project namespace
  - **Traditional**: Single AI agent handles all tasks for simpler, faster setup
  - **Arrow-based selection UI** for intuitive navigation (↑/↓ keys, Enter to select)
  - Interactive prompt with clear descriptions and use-case guidance
  - Strategy stored in `.specify/config.json` for reference
  - Persona system only activates when Role-Based strategy is selected
  - **Namespace selection only appears for Role-Based strategy** (Traditional uses default "speckit")
  - Default is Role-Based for new projects, maintaining backward compatibility
  - Non-interactive mode defaults to Role-Based strategy

- **Project Namespace**: Users can now set a custom namespace for project commands during `specx init` (Role-Based strategy only)
  - Interactive prompt asks for a single-word, lowercase namespace identifier
  - Default namespace is "speckit" if no input provided
  - Validates namespace format (lowercase, alphanumeric with hyphens, starts with letter)
  - Stored in `.specify/config.json` for reference by AI agents
  - Commands become: `/<namespace>-specify`, `/<namespace>-plan`, `/<namespace>-tasks`, `/<namespace>-implement`, etc.
  - Example: namespace "myapp" creates commands `/myapp-specify`, `/myapp-plan`, etc.
  - Helps avoid command conflicts between multiple projects

- **Role Personas System**: Major new feature that brings specialized AI agent profiles to the Spec-Driven Development workflow
  - **9 Predefined Personas**: Business Analyst (BA), Solution Architect (SA), Tech Lead (TL), Quality Assurance (QA), DevOps Engineer, Security Engineer, UX Designer, Frontend Developer (FE), Backend Developer (BE)
  - **Interactive Multi-Select UI**: During `specx init`, users can select which personas to enable using arrow keys and space bar
  - **Sub-Agent Orchestration**: Main AI agent coordinates multiple persona sub-agents working in parallel (similar to Cursor's Composer)
  - **Phase-Specific Contributions**: Each persona contributes specialized expertise at appropriate phases:
    - **specify**: BA, SA, Security, UX, QA
    - **plan**: SA, TL, DevOps, Security, UX, FE, BE
    - **tasks**: TL, QA, FE, BE, DevOps
    - **implement**: TL, QA, DevOps, Security, UX, FE, BE
    - **clarify**: BA, SA, TL, QA, DevOps, Security, UX, FE, BE
    - **analyze**: BA, SA, TL, QA, DevOps, Security, UX, FE, BE
    - **checklist**: BA, SA, TL, QA, DevOps, Security, UX, FE, BE
    - **constitution**: BA, SA, TL, QA, DevOps, Security, UX, FE, BE
  - **Default Selection**: Core trio (BA, SA, TL) selected by default for all projects
  - **Parallel Execution**: Configurable parallel persona execution with concurrency limits
  - **Backward Compatibility**: Persona system is opt-in; existing projects continue to work without personas

### Changed

- Enhanced `specx init` command with development strategy and persona selection steps
- Updated project initialization workflow to include strategy selection, namespace configuration, and persona setup
- Added strategy, namespace, and persona configuration tracking to initialization progress display
- Updated all command templates (`specify.md`, `plan.md`, `tasks.md`, `implement.md`, `clarify.md`, `analyze.md`, `checklist.md`, `constitution.md`) with persona orchestration instructions
- Updated all artifact templates (`spec-template.md`, `plan-template.md`, `tasks-template.md`) with persona contribution markers
- Improved CLI user experience with arrow-key navigation for all selections
- Streamlined Traditional mode with fewer prompts and faster setup

### Fixed

- **Command Generation and Namespace**: Fixed issue where commands were not being installed or listed properly
  - Added `generate_agent_commands()` function that creates agent-specific command files from templates during initialization
  - Generates commands for all supported agents (Claude, Cursor, Copilot, Gemini, Qwen, etc.) with correct format (.md or .toml)
  - **Command filenames now ALWAYS include namespace prefix** (e.g., `speckit-specify.md` or `myapp-specify.md`)
  - **Command content uses namespace in slash commands** (e.g., `/speckit-specify` or `/myapp-specify`)
  - Removed special-case logic that was creating unprefixed filenames for default namespace
  - Replaces `{SCRIPT}` placeholders with appropriate script commands (bash or PowerShell)
  - Replaces `$ARGUMENTS` with agent-specific argument formats (`$ARGUMENTS` for Markdown, `{{args}}` for TOML)
  - Falls back to updating existing commands if they're already present (from release packages)
  - Commands now properly install and appear in AI agent command lists with the correct namespace
- **Documentation Accuracy**: Updated README.md to reflect actual command naming
  - Changed all command examples from `/specx-*` to `/<namespace>-*` format
  - Added notes explaining namespace replacement (default: `speckit`, custom: user's choice)
  - Updated command reference table to show `/<namespace>-specify` instead of `/specx-specify`
  - Fixed comparison table to show correct default command prefix (`/speckit-specify` instead of `/specify`)
  - Added concrete examples showing both default (`/speckit-specify`) and custom (`/myapp-specify`) namespaces

- **Persona File Copying**: Fixed issue where persona files were not being copied during `specx init`
  - Changed source path from package templates to downloaded project templates directory
  - Added warning messages when persona files are not found
  - Persona files now correctly copied from `templates/personas/` to `memory/personas/`
  - Fixed "same file" error when copying README.md that already exists in destination
  - Added smart detection to skip copying files that are already in place (from git clone)

- **No Releases Fallback**: Added automatic fallback to clone from main branch when no GitHub releases are available
  - CLI now clones directly from the repository when releases are not found (404 error)
  - Useful for development and forked repositories without published releases
  - Maintains same functionality as release-based downloads
  - Fixed metadata compatibility to ensure cloned repositories work with existing extraction logic
  - Added separate file copying logic for git-cloned repositories vs zip extraction

### Documentation

- **Complete README Rewrite**: New comprehensive README with SpecX Bot branding
  - Added prominent credit to original [GitHub Spec Kit](https://github.com/github/spec-kit) project
  - Documented all new features (Development Strategy, Project Namespace, Role Personas)
  - Added comparison tables for strategies and personas
  - Included detailed persona contribution guides for each command phase
  - Added migration guide from old Spec Kit commands
  - Enhanced quick start guide with interactive setup flow
  - Added visual examples and code snippets throughout

- **AGENTS.md Updates**: Enhanced agent integration documentation
  - Added Role Personas System section
  - Documented persona architecture and orchestration patterns
  - Added guidelines for creating custom personas
  - Included persona integration testing checklist

- **New Documentation Files**:
  - `memory/personas/README.md` - Persona system documentation
  - Individual persona definition files for all 9 personas

### Credits

SpecX Bot is a fork of [GitHub Spec Kit](https://github.com/github/spec-kit) with enhanced role-based persona capabilities.

**Original Spec Kit:**
- Repository: https://github.com/github/spec-kit
- License: MIT
- Maintainers: Den Delimarsky ([@localden](https://github.com/localden)), John Lam ([@jflam](https://github.com/jflam))
- Contributors: 61+ contributors

**SpecX Bot Enhancements:**
- Role-Based Persona System with multi-agent orchestration
- Development Strategy Selection (Role-Based vs Traditional)
- Custom Project Namespaces
- Enhanced CLI experience with arrow-key navigation
- Extended documentation and guides

Thank you to the Spec Kit team and community for creating the foundation that makes SpecX Bot possible!

---

## [0.1.0] - Previous Versions

For changelog entries prior to the SpecX Bot rebranding, please refer to the original [GitHub Spec Kit changelog](https://github.com/github/spec-kit/blob/main/CHANGELOG.md).

---

## Version History

- **1.0.0** - SpecX Bot initial release (rebranded from Spec Kit with persona system)
- **0.1.0** - Original Spec Kit versions (see [original changelog](https://github.com/github/spec-kit/blob/main/CHANGELOG.md))
