"""OpenClaw configuration check."""

import json
import sys
from pathlib import Path

import yaml

from .base import BaseCheck, CheckResult, CheckStatus


class ConfigCheck(BaseCheck):
    """Check OpenClaw configuration files."""
    
    name = "Config"
    description = "Validates OpenClaw configuration"
    
    # Required config fields
    REQUIRED_FIELDS = ["provider"]
    OPTIONAL_FIELDS = ["model", "channels", "skills"]
    
    def __init__(self):
        self._config_path: Path | None = None
        self._config: dict | None = None
        self._missing_fields: list[str] = []
    
    def _find_config(self) -> Path | None:
        """Find the OpenClaw config file."""
        home = Path.home()
        
        possible_paths = [
            home / ".openclaw" / "config.yaml",
            home / ".openclaw" / "config.yml",
            home / ".openclaw" / "config.json",
            home / ".config" / "openclaw" / "config.yaml",
            home / ".config" / "openclaw" / "config.yml",
            home / ".config" / "openclaw" / "config.json",
        ]
        
        if sys.platform == "win32":
            possible_paths.extend([
                home / "AppData" / "Local" / "openclaw" / "config.yaml",
                home / "AppData" / "Local" / "openclaw" / "config.json",
            ])
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _parse_config(self, path: Path) -> dict | None:
        """Parse the config file."""
        try:
            content = path.read_text(encoding="utf-8")
            
            if path.suffix == ".json":
                return json.loads(content)
            else:  # YAML
                return yaml.safe_load(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
    
    def _validate_config(self, config: dict) -> list[str]:
        """Validate config and return list of missing required fields."""
        missing = []
        for field in self.REQUIRED_FIELDS:
            if field not in config or not config[field]:
                missing.append(field)
        return missing
    
    def run(self) -> CheckResult:
        """Run the config check."""
        self._config_path = self._find_config()
        
        if not self._config_path:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message="No OpenClaw config file found",
                details="Config will be created during OpenClaw setup",
                can_auto_fix=True,
                fix_suggestions=[
                    "Run 'openclaw init' to create initial config",
                    "Or create ~/.openclaw/config.yaml manually",
                ],
            )
        
        try:
            self._config = self._parse_config(self._config_path)
        except ValueError as e:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                message=f"Config file has syntax errors",
                details=str(e),
                fix_suggestions=[
                    f"Fix the syntax errors in: {self._config_path}",
                    "Use a YAML/JSON validator to check the file",
                ],
            )
        
        if not self._config:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message="Config file is empty",
                details=f"Path: {self._config_path}",
                can_auto_fix=True,
                fix_suggestions=["Add configuration to the file or run 'openclaw init'"],
            )
        
        self._missing_fields = self._validate_config(self._config)
        
        if self._missing_fields:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message=f"Config missing fields: {', '.join(self._missing_fields)}",
                details=f"Path: {self._config_path}",
                fix_suggestions=[
                    f"Add the following to your config: {', '.join(self._missing_fields)}",
                    "Run 'openclaw init' to reconfigure",
                ],
            )
        
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            message="Configuration valid",
            details=f"Path: {self._config_path}",
        )
    
    def fix(self) -> bool:
        """Attempt to fix config issues."""
        from ..console import console, print_fix_action, print_suggestion
        
        if not self._config_path:
            # Create default config directory
            home = Path.home()
            config_dir = home / ".openclaw"
            config_path = config_dir / "config.yaml"
            
            print_fix_action("Creating default OpenClaw config...")
            
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
                
                default_config = {
                    "provider": "anthropic",
                    "model": "claude-3-5-sonnet-20241022",
                    "channels": [],
                    "skills": [],
                }
                
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(default_config, f, default_flow_style=False)
                
                console.print(f"[green]Created config at:[/green] {config_path}")
                console.print("[dim]Edit this file to add your API keys and configure channels.[/dim]")
                return True
            except Exception as e:
                console.print(f"[red]Failed to create config:[/red] {e}")
                return False
        
        print_suggestion(
            "Fix Config Issues",
            [
                f"Edit your config file: {self._config_path}",
                "Or run 'openclaw init' to reconfigure",
            ]
        )
        return False
