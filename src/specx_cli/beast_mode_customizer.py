#!/usr/bin/env python3
"""
Beast Mode Customizer

Allows customization of Beast Mode chatmodes with project-specific overrides.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class BeastModeCustomizer:
    """Handles customization of Beast Mode chatmodes."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.custom_dir = project_path / ".specify" / "beast-mode-custom"
        self.custom_dir.mkdir(parents=True, exist_ok=True)
    
    def create_custom_override(self, persona_id: str, section: str, content: str) -> Path:
        """Create a custom override for a specific section of a persona."""
        override_file = self.custom_dir / f"{persona_id}.{section}.override.md"
        
        with open(override_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return override_file
    
    def get_custom_overrides(self, persona_id: str) -> Dict[str, str]:
        """Get all custom overrides for a persona."""
        overrides = {}
        
        for override_file in self.custom_dir.glob(f"{persona_id}.*.override.md"):
            parts = override_file.stem.split('.')
            if len(parts) >= 2:
                section = parts[1]
                with open(override_file, 'r', encoding='utf-8') as f:
                    overrides[section] = f.read()
        
        return overrides
    
    def apply_custom_overrides(self, template_content: str, persona_id: str, 
                              beast_mode_data: Dict[str, Any]) -> str:
        """Apply custom overrides to the template content."""
        overrides = self.get_custom_overrides(persona_id)
        
        if not overrides:
            return template_content
        
        # Apply overrides to beast_mode_data
        for section, content in overrides.items():
            if section in beast_mode_data:
                beast_mode_data[section] = content
        
        return template_content
    
    def create_project_template(self, template_name: str = "project-beast-mode.md") -> Path:
        """Create a project-specific Beast Mode template."""
        template_file = self.custom_dir / template_name
        
        if template_file.exists():
            return template_file
        
        # Create a sample template
        sample_content = """---
# Project-Specific Beast Mode Template
# This template overrides the default Beast Mode templates
---

# {name} — Project Beast Mode

## Mission
{mission_statement}

## Project-Specific Guidelines

### Technology Stack
- Frontend: [Your frontend tech]
- Backend: [Your backend tech]
- Database: [Your database]
- Infrastructure: [Your infrastructure]

### Project Conventions
- Code style: [Your style guide]
- Testing: [Your testing approach]
- Documentation: [Your docs standards]

### Team Workflows
- Review process: [Your review process]
- Deployment: [Your deployment process]
- Communication: [Your communication channels]

## Standard Beast Mode Sections

{standard_content}

## Project-Specific Sections

### Custom Section 1
[Your custom content]

### Custom Section 2
[Your custom content]
"""
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        return template_file
    
    def list_customizations(self) -> Dict[str, List[str]]:
        """List all customizations by persona."""
        customizations = {}
        
        for file in self.custom_dir.glob("*.override.md"):
            parts = file.stem.split('.')
            if len(parts) >= 2:
                persona_id = parts[0]
                section = parts[1]
                
                if persona_id not in customizations:
                    customizations[persona_id] = []
                
                customizations[persona_id].append(section)
        
        return customizations
    
    def export_customizations(self, output_path: Optional[Path] = None) -> Path:
        """Export all customizations to a file."""
        if not output_path:
            output_path = self.project_path / "beast-mode-customizations.json"
        
        export_data = {
            "project": str(self.project_path),
            "customizations": {}
        }
        
        for persona_id, sections in self.list_customizations().items():
            export_data["customizations"][persona_id] = {}
            for section in sections:
                override_file = self.custom_dir / f"{persona_id}.{section}.override.md"
                with open(override_file, 'r', encoding='utf-8') as f:
                    export_data["customizations"][persona_id][section] = f.read()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        return output_path
    
    def import_customizations(self, import_path: Path) -> int:
        """Import customizations from a file."""
        with open(import_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        count = 0
        for persona_id, sections in import_data.get("customizations", {}).items():
            for section, content in sections.items():
                self.create_custom_override(persona_id, section, content)
                count += 1
        
        return count


def enhance_transform_with_customization(
    original_transform_func,
    project_path: Path,
    persona_id: str,
    beast_mode_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Enhance the transform function with customization support."""
    customizer = BeastModeCustomizer(project_path)
    overrides = customizer.get_custom_overrides(persona_id)
    
    # Apply overrides to beast_mode_data
    for section, content in overrides.items():
        if section in beast_mode_data:
            beast_mode_data[section] = content
        else:
            # Add as new section
            beast_mode_data[f"custom_{section}"] = content
    
    # Check for project template
    project_template = customizer.custom_dir / "project-beast-mode.md"
    if project_template.exists():
        with open(project_template, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Extract standard content placeholder
        if "{standard_content}" in template_content:
            # This would be filled with the standard Beast Mode content
            beast_mode_data["has_project_template"] = True
            beast_mode_data["project_template_path"] = str(project_template)
    
    return beast_mode_data
