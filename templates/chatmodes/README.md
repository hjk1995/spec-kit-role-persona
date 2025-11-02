# Beast Mode Chatmode Templates

This directory contains templates for transforming role personas into comprehensive Beast Mode chatmodes for various AI agents.

## Template Files

### beast-mode-copilot.md
GitHub Copilot chatmode format with:
- YAML frontmatter with description and tools
- Comprehensive Beast Mode sections
- User approval blocks

### beast-mode-markdown.md
Markdown format for Claude, Cursor, Windsurf, and other agents:
- YAML frontmatter with role and mode
- Structured Beast Mode instructions
- Phase-specific workflows

### beast-mode-toml.toml
TOML format for Gemini and Qwen:
- Metadata section
- Mission and principles
- Multi-line instruction prompts

## Template Variables

All templates use placeholder variables that are replaced during generation:

### Identity Variables
- `{persona_id}` - Unique identifier (e.g., "business-analyst")
- `{name}` / `{full_name}` - Full persona name
- `{short_name}` - Abbreviation (BA, SA, TL, etc.)
- `{role}` - Role description

### Mission Variables
- `{mission}` - Brief mission statement
- `{mission_statement}` - Detailed mission
- `{role_emphasis}` - Primary role emphasis
- `{deliverable_emphasis}` - Key deliverables

### Workflow Variables
- `{phase_1_name}`, `{phase_2_name}`, `{phase_3_name}` - Phase names
- `{phase_1_duration}`, etc. - Time estimates
- `{phase_1_steps}`, etc. - Step descriptions
- `{phase_1_validation}`, etc. - Validation criteria

### Input/Output Variables
- `{input_analysis}` - Input requirements
- `{must_have_inputs}` - Required inputs
- `{output_specifications}` - Deliverable specs
- `{primary_deliverables}` - Main outputs

### Metric Variables
- `{metric_category_1}`, `{metric_category_2}` - Metric categories
- `{quality_target}` - Quality percentage
- `{time_target}` - Time limit
- `{artifact_count}` - Number of artifacts

### Error Handling Variables
- `{missing_info_description}` - Missing info scenario
- `{conflict_description}` - Conflict scenario
- `{constraint_description}` - Constraint violation

## Customization Guide

### Adding New Variables

1. Add variable to template with `{variable_name}` syntax
2. Update `transform_to_beast_mode()` function in `__init__.py`
3. Provide default value in transformation logic

### Creating Agent-Specific Templates

1. Copy existing template closest to your format
2. Adapt structure to agent requirements
3. Name as `beast-mode-{agent}.{ext}`
4. Update `CHATMODE_CONFIG` in `__init__.py`

### Modifying Sections

Each section can be customized:
- Add new sections with `## Section Name`
- Include variables with `{variable}` syntax
- Use markdown formatting for structure

## Best Practices

1. **Maintain Consistency**: Keep similar structure across formats
2. **Provide Defaults**: Always have fallback values for variables
3. **Test Thoroughly**: Verify generated output with actual agents
4. **Document Changes**: Update this README when modifying templates

## Example Usage

The transformation process:

1. **Load Persona**:
   ```yaml
   id: business-analyst
   name: Business Analyst
   short_name: BA
   role: Requirements and user story expert
   ```

2. **Apply Template**:
   Variables are substituted in the template

3. **Generate Output**:
   Beast Mode chatmode file created in agent directory

## Validation

After generation, validate:
- All variables replaced (no `{variable}` remaining)
- YAML/TOML syntax is valid
- Markdown formatting is correct
- File works with target AI agent
