"""OpenClaw folder structure check."""

import os
import sys
from pathlib import Path

from .base import BaseCheck, CheckResult, CheckStatus


class FoldersCheck(BaseCheck):
    """Check OpenClaw folder structure and directories."""
    
    name = "Folders"
    description = "Checks OpenClaw directory structure"
    
    # Expected directories in OpenClaw home
    EXPECTED_DIRS = [
        "skills",
        "channels", 
        "workspaces",
    ]
    
    # Expected files
    EXPECTED_FILES = [
        "config.yaml",
    ]
    
    def __init__(self):
        self._home_dir: Path | None = None
        self._missing_dirs: list[str] = []
        self._missing_files: list[str] = []
        self._found_dirs: list[str] = []
        self._found_files: list[str] = []
        self._permission_issues: list[str] = []
    
    def _find_openclaw_home(self) -> Path | None:
        """Find the OpenClaw home directory."""
        home = Path.home()
        
        possible_paths = [
            home / ".openclaw",
            home / ".config" / "openclaw",
        ]
        
        if sys.platform == "win32":
            possible_paths.append(home / "AppData" / "Local" / "openclaw")
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _check_permissions(self, path: Path) -> bool:
        """Check if path is readable and writable."""
        try:
            # Check read
            if not os.access(path, os.R_OK):
                return False
            # Check write
            if not os.access(path, os.W_OK):
                return False
            return True
        except Exception:
            return False
    
    def run(self) -> CheckResult:
        """Run the folder structure check."""
        self._home_dir = self._find_openclaw_home()
        self._missing_dirs = []
        self._missing_files = []
        self._found_dirs = []
        self._found_files = []
        self._permission_issues = []
        
        if not self._home_dir:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message="OpenClaw home directory not found",
                details="Expected ~/.openclaw or similar",
                can_auto_fix=True,
                fix_suggestions=[
                    "Run 'openclaw init' to create the directory structure",
                    "Or manually create ~/.openclaw/",
                ],
            )
        
        # Check home directory permissions
        if not self._check_permissions(self._home_dir):
            self._permission_issues.append(str(self._home_dir))
        
        # Check expected directories
        for dir_name in self.EXPECTED_DIRS:
            dir_path = self._home_dir / dir_name
            if dir_path.exists():
                self._found_dirs.append(dir_name)
                if not self._check_permissions(dir_path):
                    self._permission_issues.append(str(dir_path))
            else:
                self._missing_dirs.append(dir_name)
        
        # Check expected files
        for file_name in self.EXPECTED_FILES:
            file_path = self._home_dir / file_name
            if file_path.exists():
                self._found_files.append(file_name)
            else:
                # Also check .yml extension
                if file_name.endswith(".yaml"):
                    yml_path = self._home_dir / file_name.replace(".yaml", ".yml")
                    if yml_path.exists():
                        self._found_files.append(file_name.replace(".yaml", ".yml"))
                    else:
                        self._missing_files.append(file_name)
                else:
                    self._missing_files.append(file_name)
        
        # Build result
        if self._permission_issues:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                message=f"Permission issues in {len(self._permission_issues)} path(s)",
                details=f"Issues: {', '.join(self._permission_issues)}",
                fix_suggestions=[
                    "Fix permissions with: chmod 755 ~/.openclaw",
                    "Ensure your user owns the directory",
                ],
            )
        
        details_parts = [f"Home: {self._home_dir}"]
        if self._found_dirs:
            details_parts.append(f"Dirs: {', '.join(self._found_dirs)}")
        if self._found_files:
            details_parts.append(f"Files: {', '.join(self._found_files)}")
        
        if self._missing_dirs or self._missing_files:
            missing = self._missing_dirs + self._missing_files
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message=f"OpenClaw structure incomplete ({len(missing)} missing)",
                details="\n".join(details_parts) + f"\nMissing: {', '.join(missing)}",
                can_auto_fix=True,
                fix_suggestions=[
                    "Run 'openclaw init' to create missing directories",
                    f"Or manually create: {', '.join(self._missing_dirs)}",
                ],
            )
        
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            message="OpenClaw folder structure OK",
            details="\n".join(details_parts),
        )
    
    def fix(self) -> bool:
        """Attempt to create missing directories."""
        from ..console import console, print_fix_action, print_success
        
        if not self._home_dir:
            # Create home directory
            home = Path.home()
            self._home_dir = home / ".openclaw"
            
            print_fix_action(f"Creating OpenClaw home: {self._home_dir}")
            try:
                self._home_dir.mkdir(parents=True, exist_ok=True)
                print_success(f"Created {self._home_dir}")
            except Exception as e:
                console.print(f"[red]Failed to create directory:[/red] {e}")
                return False
        
        # Create missing directories
        created = []
        for dir_name in self._missing_dirs:
            dir_path = self._home_dir / dir_name
            print_fix_action(f"Creating directory: {dir_path}")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                created.append(dir_name)
            except Exception as e:
                console.print(f"[red]Failed to create {dir_name}:[/red] {e}")
        
        if created:
            print_success(f"Created directories: {', '.join(created)}")
            return True
        
        return len(self._missing_dirs) == 0
