"""API keys validation check."""

import os
import re
import sys
from pathlib import Path

import yaml

from .base import BaseCheck, CheckResult, CheckStatus


class APIKeysCheck(BaseCheck):
    """Check if API keys are configured for AI providers."""
    
    name = "API Keys"
    description = "Checks AI provider keys configured"
    
    # Known API key patterns (for basic validation, not security)
    KEY_PATTERNS = {
        "ANTHROPIC_API_KEY": r"^sk-ant-[a-zA-Z0-9\-_]{40,}$",
        "OPENAI_API_KEY": r"^sk-[a-zA-Z0-9]{40,}$",
        "GOOGLE_API_KEY": r"^AIza[a-zA-Z0-9\-_]{35}$",
        "GROQ_API_KEY": r"^gsk_[a-zA-Z0-9]{50,}$",
    }
    
    # Environment variables to check
    ENV_KEYS = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY", 
        "GOOGLE_API_KEY",
        "GOOGLE_GENERATIVE_AI_API_KEY",
        "GROQ_API_KEY",
        "OPENROUTER_API_KEY",
    ]
    
    def __init__(self):
        self._found_keys: list[str] = []
        self._invalid_keys: list[str] = []
        self._config_keys: list[str] = []
        self._env_file_keys: list[str] = []
        self._env_file_path: Path | None = None
    
    def _check_env_keys(self) -> tuple[list[str], list[str]]:
        """Check environment variables for API keys."""
        found = []
        invalid = []
        
        for key_name in self.ENV_KEYS:
            value = os.environ.get(key_name)
            if value:
                # Basic validation
                pattern = self.KEY_PATTERNS.get(key_name)
                if pattern and not re.match(pattern, value):
                    invalid.append(key_name)
                else:
                    found.append(key_name)
        
        return found, invalid
    
    def _check_env_file(self) -> tuple[list[str], Path | None]:
        """Check for API keys in OpenClaw .env file."""
        home = Path.home()
        env_paths = [
            home / ".openclaw" / ".env",
            home / ".openclaw" / "env",
            home / ".config" / "openclaw" / ".env",
            Path.cwd() / ".env",  # Also check current directory
        ]
        
        if sys.platform == "win32":
            env_paths.append(home / "AppData" / "Local" / "openclaw" / ".env")
        
        for env_path in env_paths:
            if env_path.exists():
                try:
                    found = []
                    with open(env_path, encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            # Skip comments and empty lines
                            if not line or line.startswith("#"):
                                continue
                            # Parse KEY=value format
                            if "=" in line:
                                key = line.split("=", 1)[0].strip()
                                if key in self.ENV_KEYS:
                                    found.append(f"{key} (in .env)")
                    if found:
                        return found, env_path
                except Exception:
                    pass
        
        return [], None
    
    def _check_config_keys(self) -> list[str]:
        """Check for API keys in OpenClaw config."""
        home = Path.home()
        config_paths = [
            home / ".openclaw" / "config.yaml",
            home / ".openclaw" / "config.yml",
            home / ".config" / "openclaw" / "config.yaml",
        ]
        
        if sys.platform == "win32":
            config_paths.append(home / "AppData" / "Local" / "openclaw" / "config.yaml")
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        config = yaml.safe_load(f)
                    
                    if config:
                        found = []
                        # Check for api_key or provider-specific keys
                        if config.get("api_key"):
                            found.append("api_key (in config)")
                        if config.get("anthropic", {}).get("api_key"):
                            found.append("anthropic.api_key")
                        if config.get("openai", {}).get("api_key"):
                            found.append("openai.api_key")
                        return found
                except Exception:
                    pass
        
        return []
    
    def run(self) -> CheckResult:
        """Run the API keys check."""
        self._found_keys, self._invalid_keys = self._check_env_keys()
        self._env_file_keys, self._env_file_path = self._check_env_file()
        self._config_keys = self._check_config_keys()
        
        all_keys = self._found_keys + self._env_file_keys + self._config_keys
        
        if self._invalid_keys:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message=f"Some API keys appear invalid: {', '.join(self._invalid_keys)}",
                details="Keys may be malformed or using old format",
                fix_suggestions=[
                    "Verify your API keys are correct",
                    "Get new keys from your AI provider's dashboard",
                ],
            )
        
        if not all_keys:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message="No AI provider API keys found",
                details="OpenClaw requires at least one AI provider API key",
                can_auto_fix=True,
                fix_suggestions=[
                    "Set environment variable: export ANTHROPIC_API_KEY=your_key",
                    "Or create ~/.openclaw/.env file with your keys",
                    "Or add to ~/.openclaw/config.yaml",
                    "Get API keys from:",
                    "  - Anthropic: https://console.anthropic.com/",
                    "  - OpenAI: https://platform.openai.com/",
                    "  - Google: https://aistudio.google.com/",
                ],
            )
        
        # Mask keys for display
        masked = [self._mask_key_name(k) for k in all_keys]
        
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            message=f"API keys configured ({len(all_keys)} found)",
            details=f"Found: {', '.join(masked)}",
        )
    
    def _mask_key_name(self, key_name: str) -> str:
        """Return a safe display name for the key."""
        # Just return the key name, not the value
        return key_name.replace("_API_KEY", "").replace("_", " ").title()
    
    def fix(self) -> bool:
        """Guide user to set up API keys."""
        from ..console import console, print_suggestion
        
        console.print("\n[bold]Setting up AI Provider API Keys[/bold]\n")
        
        print_suggestion(
            "Get an API Key",
            [
                "[bold]Anthropic (Claude)[/bold] - Recommended",
                "  Visit: https://console.anthropic.com/",
                "  Set: export ANTHROPIC_API_KEY=sk-ant-...",
                "",
                "[bold]OpenAI (GPT)[/bold]",
                "  Visit: https://platform.openai.com/api-keys",
                "  Set: export OPENAI_API_KEY=sk-...",
                "",
                "[bold]Google (Gemini)[/bold]",
                "  Visit: https://aistudio.google.com/apikey",
                "  Set: export GOOGLE_API_KEY=AIza...",
                "",
                "[bold]Groq (Llama/Mixtral)[/bold]",
                "  Visit: https://console.groq.com/keys",
                "  Set: export GROQ_API_KEY=gsk_...",
            ]
        )
        
        if sys.platform == "win32":
            console.print("\n[dim]On Windows, use:[/dim]")
            console.print("[dim]  $env:ANTHROPIC_API_KEY = 'your_key'[/dim]")
            console.print("[dim]Or set via System Environment Variables[/dim]")
        else:
            console.print("\n[dim]Add to your ~/.bashrc or ~/.zshrc for persistence[/dim]")
        
        return False
