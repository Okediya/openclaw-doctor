"""Node.js version check."""

import re
import shutil
import subprocess
import sys

from .base import BaseCheck, CheckResult, CheckStatus


class NodeJSCheck(BaseCheck):
    """Check if Node.js is installed and meets version requirements."""
    
    name = "Node.js"
    description = "Verifies Node.js >= 18.x is installed"
    min_version = (18, 0, 0)
    
    def __init__(self):
        self._version: tuple[int, ...] | None = None
        self._path: str | None = None
    
    def _get_node_info(self) -> tuple[str | None, tuple[int, ...] | None]:
        """Get Node.js path and version."""
        node_path = shutil.which("node")
        if not node_path:
            return None, None
        
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return node_path, None
            
            # Parse version string like "v20.10.0"
            version_str = result.stdout.strip()
            match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", version_str)
            if match:
                version = tuple(int(x) for x in match.groups())
                return node_path, version
            return node_path, None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return node_path, None
    
    def run(self) -> CheckResult:
        """Run the Node.js check."""
        self._path, self._version = self._get_node_info()
        
        if not self._path:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                message="Node.js is not installed",
                details="OpenClaw requires Node.js >= 18.x",
                can_auto_fix=True,
                fix_suggestions=self._get_install_suggestions(),
            )
        
        if not self._version:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message="Node.js found but version could not be determined",
                details=f"Path: {self._path}",
                fix_suggestions=["Try running 'node --version' manually"],
            )
        
        version_str = ".".join(str(v) for v in self._version)
        
        if self._version < self.min_version:
            min_str = ".".join(str(v) for v in self.min_version)
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                message=f"Node.js v{version_str} is below minimum v{min_str}",
                can_auto_fix=True,
                fix_suggestions=self._get_install_suggestions(),
            )
        
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            message=f"Node.js v{version_str} installed",
            details=f"Path: {self._path}",
        )
    
    def _get_install_suggestions(self) -> list[str]:
        """Get platform-specific installation suggestions."""
        if sys.platform == "darwin":
            return [
                "Install via Homebrew: brew install node",
                "Or use nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
                "Then: nvm install 20",
            ]
        elif sys.platform == "win32":
            return [
                "Download from: https://nodejs.org/en/download/",
                "Or use winget: winget install OpenJS.NodeJS.LTS",
                "Or use nvm-windows: https://github.com/coreybutler/nvm-windows",
            ]
        else:  # Linux
            return [
                "Install via nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
                "Then: nvm install 20",
                "Or via package manager (Ubuntu): sudo apt install nodejs npm",
            ]
    
    def fix(self) -> bool:
        """Attempt to fix Node.js installation."""
        from ..console import console, print_suggestion
        
        print_suggestion(
            "Install Node.js",
            self._get_install_suggestions()
        )
        
        # Can't auto-install Node.js, but we show suggestions
        console.print("\n[dim]After installing Node.js, run openclaw-doctor again.[/dim]")
        return False
