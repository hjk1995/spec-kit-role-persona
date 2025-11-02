#!/usr/bin/env python3
"""
Agent Persona Context

Creates agent-specific context files that make the current persona visible to AI agents.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json


def create_agent_context_file(project_path: Path, ai_assistant: str, persona_id: Optional[str], 
                              phase: Optional[str] = None) -> bool:
    """
    Create/update an agent-specific context file that tells the AI which persona is active.
    
    This allows AI agents to automatically know which Beast Mode persona they should use.
    """
    
    # Define where to put the context file for each agent
    context_paths = {
        "copilot": ".github/CURRENT_PERSONA.md",
        "claude": ".claude/CURRENT_PERSONA.md",
        "cursor-agent": ".cursor/CURRENT_PERSONA.md",
        "windsurf": ".windsurf/CURRENT_PERSONA.md",
        "gemini": ".gemini/CURRENT_PERSONA.md",
        "qwen": ".qwen/CURRENT_PERSONA.md",
        "opencode": ".opencode/CURRENT_PERSONA.md",
        "codex": ".codex/CURRENT_PERSONA.md",
        "kilocode": ".kilocode/CURRENT_PERSONA.md",
        "auggie": ".augment/CURRENT_PERSONA.md",
        "codebuddy": ".codebuddy/CURRENT_PERSONA.md",
        "roo": ".roo/CURRENT_PERSONA.md",
        "q": ".amazonq/CURRENT_PERSONA.md",
        "amp": ".agents/CURRENT_PERSONA.md",
    }
    
    context_file_path = context_paths.get(ai_assistant)
    if not context_file_path:
        return False
    
    context_file = project_path / context_file_path
    context_file.parent.mkdir(parents=True, exist_ok=True)
    
    if persona_id is None:
        # No active persona - remove context file
        if context_file.exists():
            context_file.unlink()
        return True
    
    # Create context file with persona information
    content = f"""# Current Active Persona

**Active Persona:** {persona_id}
**Phase:** {phase or 'Not specified'}

## Instructions for AI Agent

You are currently operating in **{persona_id.replace('-', ' ').title()}** Beast Mode.

### Activate the Persona

To adopt this persona's behavior, reference the appropriate persona file:

"""
    
    # Add agent-specific instructions
    if ai_assistant == "copilot":
        chatmode_file = f".github/chatmodes/{persona_id}.chatmode.md"
        content += f"""#### For Copilot:
1. Create a new chat participant
2. Select the chatmode file: `{chatmode_file}`
3. The persona is now active

Or simply include this in your prompt:
```
@{chatmode_file}
```
"""
    else:
        persona_file = context_paths.get(ai_assistant, "").replace("CURRENT_PERSONA.md", f"personas/{persona_id}.md")
        content += f"""#### For {ai_assistant.replace('-', ' ').title()}:
Reference the persona file in your chat:
```
@{persona_file}
```

This will activate {persona_id.replace('-', ' ').title()} Beast Mode with full autonomy.
"""
    
    content += f"""
## Current Phase

You are working on the **{phase or 'unspecified'}** phase.

## How to Switch Personas

To switch to a different persona, use:
```bash
specx persona switch <persona-id>
```

Available personas can be found in `.specify/config.json` under `personas.enabled`.

## Check Status

To see current persona status:
```bash
specx persona status
```

---
*This file is automatically updated by SpecX CLI when you switch personas*
"""
    
    with open(context_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def create_vscode_settings_persona(project_path: Path, persona_id: Optional[str]) -> bool:
    """
    Update VS Code settings to recommend the current persona chatmode.
    """
    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    
    # Load existing settings or create new
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    else:
        settings = {}
    
    # Update chat prompt recommendations
    if persona_id:
        if "chat.promptFilesRecommendations" not in settings:
            settings["chat.promptFilesRecommendations"] = {}
        
        # Add current persona chatmode
        settings["chat.promptFilesRecommendations"][f"persona.{persona_id}"] = True
    
    # Write updated settings
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)
    
    return True

