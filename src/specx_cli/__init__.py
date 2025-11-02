#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
#     "rich",
#     "platformdirs",
#     "readchar",
#     "httpx",
#     "pyyaml",
# ]
# ///
"""
SpecX CLI - AI-powered Spec-Driven Development with Role Personas

SpecX Bot is a fork of GitHub Spec Kit with enhanced multi-agent orchestration.

Usage:
    uvx specx-cli.py init <project-name>
    uvx specx-cli.py init .
    uvx specx-cli.py init --here

Or install globally:
    uv tool install specx-cli --from git+https://github.com/hjk1995/specx-bot.git
    specx init <project-name>
    specx init .
    specx init --here

Credits:
    Forked from GitHub Spec Kit: https://github.com/github/spec-kit
"""

import os
import subprocess
import sys
import zipfile
import tempfile
import shutil
import shlex
import json
from pathlib import Path
from typing import Optional, Tuple

import typer
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from typer.core import TyperGroup

# For cross-platform keyboard input
import readchar
import ssl
import truststore

ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client = httpx.Client(verify=ssl_context)

def _github_token(cli_token: str | None = None) -> str | None:
    """Return sanitized GitHub token (cli arg takes precedence) or None."""
    return ((cli_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()) or None

def _github_auth_headers(cli_token: str | None = None) -> dict:
    """Return Authorization header dict only when a non-empty token exists."""
    token = _github_token(cli_token)
    return {"Authorization": f"Bearer {token}"} if token else {}

# Agent configuration with name, folder, install URL, and CLI tool requirement
AGENT_CONFIG = {
    "copilot": {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "install_url": None,  # IDE-based, no CLI check needed
        "requires_cli": False,
    },
    "claude": {
        "name": "Claude Code",
        "folder": ".claude/",
        "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
        "requires_cli": True,
    },
    "gemini": {
        "name": "Gemini CLI",
        "folder": ".gemini/",
        "install_url": "https://github.com/google-gemini/gemini-cli",
        "requires_cli": True,
    },
    "cursor-agent": {
        "name": "Cursor",
        "folder": ".cursor/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "qwen": {
        "name": "Qwen Code",
        "folder": ".qwen/",
        "install_url": "https://github.com/QwenLM/qwen-code",
        "requires_cli": True,
    },
    "opencode": {
        "name": "opencode",
        "folder": ".opencode/",
        "install_url": "https://opencode.ai",
        "requires_cli": True,
    },
    "codex": {
        "name": "Codex CLI",
        "folder": ".codex/",
        "install_url": "https://github.com/openai/codex",
        "requires_cli": True,
    },
    "windsurf": {
        "name": "Windsurf",
        "folder": ".windsurf/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "kilocode": {
        "name": "Kilo Code",
        "folder": ".kilocode/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "auggie": {
        "name": "Auggie CLI",
        "folder": ".augment/",
        "install_url": "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
        "requires_cli": True,
    },
    "codebuddy": {
        "name": "CodeBuddy",
        "folder": ".codebuddy/",
        "install_url": "https://www.codebuddy.ai/cli",
        "requires_cli": True,
    },
    "roo": {
        "name": "Roo Code",
        "folder": ".roo/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "q": {
        "name": "Amazon Q Developer CLI",
        "folder": ".amazonq/",
        "install_url": "https://aws.amazon.com/developer/learning/q-developer-cli/",
        "requires_cli": True,
    },
    "amp": {
        "name": "Amp",
        "folder": ".agents/",
        "install_url": "https://ampcode.com/manual#install",
        "requires_cli": True,
    },
}

SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)", "ps": "PowerShell"}

# Persona configuration
PERSONA_CONFIG = {
    "business-analyst": {
        "name": "Business Analyst (BA)",
        "description": "Requirements gathering, user stories, acceptance criteria",
        "default": True,
    },
    "solution-architect": {
        "name": "Solution Architect (SA)",
        "description": "Technical architecture, system design, integration patterns",
        "default": True,
    },
    "tech-lead": {
        "name": "Tech Lead (TL)",
        "description": "Implementation strategy, code structure, best practices",
        "default": True,
    },
    "quality-assurance": {
        "name": "Quality Assurance (QA)",
        "description": "Test strategies, quality gates, validation criteria",
        "default": False,
    },
    "devops": {
        "name": "DevOps Engineer",
        "description": "Infrastructure, deployment, CI/CD, monitoring",
        "default": False,
    },
    "security": {
        "name": "Security Engineer",
        "description": "Security requirements, threat modeling, compliance",
        "default": False,
    },
    "ux": {
        "name": "UX Designer",
        "description": "User experience, accessibility, usability",
        "default": False,
    },
    "frontend-developer": {
        "name": "Frontend Developer (FE)",
        "description": "UI implementation, component design, state management",
        "default": False,
    },
    "backend-developer": {
        "name": "Backend Developer (BE)",
        "description": "API design, database design, business logic",
        "default": False,
    },
}

# Beast Mode chatmode configuration
CHATMODE_CONFIG = {
    "copilot": {
        "dir": ".github/chatmodes", 
        "ext": ".chatmode.md", 
        "format": "copilot-beast"
    },
    "claude": {
        "dir": ".claude/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "gemini": {
        "dir": ".gemini/personas", 
        "ext": ".toml", 
        "format": "toml-beast"
    },
    "cursor-agent": {
        "dir": ".cursor/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "qwen": {
        "dir": ".qwen/personas", 
        "ext": ".toml", 
        "format": "toml-beast"
    },
    "opencode": {
        "dir": ".opencode/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "codex": {
        "dir": ".codex/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "windsurf": {
        "dir": ".windsurf/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "kilocode": {
        "dir": ".kilocode/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "auggie": {
        "dir": ".augment/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "codebuddy": {
        "dir": ".codebuddy/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "roo": {
        "dir": ".roo/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "q": {
        "dir": ".amazonq/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
    "amp": {
        "dir": ".agents/personas", 
        "ext": ".md", 
        "format": "markdown-beast"
    },
}

CLAUDE_LOCAL_PATH = Path.home() / ".claude" / "local" / "claude"

BANNER = """
███████╗██████╗ ███████╗ ██████╗██╗  ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝╚██╗██╔╝
███████╗██████╔╝█████╗  ██║      ╚███╔╝ 
╚════██║██╔═══╝ ██╔══╝  ██║      ██╔██╗ 
███████║██║     ███████╗╚██████╗██╔╝ ██╗
╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝
"""

TAGLINE = "SpecX Bot - AI-Powered Spec-Driven Development with Role Personas"
class StepTracker:
    """Track and render hierarchical steps without emojis, similar to Claude Code tree output.
    Supports live auto-refresh via an attached refresh callback.
    """
    def __init__(self, title: str):
        self.title = title
        self.steps = []  # list of dicts: {key, label, status, detail}
        self.status_order = {"pending": 0, "running": 1, "done": 2, "error": 3, "skipped": 4}
        self._refresh_cb = None  # callable to trigger UI refresh

    def attach_refresh(self, cb):
        self._refresh_cb = cb

    def add(self, key: str, label: str):
        if key not in [s["key"] for s in self.steps]:
            self.steps.append({"key": key, "label": label, "status": "pending", "detail": ""})
            self._maybe_refresh()

    def start(self, key: str, detail: str = ""):
        self._update(key, status="running", detail=detail)

    def complete(self, key: str, detail: str = ""):
        self._update(key, status="done", detail=detail)

    def error(self, key: str, detail: str = ""):
        self._update(key, status="error", detail=detail)

    def skip(self, key: str, detail: str = ""):
        self._update(key, status="skipped", detail=detail)

    def _update(self, key: str, status: str, detail: str):
        for s in self.steps:
            if s["key"] == key:
                s["status"] = status
                if detail:
                    s["detail"] = detail
                self._maybe_refresh()
                return

        self.steps.append({"key": key, "label": key, "status": status, "detail": detail})
        self._maybe_refresh()

    def _maybe_refresh(self):
        if self._refresh_cb:
            try:
                self._refresh_cb()
            except Exception:
                pass

    def render(self):
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""

            status = step["status"]
            if status == "done":
                symbol = "[green]●[/green]"
            elif status == "pending":
                symbol = "[green dim]○[/green dim]"
            elif status == "running":
                symbol = "[cyan]○[/cyan]"
            elif status == "error":
                symbol = "[red]●[/red]"
            elif status == "skipped":
                symbol = "[yellow]○[/yellow]"
            else:
                symbol = " "

            if status == "pending":
                # Entire line light gray (pending)
                if detail_text:
                    line = f"{symbol} [bright_black]{label} ({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [bright_black]{label}[/bright_black]"
            else:
                # Label white, detail (if any) light gray in parentheses
                if detail_text:
                    line = f"{symbol} [white]{label}[/white] [bright_black]({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [white]{label}[/white]"

            tree.add(line)
        return tree

def get_key():
    """Get a single keypress in a cross-platform way using readchar."""
    key = readchar.readkey()

    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return 'up'
    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return 'down'

    if key == readchar.key.ENTER:
        return 'enter'

    if key == readchar.key.ESC:
        return 'escape'

    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt

    return key

def select_with_arrows(options: dict, prompt_text: str = "Select an option", default_key: str = None) -> str:
    """
    Interactive selection using arrow keys with Rich Live display.
    
    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_key: Default option key to start with
        
    Returns:
        Selected option key
    """
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row("▶", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row("", "[dim]Use ↑/↓ to navigate, Enter to select, Esc to cancel[/dim]")

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == 'up':
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == 'down':
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == 'enter':
                        selected_key = option_keys[selected_index]
                        break
                    elif key == 'escape':
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_key

def multi_select_with_arrows(options: dict, prompt_text: str = "Select options", defaults: list = None) -> list:
    """
    Interactive multi-selection using arrow keys and space bar with Rich Live display.
    
    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        defaults: List of default selected option keys
        
    Returns:
        List of selected option keys
    """
    option_keys = list(options.keys())
    selected_index = 0
    selected_items = set(defaults if defaults else [])
    confirmed = False

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            cursor = "▶" if i == selected_index else " "
            checkbox = "[X]" if key in selected_items else "[ ]"
            name = options[key]
            
            if i == selected_index:
                table.add_row(cursor, f"[cyan]{checkbox}[/cyan]", f"[cyan]{name}[/cyan]")
            else:
                table.add_row(cursor, f"[dim]{checkbox}[/dim]", f"[dim]{name}[/dim]")

        table.add_row("", "", "")
        table.add_row("", "", "[dim]↑/↓: Navigate | Space: Toggle | Enter: Confirm | Esc: Cancel[/dim]")

        selected_count = len(selected_items)
        subtitle = f"[dim]{selected_count} persona{'s' if selected_count != 1 else ''} selected[/dim]"

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            subtitle=subtitle,
            border_style="cyan",
            padding=(1, 2)
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_index, selected_items, confirmed
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == 'up':
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == 'down':
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == ' ':  # Space bar to toggle
                        current_key = option_keys[selected_index]
                        if current_key in selected_items:
                            selected_items.remove(current_key)
                        else:
                            selected_items.add(current_key)
                    elif key == 'enter':
                        confirmed = True
                        break
                    elif key == 'escape':
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if not confirmed:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return list(selected_items)

console = Console()

def get_development_strategy() -> str:
    """
    Ask user to choose between persona-based or traditional development strategy using arrow keys.
    
    Returns:
        'persona' or 'traditional'
    """
    console.print("\n[bold cyan]Development Strategy[/bold cyan]")
    console.print("Choose your development approach:\n")
    
    strategies = {
        "persona": "Role-Based (Recommended) - Multi-persona collaborative development with specialized expertise",
        "traditional": "Traditional - Single AI agent handles all tasks, simpler and faster"
    }
    
    strategy_choice = select_with_arrows(
        strategies,
        "Select development strategy (or press Enter for Role-Based):",
        default_key="persona"
    )
    
    if strategy_choice == "persona":
        console.print("[green]✓[/green] Using [bold]Role-Based[/bold] development strategy")
        console.print("[dim]   • Specialized AI personas (BA, SA, TL, etc.)[/dim]")
        console.print("[dim]   • Comprehensive documentation and planning[/dim]")
        console.print("[dim]   • Best for complex projects and team collaboration[/dim]")
    else:
        console.print("[green]✓[/green] Using [bold]Traditional[/bold] development strategy")
        console.print("[dim]   • Single AI agent approach[/dim]")
        console.print("[dim]   • Simpler setup, faster iteration[/dim]")
        console.print("[dim]   • Best for quick prototypes and solo development[/dim]")
    
    return strategy_choice

def get_project_namespace() -> str:
    """
    Get project namespace from user input with validation.
    
    Returns:
        Valid project namespace (single lowercase word)
    """
    while True:
        console.print("\n[bold cyan]Project Namespace Configuration[/bold cyan]")
        console.print("Enter a namespace for your project commands (e.g., 'myapp', 'project', 'api')")
        console.print("[dim]Commands will be: /<namespace>-specify, /<namespace>-plan, /<namespace>-tasks, etc.[/dim]")
        console.print("[dim]Press Enter for default: 'speckit'[/dim]\n")
        
        namespace = input("Project namespace: ").strip()
        
        # Use default if empty
        if not namespace:
            namespace = "speckit"
            console.print(f"[green]✓[/green] Using default namespace: [bold]{namespace}[/bold]")
            return namespace
        
        # Validate: single word, lowercase, alphanumeric with optional hyphens
        if not namespace:
            console.print("[red]Error:[/red] Namespace cannot be empty")
            continue
        
        # Convert to lowercase
        namespace = namespace.lower()
        
        # Check if it's a single word (no spaces)
        if ' ' in namespace:
            console.print("[red]Error:[/red] Namespace must be a single word (no spaces)")
            continue
        
        # Check if it contains only valid characters (alphanumeric and hyphens)
        import re
        if not re.match(r'^[a-z0-9-]+$', namespace):
            console.print("[red]Error:[/red] Namespace must contain only lowercase letters, numbers, and hyphens")
            continue
        
        # Check if it starts with a letter
        if not namespace[0].isalpha():
            console.print("[red]Error:[/red] Namespace must start with a letter")
            continue
        
        console.print(f"[green]✓[/green] Project namespace set to: [bold]{namespace}[/bold]")
        console.print(f"[dim]Your commands: /{namespace}-specify, /{namespace}-plan, /{namespace}-tasks, /{namespace}-implement, etc.[/dim]")
        return namespace

def generate_agent_commands(project_path: Path, ai_assistant: str, script_type: str, namespace: str = "speckit") -> int:
    """
    Generate agent-specific command files from templates.
    
    Args:
        project_path: Path to the project root
        ai_assistant: AI assistant name (e.g., 'cursor-agent', 'claude', 'copilot')
        script_type: Script type ('sh' or 'ps')
        namespace: Project namespace for spec commands
        
    Returns:
        Number of command files generated
    """
    # Agent-specific configuration
    agent_config_map = {
        "claude": {"dir": ".claude/commands", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "gemini": {"dir": ".gemini/commands", "ext": ".toml", "arg_format": "{{args}}"},
        "copilot": {"dir": ".github/prompts", "ext": ".prompt.md", "arg_format": "$ARGUMENTS"},
        "cursor-agent": {"dir": ".cursor/commands", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "qwen": {"dir": ".qwen/commands", "ext": ".toml", "arg_format": "{{args}}"},
        "opencode": {"dir": ".opencode/command", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "windsurf": {"dir": ".windsurf/workflows", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "codex": {"dir": ".codex/prompts", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "kilocode": {"dir": ".kilocode/workflows", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "auggie": {"dir": ".augment/commands", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "roo": {"dir": ".roo/commands", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "codebuddy": {"dir": ".codebuddy/commands", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "q": {"dir": ".amazonq/prompts", "ext": ".md", "arg_format": "$ARGUMENTS"},
        "amp": {"dir": ".agents/commands", "ext": ".md", "arg_format": "$ARGUMENTS"},
    }
    
    agent_cfg = agent_config_map.get(ai_assistant)
    if not agent_cfg:
        return 0
    
    # Create agent-specific command directory
    agent_dir = project_path / agent_cfg["dir"]
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    # Find template commands
    template_dir = project_path / "templates" / "commands"
    if not template_dir.exists():
        return 0
    
    generated_count = 0
    
    # Process each template
    for template_file in template_dir.glob("*.md"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter
            import re
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if not frontmatter_match:
                continue
            
            frontmatter, body = frontmatter_match.groups()
            
            # Extract description
            desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Extract script command for the selected script type
            script_match = re.search(rf'^\s*{script_type}:\s*(.+)$', frontmatter, re.MULTILINE)
            script_command = script_match.group(1).strip() if script_match else ""
            
            # Replace placeholders in body
            body = body.replace('{SCRIPT}', script_command)
            body = body.replace('$ARGUMENTS', agent_cfg["arg_format"])
            body = body.replace('/specx-', f'/{namespace}-')
            
            # Generate output file with namespace prefix
            # Always prefix commands with namespace (e.g., "speckit-specify.md" or "myapp-specify.md")
            output_filename = f"{namespace}-{template_file.stem}" + agent_cfg["ext"]
            output_path = agent_dir / output_filename
            
            # Create output content based on format
            if agent_cfg["ext"] == ".toml":
                # TOML format for Gemini/Qwen
                output_content = f'description = "{description}"\n\nprompt = """\n{body}\n"""\n'
            else:
                # Markdown format
                output_content = f'---\ndescription: {description}\n---\n\n{body}'
            
            # Write output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            generated_count += 1
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not generate {template_file.name}: {e}[/yellow]")
    
    return generated_count

def replace_namespace_in_commands(project_path: Path, namespace: str = "speckit") -> None:
    """
    Replace /specx- references with the custom namespace in all command files.
    
    Args:
        project_path: Path to the project root
        namespace: Project namespace for spec commands
    """
    # Find all agent-specific command directories
    agent_dirs = [
        project_path / ".claude" / "commands",
        project_path / ".gemini" / "commands",
        project_path / ".github" / "prompts",
        project_path / ".cursor" / "commands",
        project_path / ".qwen" / "commands",
        project_path / ".opencode" / "command",
        project_path / ".windsurf" / "workflows",
        project_path / ".codex" / "prompts",
        project_path / ".kilocode" / "workflows",
        project_path / ".augment" / "commands",
        project_path / ".roo" / "commands",
        project_path / ".codebuddy" / "commands",
        project_path / ".amazonq" / "prompts",
        project_path / ".agents" / "commands",
    ]
    
    # Also check templates directory for command templates
    template_commands = project_path / "templates" / "commands"
    if template_commands.exists():
        agent_dirs.append(template_commands)
    
    for agent_dir in agent_dirs:
        if not agent_dir.exists():
            continue
        
        # Process all markdown and toml files in the directory
        for file_path in agent_dir.glob("*"):
            if file_path.suffix in [".md", ".toml"]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace /specx- with /<namespace>-
                    updated_content = content.replace('/specx-', f'/{namespace}-')
                    
                    # Only write if content changed
                    if updated_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not update namespace in {file_path}: {e}[/yellow]")

def create_persona_config(project_path: Path, selected_personas: list, namespace: str = "speckit", strategy: str = "persona") -> None:
    """
    Create persona configuration file in .specify directory.
    
    Args:
        project_path: Path to the project root
        selected_personas: List of selected persona IDs
        namespace: Project namespace for spec commands
        strategy: Development strategy ('persona' or 'traditional')
    """
    specify_dir = project_path / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = specify_dir / "config.json"
    
    config = {
        "version": "1.0",
        "namespace": namespace,
        "strategy": strategy,
        "personas": {
            "enabled": selected_personas if strategy == "persona" else [],
            "available": list(PERSONA_CONFIG.keys())
        },
        "orchestration": {
            "parallel_execution": True if strategy == "persona" else False,
            "max_concurrent_personas": 3 if strategy == "persona" else 1
        }
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
        f.write('\n')

def copy_persona_files(project_path: Path, selected_personas: list, template_source: Path = None) -> None:
    """
    Copy selected persona definition files to project.
    
    Args:
        project_path: Path to the project root
        selected_personas: List of selected persona IDs
        template_source: Path to template personas directory (defaults to project templates)
    """
    # Determine source directory
    if template_source is None:
        # Use downloaded project templates directory
        template_source = project_path / "templates" / "personas"
    
    # Create destination directory
    personas_dir = project_path / "memory" / "personas"
    personas_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if persona files already exist in destination (from git clone)
    # If they do, we don't need to copy them
    all_personas_exist = all(
        (personas_dir / f"{persona_id}.md").exists() 
        for persona_id in selected_personas
    )
    
    if all_personas_exist and (personas_dir / "README.md").exists():
        # All files already in place (from git clone), no need to copy
        return
    
    # Copy selected persona files
    for persona_id in selected_personas:
        source_file = template_source / f"{persona_id}.md"
        dest_file = personas_dir / f"{persona_id}.md"
        
        # Skip if file already exists in destination
        if dest_file.exists():
            continue
            
        if source_file.exists():
            # Only copy if source and destination are different
            if source_file.resolve() != dest_file.resolve():
                shutil.copy2(source_file, dest_file)
        else:
            console.print(f"[yellow]Warning: Persona file not found: {source_file}[/yellow]")
    
    # Copy README if it doesn't already exist
    readme_dest = personas_dir / "README.md"
    if not readme_dest.exists():
        # Try templates directory first
        template_readme = project_path / "templates" / "personas" / "README.md"
        if template_readme.exists():
            shutil.copy2(template_readme, readme_dest)
        else:
            console.print(f"[yellow]Warning: Persona README not found[/yellow]")

def generate_beast_mode_chatmodes(project_path: Path, ai_assistant: str, selected_personas: list) -> int:
    """
    Generate Beast Mode chatmode files from selected personas.
    
    Args:
        project_path: Path to the project root
        ai_assistant: AI assistant key (e.g., 'claude', 'copilot', 'gemini')
        selected_personas: List of selected persona IDs
        
    Returns:
        Number of chatmode files generated
    """
    import re
    import yaml
    from string import Template
    
    # Get chatmode configuration for the agent
    chatmode_cfg = CHATMODE_CONFIG.get(ai_assistant)
    if not chatmode_cfg:
        return 0
    
    # Create agent-specific chatmode/persona directory
    chatmode_dir = project_path / chatmode_cfg["dir"]
    chatmode_dir.mkdir(parents=True, exist_ok=True)
    
    # Load Beast Mode templates from CLI installation directory
    # These templates are part of the SpecX CLI, not the project template
    cli_template_dir = Path(__file__).parent.parent.parent / "templates" / "chatmodes"
    
    # Fallback to project template directory for development/testing
    if not cli_template_dir.exists():
        cli_template_dir = project_path / "templates" / "chatmodes"
    
    if chatmode_cfg["format"] == "copilot-beast":
        template_file = cli_template_dir / "beast-mode-copilot.md"
    elif chatmode_cfg["format"] == "toml-beast":
        template_file = cli_template_dir / "beast-mode-toml.toml"
    else:  # markdown-beast
        template_file = cli_template_dir / "beast-mode-markdown.md"
    
    if not template_file.exists():
        console.print(f"[yellow]Warning: Beast Mode template not found: {template_file}[/yellow]")
        console.print(f"[yellow]Looked in: {cli_template_dir}[/yellow]")
        return 0
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    generated_count = 0
    
    # Process each selected persona
    for persona_id in selected_personas:
        # Load persona definition
        persona_file = project_path / "memory" / "personas" / f"{persona_id}.md"
        if not persona_file.exists():
            console.print(f"[yellow]Warning: Persona file not found: {persona_file}[/yellow]")
            continue
        
        with open(persona_file, 'r', encoding='utf-8') as f:
            persona_content = f.read()
        
        # Parse persona frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', persona_content, re.DOTALL)
        if not frontmatter_match:
            continue
        
        frontmatter, body = frontmatter_match.groups()
        
        # Parse YAML frontmatter
        try:
            persona_data = yaml.safe_load(frontmatter)
        except:
            console.print(f"[yellow]Warning: Could not parse persona frontmatter: {persona_id}[/yellow]")
            continue
        
        # Extract persona information
        persona_name = persona_data.get('name', 'Unknown Persona')
        short_name = persona_data.get('short_name', 'XX')
        role = persona_data.get('role', 'Unknown Role')
        contributes_to = persona_data.get('contributes_to', [])
        phases = persona_data.get('phases', {})
        
        # Transform persona content to Beast Mode
        beast_mode_data = transform_to_beast_mode(
            persona_id=persona_id,
            persona_name=persona_name,
            short_name=short_name,
            role=role,
            body=body,
            contributes_to=contributes_to,
            phases=phases
        )
        
        # Apply customizations if available
        try:
            from .beast_mode_customizer import enhance_transform_with_customization
            beast_mode_data = enhance_transform_with_customization(
                transform_to_beast_mode, project_path, persona_id, beast_mode_data
            )
        except ImportError:
            pass  # Customization not available
        
        # Apply template substitution
        try:
            output_content = Template(template_content).safe_substitute(**beast_mode_data)
        except Exception as e:
            console.print(f"[yellow]Warning: Template substitution failed for {persona_id}: {e}[/yellow]")
            continue
        
        # Generate output filename
        output_filename = f"{persona_id}{chatmode_cfg['ext']}"
        output_path = chatmode_dir / output_filename
        
        # Write chatmode file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            generated_count += 1
        except Exception as e:
            console.print(f"[yellow]Warning: Could not write chatmode file {output_filename}: {e}[/yellow]")
    
    # Generate persona switching command file
    if generated_count > 0:
        from .persona_manager import create_persona_command_file
        create_persona_command_file(project_path, ai_assistant)
    
    return generated_count

def transform_to_beast_mode(persona_id: str, persona_name: str, short_name: str, role: str, 
                           body: str, contributes_to: list, phases: dict) -> dict:
    """
    Transform persona definition to Beast Mode format.
    
    Returns dict with all template variables populated.
    """
    # Parse body sections to extract relevant information
    sections = parse_persona_sections(body)
    
    # Build Beast Mode data
    beast_mode_data = {
        'persona_id': persona_id,
        'name': persona_name,
        'full_name': persona_name,
        'short_name': short_name,
        'role': role,
        
        # Mission and objectives
        'mission': f"Transform project artifacts through {role.lower()} expertise",
        'mission_statement': sections.get('role_description', f"As {persona_name}, you are responsible for {role.lower()}."),
        'role_emphasis': f"primary {role.lower()} expert",
        'deliverable_emphasis': f"{role.lower()} foundation",
        
        # Objectives
        'objective_1': f"Analyze all inputs from a {role.lower()} perspective",
        'objective_2': f"Generate comprehensive {role.lower()} deliverables",
        'objective_3': f"Ensure quality and consistency in all outputs",
        
        # Input analysis
        'input_analysis': sections.get('input_analysis', 'Analyze all relevant project inputs'),
        'must_have_inputs': sections.get('must_have_inputs', '- [ ] Project requirements\n- [ ] Technical constraints'),
        'should_have_inputs': sections.get('should_have_inputs', '- [ ] Existing documentation\n- [ ] Team structure'),
        'nice_to_have_inputs': sections.get('nice_to_have_inputs', '- [ ] Historical context\n- [ ] Similar projects'),
        
        # Deliverables
        'deliverables_list': format_deliverables(contributes_to),
        'primary_deliverables': format_primary_deliverables(contributes_to),
        
        # Phase information
        'phase_number': '1',
        'phase_name': 'Analysis and Planning',
        'phase_duration': '30-45 min',
        'phase_steps': '1. Parse all input documents\n2. Extract relevant information\n3. Identify gaps and conflicts',
        'phase_validation': '- [ ] All inputs reviewed\n- [ ] Key information extracted\n- [ ] Gaps documented',
        'phase_issues': '- Missing critical information\n- Conflicting requirements\n- Ambiguous specifications',
        
        # Workflow phases
        'phase_1_name': 'Analysis and Planning',
        'phase_1_duration': '30-45 minutes',
        'phase_1_objective': f'Understand project context from {role.lower()} perspective',
        'phase_1_steps': format_phase_steps(phases, 'specify', 'analysis'),
        'phase_1_validation': '- All inputs analyzed\n- Context understood\n- Plan created',
        
        'phase_2_name': 'Core Execution',
        'phase_2_duration': '45-60 minutes',
        'phase_2_objective': f'Generate all {role.lower()} deliverables',
        'phase_2_steps': format_phase_steps(phases, 'plan', 'execution'),
        'phase_2_validation': '- All deliverables created\n- Quality standards met\n- Dependencies resolved',
        
        'phase_3_name': 'Validation and Finalization',
        'phase_3_duration': '15-30 minutes',
        'phase_3_objective': 'Validate and finalize all outputs',
        'phase_3_steps': format_phase_steps(phases, 'implement', 'validation'),
        'phase_3_validation': '- All outputs validated\n- Integration verified\n- Approval ready',
        
        # Metrics
        'metric_category_1': f'{persona_id.replace("-", "_")}_deliverables',
        'metric_1': 'documents_created',
        'metric_2': 'sections_completed',
        'metric_category_2': 'quality',
        'metric_subcategory_1': 'validation_passed',
        'metric_subcategory_2': 'rework_required',
        
        # Coverage metrics
        'coverage_metric_1': 'requirements_addressed',
        'coverage_metric_2': 'deliverables_complete',
        'coverage_metric_3': 'edge_cases_documented',
        
        # Artifacts and quality
        'artifact_checklist': format_artifact_checklist(contributes_to),
        'quality_checklist': sections.get('quality_checklist', '- [ ] All deliverables complete\n- [ ] Quality standards met'),
        'integration_checklist': '- [ ] Notifications queued\n- [ ] Approvals requested\n- [ ] Changes logged',
        'next_stage_checklist': format_next_stage_checklist(role),
        
        # Collaboration
        'collaboration_section': sections.get('collaboration', f'Collaborate with other personas for {role.lower()} alignment'),
        'phase_contributions': format_phase_contributions(phases),
        
        # Additional fields
        'start_message': f'Analyzing project from {role.lower()} perspective',
        'estimated_duration': '2-3 hours',
        'artifact_name': f'{persona_name} Deliverables',
        'artifact_summary': f'Complete {role.lower()} documentation and artifacts',
        'artifact_path': f'docs/{persona_id}/',
        'approval_summary': f'All {role.lower()} deliverables ready for review',
        'duration': 'Xh Ym',
        'artifact_count': 'N',
        
        # Error handling
        'missing_info_description': 'Missing critical project information',
        'required_field_1': 'Project requirements',
        'required_field_2': 'Technical constraints',
        'required_field_3': 'Success criteria',
        
        'conflict_description': 'Requirement conflict detected',
        'item_1': 'Requirement A',
        'item_2': 'Requirement B',
        
        'constraint_description': 'Technical constraint violation',
        'requirement': 'Required capability',
        'reality': 'Current limitation',
        
        # TOML-specific fields
        'phase_1_step_1': 'Review all input documents',
        'phase_1_step_2': 'Extract key information',
        'phase_1_step_3': 'Document findings',
        
        'phase_2_step_1': 'Create primary deliverables',
        'phase_2_step_2': 'Validate outputs',
        'phase_2_step_3': 'Integrate with other work',
        
        'phase_3_step_1': 'Run final validation',
        'phase_3_step_2': 'Prepare for approval',
        'phase_3_step_3': 'Document completion',
        
        # Additional TOML fields
        'required_input_1': 'Project specification',
        'required_input_2': 'Technical requirements',
        'required_input_3': 'Constraints and assumptions',
        
        'optional_input_1': 'Historical context',
        'optional_input_2': 'Similar projects',
        
        'deliverable_1': f'Primary {role.lower()} document',
        'deliverable_2': f'{role.capitalize()} analysis report',
        'deliverable_3': f'{role.capitalize()} recommendations',
        
        'expanded_mission': sections.get('role_description', f'Transform project through {role.lower()} expertise'),
        'phase_1_detailed_steps': 'Step-by-step analysis process',
        'phase_2_detailed_steps': 'Detailed execution workflow',
        'phase_3_detailed_steps': 'Validation and finalization steps',
        
        'detailed_output_requirements': f'Generate comprehensive {role.lower()} deliverables',
        'success_criteria_list': f'- All {role.lower()} work complete\n- Quality validated\n- Ready for integration',
        'final_checklist': '- All deliverables present\n- Quality standards met\n- Integration verified',
        
        'input_sources': 'Project specifications, requirements, constraints',
        'output_consumers': 'Next phase personas, project team',
        'coordination_points': 'Integration touchpoints with other personas',
        
        # Quality targets
        'quality_target': '95',
        'rework_target': '5',
        'time_target': '3 hours',
        
        # Phase contributions for TOML
        'specify_contribution_1': phases.get('specify', ['requirements'])[0] if phases.get('specify') else 'requirements',
        'specify_contribution_2': phases.get('specify', ['', 'analysis'])[1] if len(phases.get('specify', [])) > 1 else 'analysis',
        'plan_contribution_1': phases.get('plan', ['design'])[0] if phases.get('plan') else 'design',
        'plan_contribution_2': phases.get('plan', ['', 'architecture'])[1] if len(phases.get('plan', [])) > 1 else 'architecture',
        'tasks_contribution_1': phases.get('tasks', ['breakdown'])[0] if phases.get('tasks') else 'breakdown',
        'tasks_contribution_2': phases.get('tasks', ['', 'estimation'])[1] if len(phases.get('tasks', [])) > 1 else 'estimation',
        'implement_contribution_1': phases.get('implement', ['validation'])[0] if phases.get('implement') else 'validation',
        'implement_contribution_2': phases.get('implement', ['', 'review'])[1] if len(phases.get('implement', [])) > 1 else 'review',
        'clarify_contribution_1': phases.get('clarify', ['questions'])[0] if phases.get('clarify') else 'questions',
        'clarify_contribution_2': phases.get('clarify', ['', 'resolution'])[1] if len(phases.get('clarify', [])) > 1 else 'resolution',
        'analyze_contribution_1': phases.get('analyze', ['review'])[0] if phases.get('analyze') else 'review',
        'analyze_contribution_2': phases.get('analyze', ['', 'validation'])[1] if len(phases.get('analyze', [])) > 1 else 'validation',
        'checklist_contribution_1': phases.get('checklist', ['quality'])[0] if phases.get('checklist') else 'quality',
        'checklist_contribution_2': phases.get('checklist', ['', 'completeness'])[1] if len(phases.get('checklist', [])) > 1 else 'completeness',
        'constitution_contribution_1': phases.get('constitution', ['principles'])[0] if phases.get('constitution') else 'principles',
        'constitution_contribution_2': phases.get('constitution', ['', 'standards'])[1] if len(phases.get('constitution', [])) > 1 else 'standards',
        
        # Success and completion
        'completion_metrics': f'- All {role.lower()} deliverables complete\n- Quality validation passed',
        'quality_metrics': '- First-pass quality > 95%\n- Rework < 5%',
        'deliverable_checklist': f'- [ ] All {role.lower()} documents complete\n- [ ] Quality standards met',
        'completion_summary': f'All {role.lower()} work complete and validated',
        'artifact_list': f'- Primary {role.lower()} document\n- Analysis reports\n- Recommendations',
        'validation_summary': 'All validation checks passed',
        'next_steps': 'Ready for integration with other deliverables',
        'count': 'N',
        'date': 'YYYYMMDD',
    }
    
    return beast_mode_data

def parse_persona_sections(body: str) -> dict:
    """Parse persona markdown body into sections."""
    sections = {}
    current_section = None
    current_content = []
    
    for line in body.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section.lower().replace(' ', '_')] = '\n'.join(current_content)
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section.lower().replace(' ', '_')] = '\n'.join(current_content)
    
    return sections

def format_deliverables(contributes_to: list) -> str:
    """Format deliverables list from contributes_to phases."""
    deliverables = []
    for phase in contributes_to:
        deliverables.append(f"- {phase.capitalize()} phase contributions")
    return '\n'.join(deliverables) if deliverables else '- Primary analysis document\n- Recommendations report'

def format_primary_deliverables(contributes_to: list) -> str:
    """Format primary deliverables section."""
    return '\n'.join([f"### {phase.capitalize()} Phase\n- Comprehensive {phase} documentation" 
                     for phase in contributes_to[:3]]) if contributes_to else '### Primary Deliverables\n- Core documentation'

def format_phase_steps(phases: dict, phase_name: str, default: str) -> str:
    """Format phase steps from phases data."""
    if phase_name in phases and phases[phase_name]:
        return '\n'.join([f"{i+1}. {step.replace('-', ' ').capitalize()}" 
                         for i, step in enumerate(phases[phase_name])])
    return f"1. Perform {default} tasks\n2. Validate outputs\n3. Prepare for next phase"

def format_artifact_checklist(contributes_to: list) -> str:
    """Format artifact checklist based on contributions."""
    checklist = []
    for phase in contributes_to:
        checklist.append(f"- [ ] {phase.capitalize()} deliverables complete")
    return '\n'.join(checklist) if checklist else '- [ ] All deliverables complete'

def format_next_stage_checklist(role: str) -> str:
    """Format next stage readiness checklist."""
    return f"""- [ ] All {role.lower()} deliverables ready
- [ ] Integration points documented
- [ ] Handoff to next phase prepared
- [ ] Quality validation complete"""

def format_phase_contributions(phases: dict) -> str:
    """Format phase contributions section."""
    contributions = []
    for phase, items in phases.items():
        if items:
            contributions.append(f"### {phase.capitalize()} Phase")
            for item in items:
                contributions.append(f"- {item.replace('-', ' ').capitalize()}")
    return '\n'.join(contributions) if contributions else '### Phase Contributions\n- Analysis and recommendations'

def update_chatmodes_with_constitution(project_path: Path) -> int:
    """
    Update Beast Mode chatmodes and persona files to include project constitution.
    
    This is called after /constitution command to inject project-specific
    governance principles into both chatmode files and persona definition files.
    
    Args:
        project_path: Path to the project root
        
    Returns:
        Number of files updated
    """
    import re
    
    # Load constitution
    constitution_file = project_path / "memory" / "constitution.md"
    if not constitution_file.exists():
        return 0
    
    with open(constitution_file, 'r', encoding='utf-8') as f:
        constitution_content = f.read()
    
    updated_count = 0
    
    # 1. Update persona definition files in memory/personas/
    personas_dir = project_path / "memory" / "personas"
    if personas_dir.exists():
        for persona_file in personas_dir.glob("*.md"):
            # Skip README
            if persona_file.name == "README.md":
                continue
            
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if constitution already embedded
                if '## Project Constitution' in content:
                    # Replace existing constitution section
                    pattern = r'## Project Constitution\n.*?(?=\n## |\Z)'
                    replacement = f'## Project Constitution\n\n{constitution_content}\n'
                    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                else:
                    # Append constitution at the end
                    updated_content = content.rstrip() + f'\n\n---\n\n## Project Constitution\n\n{constitution_content}\n'
                
                # Write updated content
                with open(persona_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                updated_count += 1
            except Exception as e:
                console.print(f"[yellow]Warning: Could not update persona {persona_file.name}: {e}[/yellow]")
    
    # 2. Update Beast Mode chatmode files
    # Detect AI assistant from project structure
    ai_assistant = None
    for agent_key in AGENT_CONFIG.keys():
        agent_dir = project_path / AGENT_CONFIG[agent_key]["folder"]
        if agent_dir.exists():
            ai_assistant = agent_key
            break
    
    if ai_assistant:
        chatmode_cfg = CHATMODE_CONFIG.get(ai_assistant)
        if chatmode_cfg:
            chatmode_dir = project_path / chatmode_cfg["dir"]
            if chatmode_dir.exists():
                # Update each chatmode/persona file with constitution
                for chatmode_file in chatmode_dir.glob(f"*{chatmode_cfg['ext']}"):
                    # Skip persona-switch and current persona files
                    if 'persona-switch' in chatmode_file.name or 'CURRENT_PERSONA' in chatmode_file.name:
                        continue
                    
                    try:
                        with open(chatmode_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check if constitution already embedded
                        if '## Project Constitution' in content:
                            # Replace existing constitution section
                            pattern = r'## Project Constitution\n.*?(?=\n## |\Z)'
                            replacement = f'## Project Constitution\n\n{constitution_content}\n'
                            updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                        else:
                            # Append constitution at the end
                            updated_content = content.rstrip() + f'\n\n---\n\n## Project Constitution\n\n{constitution_content}\n'
                        
                        # Write updated content
                        with open(chatmode_file, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        updated_count += 1
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not update {chatmode_file.name}: {e}[/yellow]")
    
    return updated_count

class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)


app = typer.Typer(
    name="specify",
    help="Setup tool for Specify spec-driven development projects",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)

def show_banner():
    """Display the ASCII art banner."""
    banner_lines = BANNER.strip().split('\n')
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]

    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()

@app.callback()
def callback(ctx: typer.Context):
    """Show banner when no subcommand is provided."""
    if ctx.invoked_subcommand is None and "--help" not in sys.argv and "-h" not in sys.argv:
        show_banner()
        console.print(Align.center("[dim]Run 'specx --help' for usage information[/dim]"))
        console.print()

def run_command(cmd: list[str], check_return: bool = True, capture: bool = False, shell: bool = False) -> Optional[str]:
    """Run a shell command and optionally capture output."""
    try:
        if capture:
            result = subprocess.run(cmd, check=check_return, capture_output=True, text=True, shell=shell)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check_return, shell=shell)
            return None
    except subprocess.CalledProcessError as e:
        if check_return:
            console.print(f"[red]Error running command:[/red] {' '.join(cmd)}")
            console.print(f"[red]Exit code:[/red] {e.returncode}")
            if hasattr(e, 'stderr') and e.stderr:
                console.print(f"[red]Error output:[/red] {e.stderr}")
            raise
        return None

def check_tool(tool: str, tracker: StepTracker = None) -> bool:
    """Check if a tool is installed. Optionally update tracker.
    
    Args:
        tool: Name of the tool to check
        tracker: Optional StepTracker to update with results
        
    Returns:
        True if tool is found, False otherwise
    """
    # Special handling for Claude CLI after `claude migrate-installer`
    # See: https://github.com/hjk1995/specx-bot/issues/123
    # The migrate-installer command REMOVES the original executable from PATH
    # and creates an alias at ~/.claude/local/claude instead
    # This path should be prioritized over other claude executables in PATH
    if tool == "claude":
        if CLAUDE_LOCAL_PATH.exists() and CLAUDE_LOCAL_PATH.is_file():
            if tracker:
                tracker.complete(tool, "available")
            return True
    
    found = shutil.which(tool) is not None
    
    if tracker:
        if found:
            tracker.complete(tool, "available")
        else:
            tracker.error(tool, "not found")
    
    return found

def is_git_repo(path: Path = None) -> bool:
    """Check if the specified path is inside a git repository."""
    if path is None:
        path = Path.cwd()
    
    if not path.is_dir():
        return False

    try:
        # Use git command to check if inside a work tree
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            cwd=path,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def init_git_repo(project_path: Path, quiet: bool = False) -> Tuple[bool, Optional[str]]:
    """Initialize a git repository in the specified path.
    
    Args:
        project_path: Path to initialize git repository in
        quiet: if True suppress console output (tracker handles status)
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        original_cwd = Path.cwd()
        os.chdir(project_path)
        if not quiet:
            console.print("[cyan]Initializing git repository...[/cyan]")
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "Initial commit from Specify template"], check=True, capture_output=True, text=True)
        if not quiet:
            console.print("[green]✓[/green] Git repository initialized")
        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = f"Command: {' '.join(e.cmd)}\nExit code: {e.returncode}"
        if e.stderr:
            error_msg += f"\nError: {e.stderr.strip()}"
        elif e.stdout:
            error_msg += f"\nOutput: {e.stdout.strip()}"
        
        if not quiet:
            console.print(f"[red]Error initializing git repository:[/red] {e}")
        return False, error_msg
    finally:
        os.chdir(original_cwd)

def handle_vscode_settings(sub_item, dest_file, rel_path, verbose=False, tracker=None) -> None:
    """Handle merging or copying of .vscode/settings.json files."""
    def log(message, color="green"):
        if verbose and not tracker:
            console.print(f"[{color}]{message}[/] {rel_path}")

    try:
        with open(sub_item, 'r', encoding='utf-8') as f:
            new_settings = json.load(f)

        if dest_file.exists():
            merged = merge_json_files(dest_file, new_settings, verbose=verbose and not tracker)
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(merged, f, indent=4)
                f.write('\n')
            log("Merged:", "green")
        else:
            shutil.copy2(sub_item, dest_file)
            log("Copied (no existing settings.json):", "blue")

    except Exception as e:
        log(f"Warning: Could not merge, copying instead: {e}", "yellow")
        shutil.copy2(sub_item, dest_file)

def merge_json_files(existing_path: Path, new_content: dict, verbose: bool = False) -> dict:
    """Merge new JSON content into existing JSON file.

    Performs a deep merge where:
    - New keys are added
    - Existing keys are preserved unless overwritten by new content
    - Nested dictionaries are merged recursively
    - Lists and other values are replaced (not merged)

    Args:
        existing_path: Path to existing JSON file
        new_content: New JSON content to merge in
        verbose: Whether to print merge details

    Returns:
        Merged JSON content as dict
    """
    try:
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, just use new content
        return new_content

    def deep_merge(base: dict, update: dict) -> dict:
        """Recursively merge update dict into base dict."""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = deep_merge(result[key], value)
            else:
                # Add new key or replace existing value
                result[key] = value
        return result

    merged = deep_merge(existing_content, new_content)

    if verbose:
        console.print(f"[cyan]Merged JSON file:[/cyan] {existing_path.name}")

    return merged

def clone_from_main_branch(repo_owner: str, repo_name: str, ai_assistant: str, download_dir: Path, *, script_type: str = "sh", verbose: bool = True, debug: bool = False) -> Tuple[Path, dict]:
    """
    Clone repository from main branch when no releases are available.
    
    Args:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        ai_assistant: AI assistant name
        download_dir: Directory to download to
        script_type: Script type (sh or ps)
        verbose: Whether to show verbose output
        debug: Whether to show debug output
        
    Returns:
        Tuple of (extracted_path, metadata_dict)
    """
    import tempfile
    
    repo_url = f"https://github.com/{repo_owner}/{repo_name}.git"
    
    if verbose:
        console.print(f"[cyan]Cloning repository:[/cyan] {repo_url}")
    
    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_clone_dir:
        clone_path = Path(temp_clone_dir) / repo_name
        
        try:
            # Clone the repository
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", "main", repo_url, str(clone_path)],
                capture_output=True,
                text=True,
                check=True
            )
            
            if verbose:
                console.print("[green]✓[/green] Repository cloned successfully")
            
            # Copy the cloned repository to the download directory
            extracted_path = download_dir / f"{repo_name}-main"
            if extracted_path.exists():
                shutil.rmtree(extracted_path)
            
            shutil.copytree(clone_path, extracted_path, ignore=shutil.ignore_patterns('.git'))
            
            if verbose:
                console.print(f"[cyan]Extracted to:[/cyan] {extracted_path}")
            
            # Calculate directory size for metadata
            total_size = sum(f.stat().st_size for f in extracted_path.rglob('*') if f.is_file())
            
            # Return metadata compatible with release download format
            metadata = {
                "filename": f"{repo_name}-main",
                "size": total_size,
                "release": "main-branch",
                "asset_url": repo_url,
                "source": "git-clone",
                "branch": "main",
                "repo": f"{repo_owner}/{repo_name}"
            }
            
            return extracted_path, metadata
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error cloning repository[/red]")
            console.print(Panel(f"Git clone failed: {e.stderr}", title="Clone Error", border_style="red"))
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error processing cloned repository[/red]")
            console.print(Panel(str(e), title="Processing Error", border_style="red"))
            raise typer.Exit(1)

def download_template_from_github(ai_assistant: str, download_dir: Path, *, script_type: str = "sh", verbose: bool = True, show_progress: bool = True, client: httpx.Client = None, debug: bool = False, github_token: str = None) -> Tuple[Path, dict]:
    repo_owner = "hjk1995"
    repo_name = "specx-bot"
    if client is None:
        client = httpx.Client(verify=ssl_context)

    if verbose:
        console.print("[cyan]Fetching latest release information...[/cyan]")
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    try:
        response = client.get(
            api_url,
            timeout=30,
            follow_redirects=True,
            headers=_github_auth_headers(github_token),
        )
        status = response.status_code
        if status == 404:
            # No releases found - fall back to cloning from main branch
            if verbose:
                console.print("[yellow]No releases found. Cloning from main branch...[/yellow]")
            return clone_from_main_branch(repo_owner, repo_name, ai_assistant, download_dir, script_type=script_type, verbose=verbose, debug=debug)
        elif status != 200:
            msg = f"GitHub API returned {status} for {api_url}"
            if debug:
                msg += f"\nResponse headers: {response.headers}\nBody (truncated 500): {response.text[:500]}"
            raise RuntimeError(msg)
        try:
            release_data = response.json()
        except ValueError as je:
            raise RuntimeError(f"Failed to parse release JSON: {je}\nRaw (truncated 400): {response.text[:400]}")
    except Exception as e:
        if "404" in str(e):
            # No releases found - fall back to cloning from main branch
            if verbose:
                console.print("[yellow]No releases found. Cloning from main branch...[/yellow]")
            return clone_from_main_branch(repo_owner, repo_name, ai_assistant, download_dir, script_type=script_type, verbose=verbose, debug=debug)
        console.print(f"[red]Error fetching release information[/red]")
        console.print(Panel(str(e), title="Fetch Error", border_style="red"))
        raise typer.Exit(1)

    assets = release_data.get("assets", [])
    pattern = f"spec-kit-template-{ai_assistant}-{script_type}"
    matching_assets = [
        asset for asset in assets
        if pattern in asset["name"] and asset["name"].endswith(".zip")
    ]

    asset = matching_assets[0] if matching_assets else None

    if asset is None:
        console.print(f"[red]No matching release asset found[/red] for [bold]{ai_assistant}[/bold] (expected pattern: [bold]{pattern}[/bold])")
        asset_names = [a.get('name', '?') for a in assets]
        console.print(Panel("\n".join(asset_names) or "(no assets)", title="Available Assets", border_style="yellow"))
        raise typer.Exit(1)

    download_url = asset["browser_download_url"]
    filename = asset["name"]
    file_size = asset["size"]

    if verbose:
        console.print(f"[cyan]Found template:[/cyan] {filename}")
        console.print(f"[cyan]Size:[/cyan] {file_size:,} bytes")
        console.print(f"[cyan]Release:[/cyan] {release_data['tag_name']}")

    zip_path = download_dir / filename
    if verbose:
        console.print(f"[cyan]Downloading template...[/cyan]")

    try:
        with client.stream(
            "GET",
            download_url,
            timeout=60,
            follow_redirects=True,
            headers=_github_auth_headers(github_token),
        ) as response:
            if response.status_code != 200:
                body_sample = response.text[:400]
                raise RuntimeError(f"Download failed with {response.status_code}\nHeaders: {response.headers}\nBody (truncated): {body_sample}")
            total_size = int(response.headers.get('content-length', 0))
            with open(zip_path, 'wb') as f:
                if total_size == 0:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
                else:
                    if show_progress:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                            console=console,
                        ) as progress:
                            task = progress.add_task("Downloading...", total=total_size)
                            downloaded = 0
                            for chunk in response.iter_bytes(chunk_size=8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, completed=downloaded)
                    else:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
    except Exception as e:
        console.print(f"[red]Error downloading template[/red]")
        detail = str(e)
        if zip_path.exists():
            zip_path.unlink()
        console.print(Panel(detail, title="Download Error", border_style="red"))
        raise typer.Exit(1)
    if verbose:
        console.print(f"Downloaded: {filename}")
    metadata = {
        "filename": filename,
        "size": file_size,
        "release": release_data["tag_name"],
        "asset_url": download_url
    }
    return zip_path, metadata

def download_and_extract_template(project_path: Path, ai_assistant: str, script_type: str, is_current_dir: bool = False, *, verbose: bool = True, tracker: StepTracker | None = None, client: httpx.Client = None, debug: bool = False, github_token: str = None) -> Path:
    """Download the latest release and extract it to create a new project.
    Returns project_path. Uses tracker if provided (with keys: fetch, download, extract, cleanup)
    """
    current_dir = Path.cwd()

    if tracker:
        tracker.start("fetch", "contacting GitHub API")
    
    # Check if we got a cloned directory or a zip file
    is_cloned = False
    try:
        result = download_template_from_github(
            ai_assistant,
            current_dir,
            script_type=script_type,
            verbose=verbose and tracker is None,
            show_progress=(tracker is None),
            client=client,
            debug=debug,
            github_token=github_token
        )
        
        # Check if result is a tuple with Path and metadata
        if isinstance(result, tuple) and len(result) == 2:
            path_or_zip, meta = result
            # Check if it's a cloned directory (from git) or a zip file
            is_cloned = meta.get('source') == 'git-clone'
        else:
            raise ValueError("Unexpected return format from download_template_from_github")
            
        if tracker:
            tracker.complete("fetch", f"release {meta['release']} ({meta['size']:,} bytes)")
            if not is_cloned:
                tracker.add("download", "Download template")
                tracker.complete("download", meta['filename'])
    except Exception as e:
        if tracker:
            tracker.error("fetch", str(e))
        else:
            if verbose:
                console.print(f"[red]Error downloading template:[/red] {e}")
        raise

    # If cloned from git, copy files directly instead of extracting zip
    if is_cloned:
        if tracker:
            tracker.add("extract", "Copy cloned files")
            tracker.start("extract")
        elif verbose:
            console.print("Copying cloned files...")
        
        try:
            if not is_current_dir:
                project_path.mkdir(parents=True, exist_ok=True)
            
            # Copy files from cloned directory to project path
            source_dir = path_or_zip
            for item in source_dir.iterdir():
                dest_path = project_path / item.name
                if item.is_dir():
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(item, dest_path)
                else:
                    shutil.copy2(item, dest_path)
            
            if tracker:
                file_count = len(list(source_dir.iterdir()))
                tracker.complete("extract", f"{file_count} items copied")
            elif verbose:
                console.print(f"[green]✓[/green] Files copied successfully")
            
            # Cleanup cloned directory
            if tracker:
                tracker.add("cleanup", "Cleanup")
                tracker.start("cleanup")
            
            try:
                shutil.rmtree(source_dir)
                if tracker:
                    tracker.complete("cleanup", "cloned directory removed")
                elif verbose:
                    console.print("[green]✓[/green] Cleanup complete")
            except Exception as cleanup_error:
                if tracker:
                    tracker.error("cleanup", str(cleanup_error))
                elif verbose:
                    console.print(f"[yellow]Warning: cleanup failed: {cleanup_error}[/yellow]")
            
            return project_path
            
        except Exception as e:
            if tracker:
                tracker.error("extract", str(e))
            else:
                if verbose:
                    console.print(f"[red]Error copying files:[/red] {e}")
            raise
    
    # Original zip extraction logic
    zip_path = path_or_zip
    if tracker:
        tracker.add("extract", "Extract template")
        tracker.start("extract")
    elif verbose:
        console.print("Extracting template...")

    try:
        if not is_current_dir:
            project_path.mkdir(parents=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            if tracker:
                tracker.start("zip-list")
                tracker.complete("zip-list", f"{len(zip_contents)} entries")
            elif verbose:
                console.print(f"[cyan]ZIP contains {len(zip_contents)} items[/cyan]")

            if is_current_dir:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    if tracker:
                        tracker.start("extracted-summary")
                        tracker.complete("extracted-summary", f"temp {len(extracted_items)} items")
                    elif verbose:
                        console.print(f"[cyan]Extracted {len(extracted_items)} items to temp location[/cyan]")

                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]
                        if tracker:
                            tracker.add("flatten", "Flatten nested directory")
                            tracker.complete("flatten")
                        elif verbose:
                            console.print(f"[cyan]Found nested directory structure[/cyan]")

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            if dest_path.exists():
                                if verbose and not tracker:
                                    console.print(f"[yellow]Merging directory:[/yellow] {item.name}")
                                for sub_item in item.rglob('*'):
                                    if sub_item.is_file():
                                        rel_path = sub_item.relative_to(item)
                                        dest_file = dest_path / rel_path
                                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                                        # Special handling for .vscode/settings.json - merge instead of overwrite
                                        if dest_file.name == "settings.json" and dest_file.parent.name == ".vscode":
                                            handle_vscode_settings(sub_item, dest_file, rel_path, verbose, tracker)
                                        else:
                                            shutil.copy2(sub_item, dest_file)
                            else:
                                shutil.copytree(item, dest_path)
                        else:
                            if dest_path.exists() and verbose and not tracker:
                                console.print(f"[yellow]Overwriting file:[/yellow] {item.name}")
                            shutil.copy2(item, dest_path)
                    if verbose and not tracker:
                        console.print(f"[cyan]Template files merged into current directory[/cyan]")
            else:
                zip_ref.extractall(project_path)

                extracted_items = list(project_path.iterdir())
                if tracker:
                    tracker.start("extracted-summary")
                    tracker.complete("extracted-summary", f"{len(extracted_items)} top-level items")
                elif verbose:
                    console.print(f"[cyan]Extracted {len(extracted_items)} items to {project_path}:[/cyan]")
                    for item in extracted_items:
                        console.print(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")

                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    nested_dir = extracted_items[0]
                    temp_move_dir = project_path.parent / f"{project_path.name}_temp"

                    shutil.move(str(nested_dir), str(temp_move_dir))

                    project_path.rmdir()

                    shutil.move(str(temp_move_dir), str(project_path))
                    if tracker:
                        tracker.add("flatten", "Flatten nested directory")
                        tracker.complete("flatten")
                    elif verbose:
                        console.print(f"[cyan]Flattened nested directory structure[/cyan]")

    except Exception as e:
        if tracker:
            tracker.error("extract", str(e))
        else:
            if verbose:
                console.print(f"[red]Error extracting template:[/red] {e}")
                if debug:
                    console.print(Panel(str(e), title="Extraction Error", border_style="red"))

        if not is_current_dir and project_path.exists():
            shutil.rmtree(project_path)
        raise typer.Exit(1)
    else:
        if tracker:
            tracker.complete("extract")
    finally:
        if tracker:
            tracker.add("cleanup", "Remove temporary archive")

        if zip_path.exists():
            zip_path.unlink()
            if tracker:
                tracker.complete("cleanup")
            elif verbose:
                console.print(f"Cleaned up: {zip_path.name}")

    return project_path


def ensure_executable_scripts(project_path: Path, tracker: StepTracker | None = None) -> None:
    """Ensure POSIX .sh scripts under .specify/scripts (recursively) have execute bits (no-op on Windows)."""
    if os.name == "nt":
        return  # Windows: skip silently
    scripts_root = project_path / ".specify" / "scripts"
    if not scripts_root.is_dir():
        return
    failures: list[str] = []
    updated = 0
    for script in scripts_root.rglob("*.sh"):
        try:
            if script.is_symlink() or not script.is_file():
                continue
            try:
                with script.open("rb") as f:
                    if f.read(2) != b"#!":
                        continue
            except Exception:
                continue
            st = script.stat(); mode = st.st_mode
            if mode & 0o111:
                continue
            new_mode = mode
            if mode & 0o400: new_mode |= 0o100
            if mode & 0o040: new_mode |= 0o010
            if mode & 0o004: new_mode |= 0o001
            if not (new_mode & 0o100):
                new_mode |= 0o100
            os.chmod(script, new_mode)
            updated += 1
        except Exception as e:
            failures.append(f"{script.relative_to(scripts_root)}: {e}")
    if tracker:
        detail = f"{updated} updated" + (f", {len(failures)} failed" if failures else "")
        tracker.add("chmod", "Set script permissions recursively")
        (tracker.error if failures else tracker.complete)("chmod", detail)
    else:
        if updated:
            console.print(f"[cyan]Updated execute permissions on {updated} script(s) recursively[/cyan]")
        if failures:
            console.print("[yellow]Some scripts could not be updated:[/yellow]")
            for f in failures:
                console.print(f"  - {f}")

# Create persona subcommand group
persona_app = typer.Typer(name="persona", help="Manage Beast Mode personas")
app.add_typer(persona_app, name="persona")

@persona_app.command(name="switch")
def persona_switch(
    persona_id: str = typer.Argument(..., help="Persona ID to switch to (e.g., business-analyst, solution-architect)"),
    phase: Optional[str] = typer.Option(None, "--phase", help="Optional phase to set (e.g., specify, plan, implement)"),
):
    """Switch to a different Beast Mode persona."""
    from .persona_manager import PersonaManager
    
    project_path = Path.cwd()
    config_file = project_path / ".specify" / "config.json"
    
    if not config_file.exists():
        console.print("[red]Error:[/red] Not in a SpecX Bot project directory")
        console.print("Run this command from a project initialized with [cyan]specx init[/cyan]")
        raise typer.Exit(1)
    
    # Load persona configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    if not config.get("personas", {}).get("enabled"):
        console.print("[red]Error:[/red] No personas enabled in this project")
        console.print("This project was initialized without personas (Traditional mode)")
        raise typer.Exit(1)
    
    enabled_personas = config["personas"]["enabled"]
    if persona_id not in enabled_personas:
        console.print(f"[red]Error:[/red] Persona '{persona_id}' is not enabled")
        console.print(f"Enabled personas: {', '.join(enabled_personas)}")
        raise typer.Exit(1)
    
    # Detect AI assistant from project structure
    ai_assistant = None
    for agent_key in AGENT_CONFIG.keys():
        agent_dir = project_path / AGENT_CONFIG[agent_key]["folder"]
        if agent_dir.exists():
            ai_assistant = agent_key
            break
    
    # Perform the switch
    manager = PersonaManager(project_path)
    result = manager.switch_persona(persona_id, phase, ai_assistant=ai_assistant)
    
    console.print(f"[green]✓[/green] Switched to [cyan]{persona_id}[/cyan] persona")
    if result.get("previous_persona"):
        console.print(f"  Previous: [dim]{result['previous_persona']}[/dim]")
    if phase:
        console.print(f"  Phase: [cyan]{phase}[/cyan]")
    console.print(f"  Activated: {result['activated_at']}")
    
    # Show how to use in AI agent
    if ai_assistant:
        chatmode_cfg = CHATMODE_CONFIG.get(ai_assistant, {})
        if chatmode_cfg:
            persona_file = chatmode_cfg["dir"] + "/" + persona_id + chatmode_cfg["ext"]
            console.print(f"\n[dim]In your AI agent, reference: [cyan]@{persona_file}[/cyan][/dim]")
            console.print(f"[dim]Or check: [cyan]CURRENT_PERSONA.md[/cyan] in your agent directory[/dim]")

@persona_app.command(name="status")
def persona_status():
    """Show current persona status and context."""
    from .persona_manager import PersonaManager
    
    project_path = Path.cwd()
    manager = PersonaManager(project_path)
    
    summary = manager.get_context_summary()
    
    if summary["status"] == "no_active_persona":
        console.print("[yellow]No active persona[/yellow]")
        console.print("Use [cyan]specx persona switch <persona-id>[/cyan] to activate a persona")
        return
    
    console.print(f"[bold]Active Persona:[/bold] [cyan]{summary['persona']}[/cyan]")
    console.print(f"Phase: {summary['phase'] or 'Not specified'}")
    console.print(f"Duration: {summary['duration_seconds'] / 60:.1f} minutes")
    
    if summary['artifacts']:
        console.print(f"\n[bold]Artifacts Created:[/bold] {len(summary['artifacts'])}")
        for artifact in summary['artifacts'][-5:]:
            console.print(f"  • {artifact}")
    
@persona_app.command(name="regenerate")
def persona_regenerate(
    persona_id: Optional[str] = typer.Argument(None, help="Specific persona to regenerate (or all if not specified)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force regeneration even if files exist"),
):
    """Regenerate Beast Mode chatmode files."""
    project_path = Path.cwd()
    config_file = project_path / ".specify" / "config.json"
    
    if not config_file.exists():
        console.print("[red]Error:[/red] Not in a SpecX Bot project directory")
        raise typer.Exit(1)
    
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    if not config.get("personas", {}).get("enabled"):
        console.print("[red]Error:[/red] No personas enabled in this project")
        raise typer.Exit(1)
    
    # Get AI assistant from config
    ai_assistant = None
    for agent_key in AGENT_CONFIG.keys():
        agent_dir = project_path / AGENT_CONFIG[agent_key]["folder"]
        if agent_dir.exists():
            ai_assistant = agent_key
            break
    
    if not ai_assistant:
        console.print("[red]Error:[/red] Could not determine AI assistant for this project")
        raise typer.Exit(1)
    
    # Determine which personas to regenerate
    if persona_id:
        if persona_id not in config["personas"]["enabled"]:
            console.print(f"[red]Error:[/red] Persona '{persona_id}' is not enabled")
            raise typer.Exit(1)
        personas_to_generate = [persona_id]
    else:
        personas_to_generate = config["personas"]["enabled"]
    
    # Check if files exist
    chatmode_cfg = CHATMODE_CONFIG.get(ai_assistant, {})
    if chatmode_cfg and not force:
        chatmode_dir = project_path / chatmode_cfg["dir"]
        existing_files = []
        for pid in personas_to_generate:
            file_path = chatmode_dir / f"{pid}{chatmode_cfg['ext']}"
            if file_path.exists():
                existing_files.append(file_path)
        
        if existing_files:
            console.print("[yellow]Warning:[/yellow] The following chatmode files already exist:")
            for f in existing_files:
                console.print(f"  • {f}")
            if not typer.confirm("\nOverwrite existing files?"):
                console.print("Regeneration cancelled")
                raise typer.Exit(0)
    
    # Regenerate chatmodes
    console.print(f"[cyan]Regenerating Beast Mode chatmodes for {ai_assistant}...[/cyan]")
    
    count = generate_beast_mode_chatmodes(project_path, ai_assistant, personas_to_generate)
    
    if count > 0:
        console.print(f"[green]✓[/green] Regenerated {count} Beast Mode chatmode(s)")
        console.print(f"Files created in: {chatmode_cfg['dir']}/")
    else:
        console.print("[yellow]No chatmodes were generated[/yellow]")


@app.command(name="regenerate-chatmodes")
def regenerate_chatmodes(
    force: bool = typer.Option(False, "--force", "-f", help="Force regeneration even if files exist"),
):
    """Regenerate all Beast Mode chatmode files for the project."""
    # This is a convenience wrapper for persona regenerate
    persona_regenerate(persona_id=None, force=force)

@app.command(name="update-constitution")
def update_constitution():
    """Update Beast Mode chatmodes with the latest project constitution."""
    project_path = Path.cwd()
    
    # Check if constitution exists
    constitution_file = project_path / "memory" / "constitution.md"
    if not constitution_file.exists():
        console.print("[red]Error:[/red] No constitution found at memory/constitution.md")
        console.print("Run the [cyan]/constitution[/cyan] command in your AI agent first")
        raise typer.Exit(1)
    
    # Update chatmodes and persona files
    console.print("[cyan]Updating persona files and Beast Mode chatmodes with project constitution...[/cyan]")
    updated_count = update_chatmodes_with_constitution(project_path)
    
    if updated_count > 0:
        console.print(f"[green]✓[/green] Updated {updated_count} file(s) with project constitution")
        console.print("  • Persona definition files (memory/personas/)")
        console.print("  • Beast Mode chatmode files (agent directory)")
        console.print("\nYour AI agent personas now include project-specific governance principles")
    else:
        console.print("[yellow]No files were updated[/yellow]")
        console.print("Make sure you have personas configured (run [cyan]specx init[/cyan] with role-based strategy)")

@app.command()
def init(
    project_name: str = typer.Argument(None, help="Name for your new project directory (optional if using --here, or use '.' for current directory)"),
    ai_assistant: str = typer.Option(None, "--ai", help="AI assistant to use: claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, amp, or q"),
    script_type: str = typer.Option(None, "--script", help="Script type to use: sh or ps"),
    ignore_agent_tools: bool = typer.Option(False, "--ignore-agent-tools", help="Skip checks for AI agent tools like Claude Code"),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git repository initialization"),
    here: bool = typer.Option(False, "--here", help="Initialize project in the current directory instead of creating a new one"),
    force: bool = typer.Option(False, "--force", help="Force merge/overwrite when using --here (skip confirmation)"),
    skip_tls: bool = typer.Option(False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"),
    debug: bool = typer.Option(False, "--debug", help="Show verbose diagnostic output for network and extraction failures"),
    github_token: str = typer.Option(None, "--github-token", help="GitHub token to use for API requests (or set GH_TOKEN or GITHUB_TOKEN environment variable)"),
):
    """
    Initialize a new SpecX Bot project from the latest template.
    
    This command will:
    1. Check that required tools are installed (git is optional)
    2. Let you choose your AI assistant
    3. Select development strategy (Role-Based or Traditional)
    4. Configure project namespace (Role-Based only)
    5. Select role personas (Role-Based only)
    6. Download the appropriate template from GitHub
    7. Extract the template to a new project directory or current directory
    8. Generate agent-specific commands with your namespace
    9. Initialize a fresh git repository (if not --no-git and no existing repo)
    
    Examples:
        specx init my-project
        specx init my-project --ai cursor-agent
        specx init my-project --ai claude --no-git
        specx init --ignore-agent-tools my-project
        specx init . --ai claude         # Initialize in current directory
        specx init .                     # Initialize in current directory (interactive AI selection)
        specx init --here --ai claude    # Alternative syntax for current directory
        specx init --here --ai copilot
        specx init --here
        specx init --here --force  # Skip confirmation when current directory not empty
    """

    show_banner()

    if project_name == ".":
        here = True
        project_name = None  # Clear project_name to use existing validation logic

    if here and project_name:
        console.print("[red]Error:[/red] Cannot specify both project name and --here flag")
        raise typer.Exit(1)

    if not here and not project_name:
        console.print("[red]Error:[/red] Must specify either a project name, use '.' for current directory, or use --here flag")
        raise typer.Exit(1)

    if here:
        project_name = Path.cwd().name
        project_path = Path.cwd()

        existing_items = list(project_path.iterdir())
        if existing_items:
            console.print(f"[yellow]Warning:[/yellow] Current directory is not empty ({len(existing_items)} items)")
            console.print("[yellow]Template files will be merged with existing content and may overwrite existing files[/yellow]")
            if force:
                console.print("[cyan]--force supplied: skipping confirmation and proceeding with merge[/cyan]")
            else:
                response = typer.confirm("Do you want to continue?")
                if not response:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(0)
    else:
        project_path = Path(project_name).resolve()
        if project_path.exists():
            error_panel = Panel(
                f"Directory '[cyan]{project_name}[/cyan]' already exists\n"
                "Please choose a different project name or remove the existing directory.",
                title="[red]Directory Conflict[/red]",
                border_style="red",
                padding=(1, 2)
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    current_dir = Path.cwd()

    setup_lines = [
        "[cyan]Specify Project Setup[/cyan]",
        "",
        f"{'Project':<15} [green]{project_path.name}[/green]",
        f"{'Working Path':<15} [dim]{current_dir}[/dim]",
    ]

    if not here:
        setup_lines.append(f"{'Target Path':<15} [dim]{project_path}[/dim]")

    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))

    should_init_git = False
    if not no_git:
        should_init_git = check_tool("git")
        if not should_init_git:
            console.print("[yellow]Git not found - will skip repository initialization[/yellow]")

    if ai_assistant:
        if ai_assistant not in AGENT_CONFIG:
            console.print(f"[red]Error:[/red] Invalid AI assistant '{ai_assistant}'. Choose from: {', '.join(AGENT_CONFIG.keys())}")
            raise typer.Exit(1)
        selected_ai = ai_assistant
    else:
        # Create options dict for selection (agent_key: display_name)
        ai_choices = {key: config["name"] for key, config in AGENT_CONFIG.items()}
        selected_ai = select_with_arrows(
            ai_choices, 
            "Choose your AI assistant:", 
            "copilot"
        )

    if not ignore_agent_tools:
        agent_config = AGENT_CONFIG.get(selected_ai)
        if agent_config and agent_config["requires_cli"]:
            install_url = agent_config["install_url"]
            if not check_tool(selected_ai):
                error_panel = Panel(
                    f"[cyan]{selected_ai}[/cyan] not found\n"
                    f"Install from: [cyan]{install_url}[/cyan]\n"
                    f"{agent_config['name']} is required to continue with this project type.\n\n"
                    "Tip: Use [cyan]--ignore-agent-tools[/cyan] to skip this check",
                    title="[red]Agent Detection Error[/red]",
                    border_style="red",
                    padding=(1, 2)
                )
                console.print()
                console.print(error_panel)
                raise typer.Exit(1)

    if script_type:
        if script_type not in SCRIPT_TYPE_CHOICES:
            console.print(f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}")
            raise typer.Exit(1)
        selected_script = script_type
    else:
        default_script = "ps" if os.name == "nt" else "sh"

        if sys.stdin.isatty():
            selected_script = select_with_arrows(SCRIPT_TYPE_CHOICES, "Choose script type (or press Enter)", default_script)
        else:
            selected_script = default_script

    console.print(f"[cyan]Selected AI assistant:[/cyan] {selected_ai}")
    console.print(f"[cyan]Selected script type:[/cyan] {selected_script}")

    # Development strategy selection
    if sys.stdin.isatty():
        strategy = get_development_strategy()
    else:
        # Non-interactive mode: use persona-based by default
        strategy = "persona"
    
    console.print(f"[cyan]Development strategy:[/cyan] {strategy}")

    # Project namespace selection (only for role-based strategy)
    if strategy == "persona":
        if sys.stdin.isatty():
            namespace = get_project_namespace()
        else:
            # Non-interactive mode: use default
            namespace = "speckit"
        
        console.print(f"[cyan]Project namespace:[/cyan] {namespace}")
    else:
        # Traditional strategy uses default namespace
        namespace = "speckit"
        console.print(f"[cyan]Project namespace:[/cyan] {namespace} (default for traditional mode)")

    # Persona selection (only if using persona-based strategy)
    selected_personas = []
    if strategy == "persona":
        persona_options = {key: f"{config['name']} - {config['description']}" 
                          for key, config in PERSONA_CONFIG.items()}
        default_personas = [key for key, config in PERSONA_CONFIG.items() if config.get('default', False)]
        
        if sys.stdin.isatty():
            selected_personas = multi_select_with_arrows(
                persona_options,
                "Select role personas for your project:",
                defaults=default_personas
            )
        else:
            # Non-interactive mode: use defaults
            selected_personas = default_personas
        
        console.print(f"[cyan]Selected personas:[/cyan] {', '.join([PERSONA_CONFIG[p]['name'] for p in selected_personas])}")
    else:
        console.print(f"[cyan]Persona system:[/cyan] Disabled (using traditional single-agent approach)")

    tracker = StepTracker("Initialize SpecX Bot Project")

    sys._specify_tracker_active = True

    tracker.add("precheck", "Check required tools")
    tracker.complete("precheck", "ok")
    tracker.add("ai-select", "Select AI assistant")
    tracker.complete("ai-select", f"{selected_ai}")
    tracker.add("script-select", "Select script type")
    tracker.complete("script-select", selected_script)
    tracker.add("strategy-select", "Select development strategy")
    tracker.complete("strategy-select", strategy)
    if strategy == "persona":
        tracker.add("namespace-select", "Set project namespace")
        tracker.complete("namespace-select", namespace)
        tracker.add("persona-select", "Select role personas")
        tracker.complete("persona-select", f"{len(selected_personas)} selected")
    for key, label in [
        ("fetch", "Fetch latest release"),
        ("download", "Download template"),
        ("extract", "Extract template"),
        ("zip-list", "Archive contents"),
        ("extracted-summary", "Extraction summary"),
        ("chmod", "Ensure scripts executable"),
        ("personas", "Setup role personas"),
        ("cleanup", "Cleanup"),
        ("git", "Initialize git repository"),
        ("final", "Finalize")
    ]:
        tracker.add(key, label)

    # Track git error message outside Live context so it persists
    git_error_message = None

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            verify = not skip_tls
            local_ssl_context = ssl_context if verify else False
            local_client = httpx.Client(verify=local_ssl_context)

            download_and_extract_template(project_path, selected_ai, selected_script, here, verbose=False, tracker=tracker, client=local_client, debug=debug, github_token=github_token)

            ensure_executable_scripts(project_path, tracker=tracker)

            # Generate agent-specific commands
            tracker.add("commands", "Generate agent commands")
            tracker.start("commands")
            try:
                cmd_count = generate_agent_commands(project_path, selected_ai, selected_script, namespace)
                if cmd_count > 0:
                    tracker.complete("commands", f"{cmd_count} commands generated")
                else:
                    # Commands might already exist from release package
                    tracker.complete("commands", "using existing commands")
                    # Still need to update namespace in existing commands
                    replace_namespace_in_commands(project_path, namespace)
            except Exception as e:
                tracker.error("commands", f"generation failed: {str(e)}")

            # Setup personas (only if using persona-based strategy)
            if strategy == "persona" and selected_personas:
                tracker.start("personas")
                try:
                    copy_persona_files(project_path, selected_personas)
                    create_persona_config(project_path, selected_personas, namespace, strategy)
                    
                    # Generate Beast Mode chatmodes for the AI assistant
                    chatmode_count = generate_beast_mode_chatmodes(project_path, selected_ai, selected_personas)
                    if chatmode_count > 0:
                        tracker.complete("personas", f"{len(selected_personas)} personas configured, {chatmode_count} chatmodes generated")
                    else:
                        tracker.complete("personas", f"{len(selected_personas)} personas configured")
                except Exception as e:
                    tracker.error("personas", f"setup failed: {str(e)}")
            else:
                tracker.skip("personas", "traditional mode")

            if not no_git:
                tracker.start("git")
                if is_git_repo(project_path):
                    tracker.complete("git", "existing repo detected")
                elif should_init_git:
                    success, error_msg = init_git_repo(project_path, quiet=True)
                    if success:
                        tracker.complete("git", "initialized")
                    else:
                        tracker.error("git", "init failed")
                        git_error_message = error_msg
                else:
                    tracker.skip("git", "git not available")
            else:
                tracker.skip("git", "--no-git flag")

            tracker.complete("final", "project ready")
        except Exception as e:
            tracker.error("final", str(e))
            console.print(Panel(f"Initialization failed: {e}", title="Failure", border_style="red"))
            if debug:
                _env_pairs = [
                    ("Python", sys.version.split()[0]),
                    ("Platform", sys.platform),
                    ("CWD", str(Path.cwd())),
                ]
                _label_width = max(len(k) for k, _ in _env_pairs)
                env_lines = [f"{k.ljust(_label_width)} → [bright_black]{v}[/bright_black]" for k, v in _env_pairs]
                console.print(Panel("\n".join(env_lines), title="Debug Environment", border_style="magenta"))
            if not here and project_path.exists():
                shutil.rmtree(project_path)
            raise typer.Exit(1)
        finally:
            pass

    console.print(tracker.render())
    console.print("\n[bold green]Project ready.[/bold green]")
    
    # Show git error details if initialization failed
    if git_error_message:
        console.print()
        git_error_panel = Panel(
            f"[yellow]Warning:[/yellow] Git repository initialization failed\n\n"
            f"{git_error_message}\n\n"
            f"[dim]You can initialize git manually later with:[/dim]\n"
            f"[cyan]cd {project_path if not here else '.'}[/cyan]\n"
            f"[cyan]git init[/cyan]\n"
            f"[cyan]git add .[/cyan]\n"
            f"[cyan]git commit -m \"Initial commit\"[/cyan]",
            title="[red]Git Initialization Failed[/red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(git_error_panel)

    # Agent folder security notice
    agent_config = AGENT_CONFIG.get(selected_ai)
    if agent_config:
        agent_folder = agent_config["folder"]
        security_notice = Panel(
            f"Some agents may store credentials, auth tokens, or other identifying and private artifacts in the agent folder within your project.\n"
            f"Consider adding [cyan]{agent_folder}[/cyan] (or parts of it) to [cyan].gitignore[/cyan] to prevent accidental credential leakage.",
            title="[yellow]Agent Folder Security[/yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print()
        console.print(security_notice)

    steps_lines = []
    if not here:
        steps_lines.append(f"1. Go to the project folder: [cyan]cd {project_name}[/cyan]")
        step_num = 2
    else:
        steps_lines.append("1. You're already in the project directory!")
        step_num = 2

    # Add Codex-specific setup step if needed
    if selected_ai == "codex":
        codex_path = project_path / ".codex"
        quoted_path = shlex.quote(str(codex_path))
        if os.name == "nt":  # Windows
            cmd = f"setx CODEX_HOME {quoted_path}"
        else:  # Unix-like systems
            cmd = f"export CODEX_HOME={quoted_path}"
        
        steps_lines.append(f"{step_num}. Set [cyan]CODEX_HOME[/cyan] environment variable before running Codex: [cyan]{cmd}[/cyan]")
        step_num += 1

    steps_lines.append(f"{step_num}. Start using slash commands with your AI agent:")

    steps_lines.append(f"   2.1 [cyan]/{namespace}-constitution[/] - Establish project principles")
    steps_lines.append(f"   2.2 [cyan]/{namespace}-specify[/] - Create baseline specification")
    steps_lines.append(f"   2.3 [cyan]/{namespace}-plan[/] - Create implementation plan")
    steps_lines.append(f"   2.4 [cyan]/{namespace}-tasks[/] - Generate actionable tasks")
    steps_lines.append(f"   2.5 [cyan]/{namespace}-implement[/] - Execute implementation")

    steps_panel = Panel("\n".join(steps_lines), title="Next Steps", border_style="cyan", padding=(1,2))
    console.print()
    console.print(steps_panel)

    enhancement_lines = [
        "Optional commands that you can use for your specs [bright_black](improve quality & confidence)[/bright_black]",
        "",
        f"○ [cyan]/{namespace}-clarify[/] [bright_black](optional)[/bright_black] - Ask structured questions to de-risk ambiguous areas before planning (run before [cyan]/{namespace}-plan[/] if used)",
        f"○ [cyan]/{namespace}-analyze[/] [bright_black](optional)[/bright_black] - Cross-artifact consistency & alignment report (after [cyan]/{namespace}-tasks[/], before [cyan]/{namespace}-implement[/])",
        f"○ [cyan]/{namespace}-checklist[/] [bright_black](optional)[/bright_black] - Generate quality checklists to validate requirements completeness, clarity, and consistency (after [cyan]/{namespace}-plan[/])"
    ]
    enhancements_panel = Panel("\n".join(enhancement_lines), title="Enhancement Commands", border_style="cyan", padding=(1,2))
    console.print()
    console.print(enhancements_panel)

@app.command()
def check():
    """Check that all required tools are installed."""
    show_banner()
    console.print("[bold]Checking for installed tools...[/bold]\n")

    tracker = StepTracker("Check Available Tools")

    tracker.add("git", "Git version control")
    git_ok = check_tool("git", tracker=tracker)

    agent_results = {}
    for agent_key, agent_config in AGENT_CONFIG.items():
        agent_name = agent_config["name"]
        requires_cli = agent_config["requires_cli"]

        tracker.add(agent_key, agent_name)

        if requires_cli:
            agent_results[agent_key] = check_tool(agent_key, tracker=tracker)
        else:
            # IDE-based agent - skip CLI check and mark as optional
            tracker.skip(agent_key, "IDE-based, no CLI check")
            agent_results[agent_key] = False  # Don't count IDE agents as "found"

    # Check VS Code variants (not in agent config)
    tracker.add("code", "Visual Studio Code")
    code_ok = check_tool("code", tracker=tracker)

    tracker.add("code-insiders", "Visual Studio Code Insiders")
    code_insiders_ok = check_tool("code-insiders", tracker=tracker)

    console.print(tracker.render())

    console.print("\n[bold green]Specify CLI is ready to use![/bold green]")

    if not git_ok:
        console.print("[dim]Tip: Install git for repository management[/dim]")

    if not any(agent_results.values()):
        console.print("[dim]Tip: Install an AI assistant for the best experience[/dim]")

def main():
    app()

if __name__ == "__main__":
    main()

