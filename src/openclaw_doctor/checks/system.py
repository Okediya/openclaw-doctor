"""System requirements check (RAM, disk space, CPU)."""

import shutil
import sys

import psutil

from .base import BaseCheck, CheckResult, CheckStatus


class SystemCheck(BaseCheck):
    """Check system requirements for OpenClaw."""
    
    name = "System"
    description = "RAM (2GB+), Disk (20GB+), CPU"
    
    # Minimum requirements
    MIN_RAM_GB = 2
    RECOMMENDED_RAM_GB = 4
    MIN_DISK_GB = 20
    MIN_CPU_CORES = 2
    
    def __init__(self):
        self._ram_gb: float = 0
        self._disk_gb: float = 0
        self._cpu_cores: int = 0
        self._issues: list[str] = []
        self._warnings: list[str] = []
    
    def run(self) -> CheckResult:
        """Run the system requirements check."""
        self._issues = []
        self._warnings = []
        
        # Check RAM
        mem = psutil.virtual_memory()
        self._ram_gb = mem.total / (1024 ** 3)
        
        if self._ram_gb < self.MIN_RAM_GB:
            self._issues.append(f"RAM: {self._ram_gb:.1f}GB (minimum {self.MIN_RAM_GB}GB required)")
        elif self._ram_gb < self.RECOMMENDED_RAM_GB:
            self._warnings.append(f"RAM: {self._ram_gb:.1f}GB (recommended {self.RECOMMENDED_RAM_GB}GB+)")
        
        # Check disk space
        if sys.platform == "win32":
            path = "C:\\"
        else:
            path = "/"
        
        disk = shutil.disk_usage(path)
        self._disk_gb = disk.free / (1024 ** 3)
        
        if self._disk_gb < self.MIN_DISK_GB:
            self._issues.append(f"Disk: {self._disk_gb:.1f}GB free (minimum {self.MIN_DISK_GB}GB required)")
        
        # Check CPU cores
        self._cpu_cores = psutil.cpu_count(logical=False) or psutil.cpu_count() or 1
        
        if self._cpu_cores < self.MIN_CPU_CORES:
            self._warnings.append(f"CPU: {self._cpu_cores} cores (recommended {self.MIN_CPU_CORES}+)")
        
        # Build result
        if self._issues:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                message="System does not meet minimum requirements",
                details="\n".join(self._issues + self._warnings),
                fix_suggestions=self._get_suggestions(),
            )
        
        summary = f"{self._ram_gb:.1f}GB RAM, {self._disk_gb:.0f}GB free, {self._cpu_cores} cores"
        
        if self._warnings:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message=f"System meets minimum requirements ({summary})",
                details="\n".join(self._warnings),
                fix_suggestions=self._get_suggestions(),
            )
        
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            message=f"System requirements met ({summary})",
        )
    
    def _get_suggestions(self) -> list[str]:
        """Get suggestions for system improvements."""
        suggestions = []
        
        if self._ram_gb < self.RECOMMENDED_RAM_GB:
            suggestions.append(f"Consider upgrading to {self.RECOMMENDED_RAM_GB}GB+ RAM for better performance")
        
        if self._disk_gb < self.MIN_DISK_GB:
            suggestions.extend([
                "Free up disk space by:",
                "  - Removing unused applications",
                "  - Clearing temporary files",
                "  - Moving large files to external storage",
            ])
        
        return suggestions
    
    def fix(self) -> bool:
        """Cannot auto-fix hardware limitations."""
        from ..console import print_suggestion
        
        print_suggestion(
            "System Requirements",
            self._get_suggestions() if self._get_suggestions() else [
                "Your system meets the minimum requirements.",
                "For best performance, ensure you have 4GB+ RAM and 20GB+ free disk space.",
            ]
        )
        return False
