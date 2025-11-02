# SpecX Bot 🤖

**AI-Powered Spec-Driven Development with Role-Based Personas**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **Note:** SpecX Bot is a fork of [GitHub Spec Kit](https://github.com/github/spec-kit) with enhanced role-based persona capabilities and multi-agent orchestration features.

---

## 🌟 What is SpecX Bot?

**SpecX Bot** is an advanced CLI tool that supercharges Spec-Driven Development (SDD) by introducing **role-based AI personas** that work together as a virtual team. Think of it as having a Business Analyst, Solution Architect, Tech Lead, and other specialists collaborating on your project—all powered by AI.

### Key Enhancements Over Original Spec Kit

- **🎭 Role-Based Personas**: Choose from 9 specialized AI personas (BA, SA, TL, QA, DevOps, Security, UX, Frontend, Backend)
- **🔀 Multi-Agent Orchestration**: Personas work in parallel, each contributing their expertise
- **🎯 Development Strategy Selection**: Choose between Role-Based (multi-persona) or Traditional (single-agent) approaches
- **🏷️ Custom Project Namespaces**: Avoid command conflicts with project-specific command names
- **⚡ Enhanced Workflow**: Streamlined initialization with arrow-key navigation

---

## 📋 Table of Contents

- [What is Spec-Driven Development?](#what-is-spec-driven-development)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Development Strategy](#development-strategy)
- [Project Namespace](#project-namespace)
- [Role Personas](#role-personas)
- [Commands](#commands)
- [Supported AI Agents](#supported-ai-agents)
- [Credits](#credits)
- [License](#license)

---

## 💡 What is Spec-Driven Development?

Spec-Driven Development (SDD) is a methodology that treats specifications as **executable artifacts** rather than static documents. Instead of writing specs that get outdated, SDD creates living specifications that guide the entire development process.

### The SDD Workflow

```
1. Specify   → Create detailed feature specifications
2. Plan      → Generate implementation plans with architecture
3. Tasks     → Break down into actionable development tasks
4. Implement → Execute with AI guidance and validation
```

For a deep dive into SDD principles, see the [original Spec Kit documentation](https://github.com/github/spec-kit).

---

## 🚀 Installation

### Prerequisites

- **Python 3.11+**
- **uv** (Python package manager)
- **Git**
- **AI Coding Agent** (Claude Code, Cursor, GitHub Copilot, etc.)

### Install SpecX Bot

```bash
# Install from GitHub
uv tool install specx-cli --from git+https://github.com/hjk1995/specx-bot.git

# Verify installation
specx --version
```

### Update SpecX Bot

```bash
uv tool install --force specx-cli --from git+https://github.com/hjk1995/specx-bot.git
```

---

## ⚡ Quick Start

### Initialize a New Project

```bash
# Interactive mode (recommended)
specx init myproject

# With AI agent specified
specx init myproject --ai cursor-agent

# Initialize in current directory
specx init --here
```

### Interactive Setup Flow

When you run `specx init`, you'll be guided through:

1. **AI Assistant Selection** - Choose your preferred AI agent
2. **Script Type** - Select bash (sh) or PowerShell (ps)
3. **Development Strategy** - Role-Based or Traditional
4. **Project Namespace** (Role-Based only) - Custom command prefix
5. **Persona Selection** (Role-Based only) - Choose your virtual team

### Your First Specification

After initialization, create your first feature spec:

```bash
# Navigate to your project
cd myproject

# Create a specification (using your AI agent)
# Use your chosen namespace (default: speckit)
/speckit-specify Create a user authentication system with login, signup, and password reset

# Or if you chose a custom namespace like "myapp":
/myapp-specify Create a user authentication system with login, signup, and password reset
```

---

## 🎯 Development Strategy

SpecX Bot offers two development approaches to match your project needs:

### 1. Role-Based Development (Recommended)

Use specialized AI personas that work together as virtual team members. Each persona contributes domain-specific expertise at appropriate phases.

**Best for:**
- Complex projects requiring comprehensive planning
- Team collaboration and knowledge sharing
- Projects with multiple stakeholders
- Long-term maintainability and documentation

### 2. Traditional Development

Single AI agent handles all development tasks in a straightforward, unified approach.

**Best for:**
- Quick prototypes and MVPs
- Simple, single-purpose projects
- Solo development with minimal overhead
- Learning and experimentation

### Interactive Selection

```
Development Strategy
Choose your development approach:

> Role-Based (Recommended) - Multi-persona collaborative development with specialized expertise
  Traditional - Single AI agent handles all tasks, simpler and faster

Select development strategy (or press Enter for Role-Based):
```

### Key Differences

| Feature | Role-Based | Traditional |
|---------|------------|-------------|
| **Namespace Selection** | ✅ Custom namespace prompt | ❌ Uses default "speckit" |
| **Persona Selection** | ✅ Multi-select personas | ❌ No personas |
| **Command Prefix** | Custom (e.g., `/myapp-specify`) | Default (`/speckit-specify`) |
| **Setup Steps** | Strategy → Namespace → Personas | Strategy only |
| **Complexity** | Moderate (3 extra steps) | Minimal (no extra steps) |

---

## 🎯 Project Namespace (Role-Based Strategy Only)

When using the **Role-Based** development strategy, SpecX Bot allows you to customize the namespace for your project commands. This lets you create project-specific commands that match your workflow and avoid conflicts with other projects.

**Note:** Traditional strategy uses the default "speckit" namespace and skips this step for simplicity.

### Configuration

```
Project Namespace Configuration
Enter a namespace for your project commands (e.g., 'myapp', 'project', 'api')
Commands will be: /<namespace>-specify, /<namespace>-plan, /<namespace>-tasks, etc.
Press Enter for default: 'speckit'

Project namespace: myapp
✓ Project namespace set to: myapp
Your commands: /myapp-specify, /myapp-plan, /myapp-tasks, /myapp-implement, etc.
```

### Validation Rules

- Must be a single word (no spaces)
- Lowercase letters, numbers, and hyphens only
- Must start with a letter
- Default is "speckit" if no input provided

### Your Commands

- `/<namespace>-specify` - Create feature specifications
- `/<namespace>-plan` - Generate implementation plans
- `/<namespace>-tasks` - Break down into tasks
- `/<namespace>-implement` - Execute implementation
- `/<namespace>-clarify` - Clarify ambiguities
- `/<namespace>-analyze` - Analyze artifacts
- `/<namespace>-checklist` - Generate quality checklists
- `/<namespace>-constitution` - Manage project governance

### How it Works

- The namespace is stored in `.specify/config.json` for reference
- During initialization, command files are generated with namespace-prefixed filenames (e.g., `myapp-specify.md`)
- Command content uses the namespace in slash commands (e.g., `/myapp.specify`)
- Commands appear in your AI agent with the custom namespace (e.g., `/myapp-specify`, `/myapp-plan`)
- Default namespace "speckit" uses original filenames for backward compatibility
- This ensures no conflicts between multiple projects using SpecX Bot

### Example

```bash
# With namespace "myapp"
.cursor/commands/
  ├── myapp-specify.md      # Command: /myapp.specify
  ├── myapp-plan.md         # Command: /myapp.plan
  ├── myapp-tasks.md        # Command: /myapp.tasks
  └── myapp-implement.md    # Command: /myapp.implement
```

---

## 👥 Role Personas (Role-Based Strategy Only)

When using the **Role-Based** development strategy, SpecX Bot brings specialized AI agent profiles to your project. During project initialization, you can select which personas to enable, and they'll contribute their specialized knowledge throughout the spec-driven development process.

### What are Role Personas?

Role personas are specialized AI profiles that act as virtual team members, each focusing on specific aspects of software development. When enabled, your AI agent orchestrates these personas (similar to Cursor's Composer), allowing them to contribute their expertise in parallel.

### Available Personas

#### Core Personas (Recommended for All Projects)

| Persona | Focus | Key Contributions |
|---------|-------|-------------------|
| **Business Analyst (BA)** | Requirements & User Stories | User scenarios, functional requirements, acceptance criteria, success metrics |
| **Solution Architect (SA)** | Technical Architecture | System design, technology stack selection, integration patterns, data models |
| **Tech Lead (TL)** | Implementation Strategy | Code organization, task breakdown, development workflow, best practices |

#### Specialized Personas (Add as Needed)

| Persona | Focus | Key Contributions |
|---------|-------|-------------------|
| **Quality Assurance (QA)** | Testing & Quality | Test strategies, quality gates, edge cases, validation criteria |
| **DevOps Engineer** | Infrastructure & Deployment | CI/CD pipelines, deployment strategies, monitoring, scalability |
| **Security Engineer** | Security & Compliance | Security requirements, threat modeling, authentication, compliance |
| **UX Designer** | User Experience | User flows, accessibility, usability, interaction design |
| **Frontend Developer** | Frontend Implementation | UI components, state management, responsive design, frontend architecture |
| **Backend Developer** | Backend Implementation | API design, database schema, business logic, backend architecture |

### Persona Selection

During `specx init` (Role-Based mode), you'll see:

```
Select role personas for your project:

> [✓] Business Analyst (BA) - Requirements gathering, user stories, acceptance criteria
  [✓] Solution Architect (SA) - Technical architecture, system design, integration
  [✓] Tech Lead (TL) - Implementation strategy, code organization, best practices
  [ ] Quality Assurance (QA) - Test strategies, quality gates, validation
  [ ] DevOps Engineer - Infrastructure, deployment, CI/CD, monitoring
  [ ] Security Engineer - Security requirements, threat modeling, compliance
  [ ] UX Designer - User experience, accessibility, usability
  [ ] Frontend Developer - UI implementation, component design, state management
  [ ] Backend Developer - API design, database design, business logic

Use ↑↓ to navigate, Space to select/deselect, Enter to confirm
Selected: 3 personas
```

### Persona Contributions by Phase

> **Note:** Commands shown use the default `speckit` namespace. If you chose a custom namespace (e.g., `myapp`), replace `speckit` with your namespace.

#### `/<namespace>-specify` - Specification Phase

- **BA**: User stories, functional requirements, acceptance criteria
- **SA**: Technical feasibility, system constraints
- **Security**: Security and compliance requirements
- **UX**: User experience and accessibility requirements
- **QA**: Test scenarios and quality criteria

#### `/<namespace>-plan` - Planning Phase

- **SA**: Architecture, technology stack, data models, API contracts
- **TL**: Implementation strategy, code organization, development workflow
- **DevOps**: Infrastructure, deployment strategy, monitoring
- **Security**: Security architecture, authentication/authorization
- **UX**: Interaction design, UI patterns, responsive design
- **Frontend**: Frontend architecture, component design, state management
- **Backend**: Backend architecture, API design, database schema

#### `/<namespace>-tasks` - Task Breakdown Phase

- **TL**: Task breakdown, dependency management, estimation
- **QA**: Testing tasks, validation checkpoints
- **Frontend**: UI implementation tasks
- **Backend**: API and database tasks
- **DevOps**: Infrastructure and CI/CD tasks

#### `/<namespace>-implement` - Implementation Phase

- **TL**: Code review, best practices enforcement, quality gates
- **QA**: Test execution, quality validation, defect identification
- **DevOps**: Deployment validation, monitoring setup, operational readiness
- **Security**: Security validation, vulnerability assessment
- **UX**: UX validation, accessibility testing, usability testing
- **Frontend**: UI implementation, frontend validation
- **Backend**: API implementation, backend validation

#### `/<namespace>-clarify` - Clarification Phase

- **BA**: Functional requirements clarification, acceptance criteria refinement
- **SA**: Technical feasibility clarification, architecture validation
- **TL**: Implementation approach clarification, best practices alignment
- **QA**: Test scenario clarification, edge case identification
- **DevOps**: Infrastructure requirement clarification, deployment validation
- **Security**: Security requirement clarification, threat model validation
- **UX**: User experience clarification, accessibility refinement
- **Frontend**: Frontend requirement clarification, UI specification refinement
- **Backend**: Backend requirement clarification, API specification refinement

#### `/<namespace>-analyze` - Analysis Phase

- **BA**: Requirements completeness, acceptance criteria validation
- **SA**: Architecture consistency, technical feasibility validation
- **TL**: Implementation task coverage, code organization alignment
- **QA**: Test coverage validation, quality gate verification
- **DevOps**: Infrastructure task coverage, deployment readiness
- **Security**: Security requirement coverage, threat model validation
- **UX**: User experience requirement coverage, accessibility validation
- **Frontend**: Frontend task coverage, UI requirement completeness
- **Backend**: Backend task coverage, API requirement completeness

#### `/<namespace>-checklist` - Checklist Generation Phase

- **BA**: Requirements quality validation, acceptance criteria completeness
- **SA**: Architecture requirement clarity, technical constraint validation
- **TL**: Implementation requirement completeness, best practices validation
- **QA**: Test scenario coverage, quality criteria validation
- **DevOps**: Infrastructure requirement completeness, deployment criteria validation
- **Security**: Security requirement coverage, compliance validation
- **UX**: User experience requirement quality, accessibility criteria validation
- **Frontend**: Frontend requirement clarity, UI specification completeness
- **Backend**: Backend requirement clarity, API specification completeness

#### `/<namespace>-constitution` - Governance Phase

- **BA**: Requirements governance principles, acceptance criteria standards
- **SA**: Architecture governance principles, technical standards
- **TL**: Code quality principles, best practices standards
- **QA**: Testing standards, quality gate principles
- **DevOps**: Infrastructure governance, deployment standards
- **Security**: Security governance principles, compliance standards
- **UX**: User experience principles, accessibility standards
- **Frontend**: Frontend standards, UI consistency principles
- **Backend**: Backend standards, API governance principles

### Sub-Agent Orchestration

SpecX Bot's persona system enables powerful sub-agent orchestration:

1. **Main AI agent** reads persona definitions from `memory/personas/`
2. **Configuration** is loaded from `.specify/config.json`
3. **For each command phase**, relevant personas are identified
4. **Personas are invoked** as sub-agents with appropriate context
5. **Parallel execution** allows independent personas to work simultaneously
6. **Main agent merges** contributions into cohesive artifacts
7. **Conflict resolution** ensures consistent recommendations

### Customization

You can customize personas in several ways:

1. **Edit Existing Personas**: Modify files in `memory/personas/` to add project-specific guidelines
2. **Create Custom Personas**: Add new persona definition files following the standard format
3. **Disable Personas**: Update `.specify/config.json` to change enabled personas
4. **Adjust Orchestration**: Configure parallel execution and concurrency limits

### Beast Mode Chatmodes

SpecX Bot automatically transforms your selected personas into comprehensive "Beast Mode" chatmodes for your AI agent. These chatmodes provide:

- **Autonomous Operation**: Complete independence to finish all deliverables
- **Comprehensive Workflows**: Phase-by-phase execution guides with time estimates
- **Error Handling**: Built-in recovery procedures for common scenarios
- **Success Metrics**: Trackable performance indicators
- **Quality Gates**: Validation checkpoints throughout the process

#### Generated Chatmode Files

Based on your AI agent selection, Beast Mode files are created in:

| AI Agent | Directory | File Format |
|----------|-----------|-------------|
| GitHub Copilot | `.github/chatmodes/` | `[persona].chatmode.md` |
| Claude | `.claude/personas/` | `[persona].md` |
| Cursor | `.cursor/personas/` | `[persona].md` |
| Windsurf | `.windsurf/personas/` | `[persona].md` |
| Gemini | `.gemini/personas/` | `[persona].toml` |

#### Using Beast Mode

1. **Activation**: Reference the chatmode file in your AI agent
   - Copilot: Create new chat participant with chatmode file
   - Claude: `@.claude/personas/business-analyst.md`
   - Cursor: `@.cursor/personas/business-analyst.md`

2. **Switching**: Change personas during development
   ```
   /persona:business-analyst    # Activate BA Beast Mode
   /persona:solution-architect  # Switch to SA Beast Mode
   ```

3. **Workflow**: Let Beast Mode handle autonomous execution
   - Personas work independently until completion
   - Validate outputs at checkpoints
   - Request approval when ready

For detailed information, see [Beast Mode Documentation](docs/beast-mode.md).

---

## 📝 Commands

SpecX Bot provides a comprehensive set of commands for the entire development lifecycle:

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `specx init` | Initialize a new project | `specx init myproject --ai cursor-agent` |
| `specx check` | Verify prerequisites | `specx check` |
| `specx regenerate-chatmodes` | Regenerate Beast Mode chatmodes | `specx regenerate-chatmodes --force` |
| `specx update-constitution` | Update chatmodes with project constitution | `specx update-constitution` |

### Persona Management Commands (Beast Mode)

| Command | Description | Example |
|---------|-------------|---------|
| `specx persona switch` | Switch to a different persona | `specx persona switch business-analyst --phase specify` |
| `specx persona status` | Show current persona status | `specx persona status` |
| `specx persona regenerate` | Regenerate persona chatmodes | `specx persona regenerate --force` |

### Spec Commands (via AI Agent)

These commands are executed through your AI agent (e.g., in Cursor, Claude Code):

> **Note:** Replace `<namespace>` with your chosen namespace (default: `speckit`, or custom like `myapp`).

| Command | Description | When to Use |
|---------|-------------|-------------|
| `/<namespace>-specify` | Create feature specification | Start of new feature development |
| `/<namespace>-plan` | Generate implementation plan | After specification is complete |
| `/<namespace>-tasks` | Break down into tasks | After plan is validated |
| `/<namespace>-implement` | Execute implementation | When ready to code |
| `/<namespace>-clarify` | Clarify ambiguities | When spec needs refinement |
| `/<namespace>-analyze` | Analyze cross-artifact consistency | Quality assurance check |
| `/<namespace>-checklist` | Generate quality checklist | Before implementation |
| `/<namespace>-constitution` | Manage project governance | Establish project principles |

### Command Workflow

```
1. /<namespace>-specify "Add user authentication"
   ↓
2. /<namespace>-plan
   ↓
3. /<namespace>-tasks
   ↓
4. /<namespace>-implement
```

**Example with default namespace:**
```
1. /speckit-specify "Add user authentication"
2. /speckit-plan
3. /speckit-tasks
4. /speckit-implement
```

For detailed step-by-step instructions, see the [Spec-Driven Development guide](./spec-driven.md).

---

## 🤖 Supported AI Agents

SpecX Bot works with all major AI coding assistants:

| AI Agent | Support Level | Installation | Notes |
|----------|---------------|--------------|-------|
| **Cursor** | ✅ Full | [cursor.sh](https://cursor.sh/) | Excellent sub-agent support |
| **Claude Code** | ✅ Full | [claude.ai/code](https://claude.ai/code) | Native orchestration |
| **GitHub Copilot** | ✅ Full | Built into VS Code | IDE-based |
| **Windsurf** | ✅ Full | [windsurf.ai](https://windsurf.ai/) | IDE-based workflows |
| **Gemini CLI** | ✅ Full | [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | CLI tool |
| **Qwen Code** | ✅ Full | [qwen.ai](https://qwen.ai/) | CLI tool |
| **Amazon Q Developer** | ✅ Full | [aws.amazon.com/q](https://aws.amazon.com/q) | CLI tool |
| **Others** | ✅ Partial | Various | May have limited sub-agent support |

### Selecting Your AI Agent

During `specx init`, you can specify your preferred agent:

```bash
specx init myproject --ai cursor-agent
specx init myproject --ai claude
specx init myproject --ai copilot
```

Or choose interactively during initialization.

---

## 🙏 Credits

**SpecX Bot** is a fork of the excellent [GitHub Spec Kit](https://github.com/github/spec-kit) project.

### Original Spec Kit

- **Repository**: [github.com/github/spec-kit](https://github.com/github/spec-kit)
- **License**: MIT
- **Maintainers**: 
- Den Delimarsky ([@localden](https://github.com/localden))
- John Lam ([@jflam](https://github.com/jflam))
- **Contributors**: 61+ contributors to the original project

### SpecX Bot Enhancements

SpecX Bot builds upon Spec Kit's foundation with:

- **Role-Based Persona System**: Multi-agent orchestration with specialized AI personas
- **Development Strategy Selection**: Choose between Role-Based and Traditional approaches
- **Custom Project Namespaces**: Avoid command conflicts across projects
- **Enhanced CLI Experience**: Arrow-key navigation and streamlined workflows
- **Extended Documentation**: Comprehensive guides for persona-based development

**Thank you to the Spec Kit team and community for creating the foundation that makes SpecX Bot possible!**

---

## 📄 License

This project is licensed under the terms of the MIT open source license, consistent with the original [GitHub Spec Kit](https://github.com/github/spec-kit).

See the [LICENSE](./LICENSE) file for full details.

---

## 💬 Support

For support, please open a GitHub issue at [github.com/hjk1995/specx-bot/issues](https://github.com/hjk1995/specx-bot/issues).

We welcome:
- 🐛 Bug reports
- ✨ Feature requests
- 💡 Questions about using SpecX Bot
- 🤝 Contributions and pull requests

---

## 🚀 What's Next?

1. **Install SpecX Bot**: `uv tool install specx-cli --from git+https://github.com/hjk1995/specx-bot.git`
2. **Initialize Your Project**: `specx init myproject`
3. **Choose Your Strategy**: Role-Based or Traditional
4. **Select Your Personas**: Build your virtual team
5. **Start Developing**: `/speckit-specify "Your first feature"` (or `/<your-namespace>-specify`)

**Happy Spec-Driven Development with SpecX Bot!** 🎉

---

<div align="center">

**[Installation](#installation)** • **[Quick Start](#quick-start)** • **[Commands](#commands)** • **[Personas](#role-personas)** • **[Support](#support)**

Made with ❤️ by the SpecX Bot community • Powered by [GitHub Spec Kit](https://github.com/github/spec-kit)

</div>
