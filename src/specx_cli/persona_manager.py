#!/usr/bin/env python3
"""
Beast Mode Persona Manager

Handles dynamic persona switching, context preservation, and performance tracking.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class PersonaContext:
    """Context for a specific persona session."""
    persona_id: str
    activated_at: str
    deactivated_at: Optional[str] = None
    phase: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


@dataclass
class PersonaPerformance:
    """Performance metrics for a persona."""
    persona_id: str
    total_sessions: int = 0
    total_duration_seconds: float = 0.0
    phases_completed: Dict[str, int] = field(default_factory=dict)
    artifacts_created: int = 0
    error_count: int = 0
    success_rate: float = 100.0
    last_active: Optional[str] = None


class PersonaManager:
    """Manages Beast Mode personas with context preservation and performance tracking."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.state_file = project_path / ".specify" / "persona_state.json"
        self.history_file = project_path / ".specify" / "persona_history.json"
        self.performance_file = project_path / ".specify" / "persona_performance.json"
        self.current_context: Optional[PersonaContext] = None
        self._ensure_files()
        self._load_state()
    
    def _ensure_files(self):
        """Ensure all required files exist."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.state_file.exists():
            self._save_state()
        
        if not self.history_file.exists():
            self._save_history([])
        
        if not self.performance_file.exists():
            self._save_performance({})
    
    def _load_state(self):
        """Load current persona state."""
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                if data.get("current_persona"):
                    self.current_context = PersonaContext(**data["current_persona"])
        except Exception:
            self.current_context = None
    
    def _save_state(self):
        """Save current persona state."""
        state = {
            "current_persona": asdict(self.current_context) if self.current_context else None,
            "updated_at": datetime.now().isoformat()
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _load_history(self) -> List[Dict]:
        """Load persona session history."""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_history(self, history: List[Dict]):
        """Save persona session history."""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def _load_performance(self) -> Dict[str, PersonaPerformance]:
        """Load performance metrics."""
        try:
            with open(self.performance_file, 'r') as f:
                data = json.load(f)
                return {
                    pid: PersonaPerformance(**pdata)
                    for pid, pdata in data.items()
                }
        except Exception:
            return {}
    
    def _save_performance(self, performance: Dict[str, Any]):
        """Save performance metrics."""
        data = {}
        for pid, perf in performance.items():
            if isinstance(perf, PersonaPerformance):
                data[pid] = asdict(perf)
            else:
                data[pid] = perf
        
        with open(self.performance_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def activate_persona(self, persona_id: str, phase: Optional[str] = None, 
                        ai_assistant: Optional[str] = None) -> Dict[str, Any]:
        """Activate a Beast Mode persona."""
        # Deactivate current persona if any
        if self.current_context:
            self.deactivate_persona(ai_assistant=ai_assistant)
        
        # Create new context
        self.current_context = PersonaContext(
            persona_id=persona_id,
            activated_at=datetime.now().isoformat(),
            phase=phase
        )
        
        self._save_state()
        
        # Update agent context file if AI assistant is known
        if ai_assistant:
            self._update_agent_context(ai_assistant, persona_id, phase)
        
        return {
            "status": "activated",
            "persona": persona_id,
            "phase": phase,
            "activated_at": self.current_context.activated_at
        }
    
    def _update_agent_context(self, ai_assistant: str, persona_id: Optional[str], 
                             phase: Optional[str] = None):
        """Update agent-specific context file."""
        try:
            from .agent_persona_context import create_agent_context_file
            create_agent_context_file(self.project_path, ai_assistant, persona_id, phase)
        except ImportError:
            pass  # Agent context module not available
    
    def deactivate_persona(self, ai_assistant: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Deactivate current persona and update metrics."""
        if not self.current_context:
            return None
        
        # Mark deactivation time
        self.current_context.deactivated_at = datetime.now().isoformat()
        
        # Calculate session duration
        start = datetime.fromisoformat(self.current_context.activated_at)
        end = datetime.fromisoformat(self.current_context.deactivated_at)
        duration = (end - start).total_seconds()
        
        # Update history
        history = self._load_history()
        history.append(asdict(self.current_context))
        self._save_history(history)
        
        # Update performance metrics
        self._update_performance(self.current_context, duration)
        
        result = {
            "status": "deactivated",
            "persona": self.current_context.persona_id,
            "duration_seconds": duration,
            "artifacts": len(self.current_context.artifacts)
        }
        
        # Clear current context
        self.current_context = None
        self._save_state()
        
        return result
    
    def _update_performance(self, context: PersonaContext, duration: float):
        """Update performance metrics for a persona."""
        performance = self._load_performance()
        
        if context.persona_id not in performance:
            performance[context.persona_id] = PersonaPerformance(persona_id=context.persona_id)
        
        perf = performance[context.persona_id]
        if isinstance(perf, dict):
            perf = PersonaPerformance(**perf)
        
        # Update metrics
        perf.total_sessions += 1
        perf.total_duration_seconds += duration
        perf.artifacts_created += len(context.artifacts)
        perf.last_active = context.deactivated_at
        
        if context.phase:
            if context.phase not in perf.phases_completed:
                perf.phases_completed[context.phase] = 0
            perf.phases_completed[context.phase] += 1
        
        # Update success rate based on notes
        if any("error" in note.lower() for note in context.notes):
            perf.error_count += 1
        
        if perf.total_sessions > 0:
            perf.success_rate = ((perf.total_sessions - perf.error_count) / perf.total_sessions) * 100
        
        performance[context.persona_id] = perf
        self._save_performance(performance)
    
    def switch_persona(self, new_persona_id: str, phase: Optional[str] = None,
                      ai_assistant: Optional[str] = None) -> Dict[str, Any]:
        """Switch from current persona to a new one."""
        previous = None
        if self.current_context:
            previous = self.current_context.persona_id
            self.deactivate_persona(ai_assistant=ai_assistant)
        
        result = self.activate_persona(new_persona_id, phase, ai_assistant=ai_assistant)
        result["previous_persona"] = previous
        
        return result
    
    def get_current_persona(self) -> Optional[str]:
        """Get the currently active persona."""
        return self.current_context.persona_id if self.current_context else None
    
    def add_artifact(self, artifact_path: str):
        """Add an artifact to the current persona context."""
        if self.current_context:
            self.current_context.artifacts.append(artifact_path)
            self._save_state()
    
    def add_note(self, note: str):
        """Add a note to the current persona context."""
        if self.current_context:
            self.current_context.notes.append(f"[{datetime.now().isoformat()}] {note}")
            self._save_state()
    
    def update_phase(self, phase: str):
        """Update the current phase for the active persona."""
        if self.current_context:
            self.current_context.phase = phase
            self._save_state()
    
    def get_performance_report(self, persona_id: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for personas."""
        performance = self._load_performance()
        
        if persona_id:
            perf = performance.get(persona_id)
            if perf:
                if isinstance(perf, dict):
                    perf = PersonaPerformance(**perf)
                return self._format_performance(perf)
            return {"error": f"No performance data for persona: {persona_id}"}
        
        # Return all personas performance
        report = {}
        for pid, perf in performance.items():
            if isinstance(perf, dict):
                perf = PersonaPerformance(**perf)
            report[pid] = self._format_performance(perf)
        
        return report
    
    def _format_performance(self, perf: PersonaPerformance) -> Dict[str, Any]:
        """Format performance metrics for display."""
        avg_duration = perf.total_duration_seconds / perf.total_sessions if perf.total_sessions > 0 else 0
        
        return {
            "persona_id": perf.persona_id,
            "total_sessions": perf.total_sessions,
            "total_duration_minutes": round(perf.total_duration_seconds / 60, 2),
            "average_duration_minutes": round(avg_duration / 60, 2),
            "phases_completed": perf.phases_completed,
            "artifacts_created": perf.artifacts_created,
            "error_count": perf.error_count,
            "success_rate": round(perf.success_rate, 2),
            "last_active": perf.last_active
        }
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent persona session history."""
        history = self._load_history()
        
        # Sort by activation time (newest first)
        history.sort(key=lambda x: x['activated_at'], reverse=True)
        
        # Return limited results
        return history[:limit]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context."""
        if not self.current_context:
            return {"status": "no_active_persona"}
        
        start = datetime.fromisoformat(self.current_context.activated_at)
        duration = (datetime.now() - start).total_seconds()
        
        return {
            "status": "active",
            "persona": self.current_context.persona_id,
            "phase": self.current_context.phase,
            "duration_seconds": round(duration, 2),
            "artifacts": self.current_context.artifacts,
            "notes": self.current_context.notes[-5:],  # Last 5 notes
            "activated_at": self.current_context.activated_at
        }
    
    def export_metrics(self, output_path: Optional[Path] = None) -> Path:
        """Export all metrics to a file."""
        if not output_path:
            output_path = self.project_path / "persona_metrics_export.json"
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "current_state": self.get_context_summary(),
            "performance": self.get_performance_report(),
            "recent_history": self.get_session_history(limit=50)
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_path


def create_persona_command_file(project_path: Path, ai_assistant: str) -> bool:
    """Create persona switching command file for the AI agent."""
    from . import CHATMODE_CONFIG
    
    chatmode_cfg = CHATMODE_CONFIG.get(ai_assistant)
    if not chatmode_cfg:
        return False
    
    # Create persona switching command
    command_dir = project_path / chatmode_cfg["dir"]
    command_dir.mkdir(parents=True, exist_ok=True)
    
    command_file = command_dir / f"persona-switch{chatmode_cfg['ext']}"
    
    if chatmode_cfg["format"] == "toml-beast":
        content = '''[metadata]
name = "Persona Switcher"
description = "Switch between Beast Mode personas dynamically"

[commands]
switch = "specx persona switch {persona_id}"
status = "specx persona status"
history = "specx persona history"
performance = "specx persona performance"

[instructions]
prompt = """
Use the persona switching commands to change between different Beast Mode personas.

Available commands:
- Switch persona: specx persona switch [persona-id]
- Check status: specx persona status
- View history: specx persona history
- Performance report: specx persona performance

Example: specx persona switch business-analyst
"""'''
    else:
        # Markdown format
        content = '''---
description: "Switch between Beast Mode personas dynamically"
---

# Persona Switcher

Use these commands to switch between different Beast Mode personas:

## Commands

### Switch Persona
```bash
specx persona switch [persona-id]
```

Example:
```bash
specx persona switch business-analyst
specx persona switch solution-architect --phase plan
```

### Check Current Status
```bash
specx persona status
```

### View Session History
```bash
specx persona history
specx persona history --limit 20
```

### Performance Report
```bash
specx persona performance
specx persona performance business-analyst
```

### Export Metrics
```bash
specx persona export-metrics
```

## Available Personas

Check your `.specify/config.json` for enabled personas.'''
    
    with open(command_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True
