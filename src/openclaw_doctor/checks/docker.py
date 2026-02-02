"""Docker and Docker Compose check."""

import shutil
import subprocess
import sys

from .base import BaseCheck, CheckResult, CheckStatus


class DockerCheck(BaseCheck):
    """Check if Docker and Docker Compose are installed and running."""
    
    name = "Docker"
    description = "Validates Docker & Compose setup (optional)"
    
    def __init__(self):
        self._docker_version: str | None = None
        self._compose_version: str | None = None
        self._docker_running: bool = False
    
    def _check_docker(self) -> tuple[str | None, bool]:
        """Check Docker installation and status."""
        docker_path = shutil.which("docker")
        if not docker_path:
            return None, False
        
        # Get version
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version = None
            if result.returncode == 0:
                # Parse "Docker version 24.0.7, build afdd53b"
                parts = result.stdout.strip().split(",")[0]
                version = parts.replace("Docker version", "").strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            version = None
        
        # Check if daemon is running
        running = False
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            running = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return version, running
    
    def _check_compose(self) -> str | None:
        """Check Docker Compose installation."""
        # Try docker compose (v2)
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                # Parse "Docker Compose version v2.23.0"
                version = result.stdout.strip()
                if "version" in version.lower():
                    version = version.split("version")[-1].strip()
                return version
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try docker-compose (v1)
        try:
            compose_path = shutil.which("docker-compose")
            if compose_path:
                result = subprocess.run(
                    ["docker-compose", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    return result.stdout.strip().split(",")[0].replace("docker-compose version", "").strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def run(self) -> CheckResult:
        """Run the Docker check."""
        self._docker_version, self._docker_running = self._check_docker()
        self._compose_version = self._check_compose()
        
        # Docker is optional for OpenClaw (only needed for server deployments)
        if not self._docker_version:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message="Docker is not installed (optional for desktop use)",
                details="Docker is only required for server deployments",
                fix_suggestions=self._get_install_suggestions(),
            )
        
        if not self._docker_running:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message=f"Docker {self._docker_version} installed but not running",
                can_auto_fix=True,
                fix_suggestions=["Start Docker Desktop or the Docker daemon"],
            )
        
        details = f"Docker {self._docker_version}"
        if self._compose_version:
            details += f", Compose {self._compose_version}"
        else:
            details += " (Compose not found)"
        
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            message=f"Docker {self._docker_version} running",
            details=details,
        )
    
    def _get_install_suggestions(self) -> list[str]:
        """Get platform-specific Docker installation suggestions."""
        if sys.platform == "darwin":
            return [
                "Install Docker Desktop: https://www.docker.com/products/docker-desktop/",
                "Or via Homebrew: brew install --cask docker",
            ]
        elif sys.platform == "win32":
            return [
                "Install Docker Desktop: https://www.docker.com/products/docker-desktop/",
                "Or via winget: winget install Docker.DockerDesktop",
            ]
        else:  # Linux
            return [
                "Install Docker: https://docs.docker.com/engine/install/",
                "For Ubuntu: sudo apt install docker.io docker-compose-v2",
                "Then: sudo systemctl enable --now docker",
            ]
    
    def fix(self) -> bool:
        """Attempt to fix Docker issues."""
        from ..console import console, print_fix_action, print_suggestion
        
        if not self._docker_version:
            print_suggestion("Install Docker", self._get_install_suggestions())
            return False
        
        if not self._docker_running:
            print_fix_action("Attempting to start Docker...")
            
            if sys.platform == "darwin":
                try:
                    subprocess.run(["open", "-a", "Docker"], timeout=10)
                    console.print("[dim]Docker Desktop is starting...[/dim]")
                    console.print("[dim]Please wait a moment and run openclaw-doctor again.[/dim]")
                    return True
                except Exception:
                    pass
            elif sys.platform == "linux":
                try:
                    result = subprocess.run(
                        ["sudo", "systemctl", "start", "docker"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        console.print("[green]Docker daemon started![/green]")
                        return True
                except Exception:
                    pass
            
            print_suggestion(
                "Start Docker Manually",
                [
                    "On macOS: Open Docker Desktop application",
                    "On Linux: sudo systemctl start docker",
                    "On Windows: Start Docker Desktop from Start Menu",
                ]
            )
        
        return False
