---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This command MUST run only after `/specx-tasks` has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The project constitution (`/memory/constitution.md`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `/specx-analyze`.

## Execution Steps

### 1. Initialize Analysis Context

Run `{SCRIPT}` once from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS. Derive absolute paths:

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md

Abort with an error message if any required file is missing (instruct the user to run missing prerequisite command).
For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

### 1a. Load Persona Configuration (if available)

- Check if `.specify/config.json` exists
- If exists, read the `personas.enabled` list
- Load persona definitions from `memory/personas/` for enabled personas
- Identify which personas contribute to the `analyze` phase:
  - **Business Analyst (BA)**: Requirements completeness, user story coverage, acceptance criteria validation
  - **Solution Architect (SA)**: Architecture consistency, technical feasibility validation, integration point verification
  - **Tech Lead (TL)**: Implementation task coverage, code organization alignment, best practices adherence
  - **Quality Assurance (QA)**: Test coverage validation, quality gate verification, edge case identification
  - **DevOps**: Infrastructure task coverage, deployment readiness, operational considerations
  - **Security**: Security requirement coverage, threat model validation, compliance verification
  - **UX**: User experience requirement coverage, accessibility validation, usability criteria
  - **Frontend Developer (FE)**: Frontend task coverage, UI requirement completeness, component consistency
  - **Backend Developer (BE)**: Backend task coverage, API requirement completeness, data model consistency
- If no persona configuration exists, proceed with standard single-agent workflow

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**

- Overview/Context
- Functional Requirements
- Non-Functional Requirements
- User Stories
- Edge Cases (if present)

**From plan.md:**

- Architecture/stack choices
- Data Model references
- Phases
- Technical constraints

**From tasks.md:**

- Task IDs
- Descriptions
- Phase grouping
- Parallel markers [P]
- Referenced file paths

**From constitution:**

- Load `/memory/constitution.md` for principle validation

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" → `user-can-upload-file`)
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Task coverage mapping**: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases)
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements

### 4. Detection Passes (Token-Efficient Analysis)

Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.

**Orchestrate Persona Contributions** (if personas enabled):

If personas are enabled, coordinate their specialized analysis in parallel where possible:

a. **Business Analyst (BA)** - Requirements analysis:
   - Validate requirements completeness and clarity
   - Check user story coverage and acceptance criteria quality
   - Identify missing or ambiguous functional requirements
   - Verify success criteria are measurable and testable

b. **Solution Architect (SA)** - Architecture consistency:
   - Validate technical architecture consistency across artifacts
   - Check integration points are properly specified
   - Verify technical constraints are reflected in tasks
   - Identify architectural gaps or contradictions

c. **Tech Lead (TL)** - Implementation coverage:
   - Validate task coverage for all requirements
   - Check code organization and structure alignment
   - Verify best practices are reflected in tasks
   - Identify missing implementation tasks

d. **Quality Assurance (QA)** (if enabled):
   - Validate test coverage for all requirements
   - Check quality gates are properly defined
   - Verify edge cases are identified and covered
   - Identify missing test scenarios

e. **DevOps** (if enabled):
   - Validate infrastructure and deployment task coverage
   - Check operational readiness considerations
   - Verify CI/CD and monitoring requirements
   - Identify missing infrastructure tasks

f. **Security** (if enabled):
   - Validate security requirement coverage
   - Check threat model alignment
   - Verify compliance requirements are addressed
   - Identify security gaps or vulnerabilities

g. **UX** (if enabled):
   - Validate user experience requirement coverage
   - Check accessibility requirements
   - Verify usability criteria are measurable
   - Identify UX gaps or inconsistencies

h. **Frontend Developer (FE)** (if enabled):
   - Validate frontend task coverage
   - Check UI requirement completeness
   - Verify component consistency
   - Identify missing frontend implementation tasks

i. **Backend Developer (BE)** (if enabled):
   - Validate backend task coverage
   - Check API requirement completeness
   - Verify data model consistency
   - Identify missing backend implementation tasks

**Orchestration Pattern**:
- All personas analyze artifacts in parallel based on their expertise
- Each persona contributes findings in their domain
- Integrate all findings into a unified analysis report
- Resolve any conflicts between persona findings (prioritize by severity)
- Ensure consistency across all analysis sections

**Attribution**: Add subtle attribution markers for persona contributions in the analysis report:
```markdown
<!-- Analysis contributed by: BA, SA, TL, QA, DevOps, Security, UX, FE, BE -->
```

#### A. Duplication Detection

- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection

- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.)

#### C. Underspecification

- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Tasks referencing files or components not defined in spec/plan

#### D. Constitution Alignment

- Any requirement or plan element conflicting with a MUST principle
- Missing mandated sections or quality gates from constitution

#### E. Coverage Gaps

- Requirements with zero associated tasks
- Tasks with no mapped requirement/story
- Non-functional requirements not reflected in tasks (e.g., performance, security)

#### F. Inconsistency

- Terminology drift (same concept named differently across files)
- Data entities referenced in plan but absent in spec (or vice versa)
- Task ordering contradictions (e.g., integration tasks before foundational setup tasks without dependency note)
- Conflicting requirements (e.g., one requires Next.js while other specifies Vue)

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates constitution MUST, missing core spec artifact, or requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Compact Analysis Report

Output a Markdown report (no file writes) with the following structure:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

(Add one row per finding; generate stable IDs prefixed by category initial.)

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**

- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `/specx-implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /specx-specify with refinement", "Run /specx-plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'"

### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Token-efficient output**: Limit findings table to 50 rows; summarize overflow
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

### Analysis Guidelines

- **NEVER modify files** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero issues gracefully** (emit success report with coverage statistics)

## Context

{ARGS}
