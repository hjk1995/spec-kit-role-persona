---
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

1a. **Load Persona Configuration** (if available):
   - Check if `.specify/config.json` exists
   - If exists, read the `personas.enabled` list
   - Load persona definitions from `memory/personas/` for enabled personas
   - Identify which personas contribute to the `constitution` phase:
     - **Business Analyst (BA)**: Requirements governance principles, acceptance criteria standards, user story quality guidelines
     - **Solution Architect (SA)**: Architecture governance principles, technical standards, integration guidelines
     - **Tech Lead (TL)**: Code quality principles, best practices standards, implementation guidelines
     - **Quality Assurance (QA)**: Testing standards, quality gate principles, validation guidelines
     - **DevOps**: Infrastructure governance, deployment standards, operational principles
     - **Security**: Security governance principles, compliance standards, threat modeling guidelines
     - **UX**: User experience principles, accessibility standards, usability guidelines
     - **Frontend Developer (FE)**: Frontend standards, UI consistency principles, component guidelines
     - **Backend Developer (BE)**: Backend standards, API governance principles, data integrity guidelines
   - If no persona configuration exists, proceed with standard single-agent workflow

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

   **Orchestrate Persona Contributions** (if personas enabled):
   
   If personas are enabled, coordinate their specialized principle contributions in parallel where possible:
   
   a. **Business Analyst (BA)** - Requirements governance:
      - Contribute principles for requirements quality and completeness
      - Define acceptance criteria standards
      - Establish user story quality guidelines
      - Specify success criteria measurability requirements
   
   b. **Solution Architect (SA)** - Architecture governance:
      - Contribute principles for architecture consistency and quality
      - Define technical standards and constraints
      - Establish integration guidelines
      - Specify system design principles
   
   c. **Tech Lead (TL)** - Code quality governance:
      - Contribute principles for code quality and maintainability
      - Define best practices standards
      - Establish implementation guidelines
      - Specify technical debt management principles
   
   d. **Quality Assurance (QA)** (if enabled):
      - Contribute principles for testing and quality assurance
      - Define quality gate standards
      - Establish validation guidelines
      - Specify test coverage requirements
   
   e. **DevOps** (if enabled):
      - Contribute principles for infrastructure and deployment
      - Define deployment standards
      - Establish operational principles
      - Specify CI/CD and monitoring requirements
   
   f. **Security** (if enabled):
      - Contribute principles for security and compliance
      - Define security standards
      - Establish threat modeling guidelines
      - Specify compliance requirements
   
   g. **UX** (if enabled):
      - Contribute principles for user experience
      - Define accessibility standards
      - Establish usability guidelines
      - Specify interaction design principles
   
   h. **Frontend Developer (FE)** (if enabled):
      - Contribute principles for frontend development
      - Define UI consistency standards
      - Establish component guidelines
      - Specify state management principles
   
   i. **Backend Developer (BE)** (if enabled):
      - Contribute principles for backend development
      - Define API governance standards
      - Establish data integrity guidelines
      - Specify business logic principles
   
   **Orchestration Pattern**:
   - Each persona contributes principles in their domain of expertise
   - Integrate all contributions into a cohesive constitution
   - Resolve any conflicts between persona principles (prioritize by project needs)
   - Ensure consistency across all principle sections
   - Validate that principles are testable and enforceable
   
   **Attribution**: Add subtle attribution markers for persona contributions:
   ```markdown
   <!-- Constitution principles contributed by: BA, SA, TL, QA, DevOps, Security, UX, FE, BE -->
   ```

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `/memory/constitution.md` (overwrite).

8. **Update Beast Mode Chatmodes** (if personas are enabled):
   - After writing the constitution, **automatically run** this command to inject the constitution into chatmode files:
   ```bash
   specx update-constitution
   ```
   - This ensures all AI agent personas include the project-specific governance principles
   - The constitution will be appended to each persona chatmode file
   - This makes the governance principles immediately available when using Beast Mode personas
   - **IMPORTANT**: Always run this command after updating the constitution. Don't ask the user - just do it.
   - Report the result (e.g., "Updated 3 chatmode files with project constitution")

9. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Confirmation that Beast Mode chatmodes were updated (if applicable)
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `/memory/constitution.md` file.
