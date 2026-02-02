"""OpenClaw installation check."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from .base import BaseCheck, CheckResult, CheckStatus


class OpenClawCheck(BaseCheck):
    """Check if OpenClaw is installed and functioning."""
    
    name = "OpenClaw"
    description = "Checks OpenClaw CLI installation"
    
    def __init__(self):
        self._version: str | None = None
        self._path: str | None = None
        self._home_dir: Path | None = None
    
    def _get_openclaw_info(self) -> tuple[str | None, str | None]:
        """Get OpenClaw path and version."""
        # Check for openclaw CLI
        openclaw_path = shutil.which("openclaw")
        if not openclaw_path:
            # Also check common alternative names
            for name in ["openclaw", "oc", "claw"]:
                openclaw_path = shutil.which(name)
                if openclaw_path:
                    break
        
        if not openclaw_path:
            return None, None
        
        try:
            result = subprocess.run(
                [openclaw_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                # Clean up version string
                if version.startswith("openclaw"):
                    version = version.replace("openclaw", "").strip()
                if version.startswith("v"):
                    version = version[1:]
                return openclaw_path, version
            return openclaw_path, None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return openclaw_path, None
    
    def _get_home_directory(self) -> Path | None:
        """Get the OpenClaw home directory."""
        # Check common locations
        home = Path.home()
        
        possible_paths = [
            home / ".openclaw",
            home / ".config" / "openclaw",
            home / "AppData" / "Local" / "openclaw" if sys.platform == "win32" else None,
        ]
        
        for path in possible_paths:
            if path and path.exists():
                return path
        
        return None
    
    def run(self) -> CheckResult:
        """Run the OpenClaw check."""
        self._path, self._version = self._get_openclaw_info()
        self._home_dir = self._get_home_directory()
        
        if not self._path:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                message="OpenClaw CLI is not installed",
                can_auto_fix=True,
                fix_suggestions=[
                    "Run the OpenClaw installer:",
                    "curl -fsSL https://openclawd.ai/install.sh | bash",
                    "Or visit: https://github.com/openclaw/openclaw",
                ],
            )
        
        if not self._version:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message="OpenClaw found but version could not be determined",
                details=f"Path: {self._path}",
                fix_suggestions=["Try running 'openclaw --version' manually"],
            )
        
        details = f"Path: {self._path}"
        if self._home_dir:
            details += f"\nHome: {self._home_dir}"
        
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            message=f"OpenClaw v{self._version} installed",
            details=details,
        )
    
    def fix(self) -> bool:
        """Attempt to install OpenClaw."""
        from ..console import console, print_fix_action, print_suggestion
        
        if sys.platform == "win32":
            print_suggestion(
                "Install OpenClaw on Windows",
                [
                    "Open PowerShell as Administrator",
                    "Run: iwr -useb https://openclawd.ai/install.ps1 | iex",
                    "Or download from: https://github.com/openclaw/openclaw/releases",
                ]
            )
            return False
        
        # On Unix-like systems, offer to run the install script
        print_fix_action("Attempting to install OpenClaw...")
        
        try:
            console.print("[dim]Running install script...[/dim]")
            result = subprocess.run(
                ["bash", "-c", "curl -fsSL https://openclawd.ai/install.sh | bash"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode == 0:
                console.print("[green]OpenClaw installed successfully![/green]")
                return True
            else:
                console.print(f"[red]Installation failed:[/red] {result.stderr}")
                print_suggestion(
                    "Manual Installation",
                    [
                        "Visit: https://github.com/openclaw/openclaw",
                        "Follow the installation instructions for your OS",
                    ]
                )
                return False
        except subprocess.TimeoutExpired:
            console.print("[red]Installation timed out[/red]")
            return False
        except FileNotFoundError:
            print_suggestion(
                "Install OpenClaw",
                [
                    "curl -fsSL https://openclawd.ai/install.sh | bash",
                    "Or visit: https://github.com/openclaw/openclaw",
                ]
            )
            return False
