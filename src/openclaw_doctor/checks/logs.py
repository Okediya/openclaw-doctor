"""OpenClaw logs parsing check."""

import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from .base import BaseCheck, CheckResult, CheckStatus


@dataclass
class LogError:
    """Represents a parsed error from logs."""
    pattern: str
    message: str
    explanation: str
    suggestion: str
    severity: str = "error"  # error, warning, info


# Common error patterns with plain language explanations
ERROR_PATTERNS: list[LogError] = [
    # API Rate Limits
    LogError(
        pattern=r"rate.?limit|too.?many.?requests|429",
        message="API rate limit exceeded",
        explanation="You've made too many API calls in a short time period.",
        suggestion="Wait a few minutes before trying again, or upgrade your API plan for higher limits.",
        severity="warning",
    ),
    # Authentication Errors
    LogError(
        pattern=r"invalid.?api.?key|unauthorized|401|authentication.?failed",
        message="API authentication failed",
        explanation="Your API key is invalid, expired, or not authorized.",
        suggestion="Check your API key in the config or environment variables. Get a new key from your provider's dashboard.",
        severity="error",
    ),
    LogError(
        pattern=r"insufficient.?quota|billing|payment.?required|402",
        message="Billing/quota issue",
        explanation="Your API account has run out of credits or has a billing problem.",
        suggestion="Add credits to your API account or check your payment method.",
        severity="error",
    ),
    # Connection Errors
    LogError(
        pattern=r"connection.?refused|ECONNREFUSED",
        message="Connection refused",
        explanation="Could not connect to the server. The service may be down.",
        suggestion="Check your internet connection. Try again in a few minutes.",
        severity="error",
    ),
    LogError(
        pattern=r"connection.?timeout|ETIMEDOUT|timed?.?out",
        message="Connection timeout",
        explanation="The server took too long to respond.",
        suggestion="Check your internet connection. The service may be experiencing high load.",
        severity="warning",
    ),
    LogError(
        pattern=r"ENOTFOUND|DNS|name.?resolution",
        message="DNS resolution failed",
        explanation="Could not find the server's address.",
        suggestion="Check your internet connection and DNS settings.",
        severity="error",
    ),
    LogError(
        pattern=r"ssl|certificate|TLS|CERT",
        message="SSL/TLS certificate error",
        explanation="There's a problem with the secure connection.",
        suggestion="Check your system date/time is correct. Your firewall may be intercepting traffic.",
        severity="error",
    ),
    # OpenClaw Specific
    LogError(
        pattern=r"config.?not.?found|missing.?config",
        message="Configuration not found",
        explanation="OpenClaw couldn't find its configuration file.",
        suggestion="Run 'openclaw init' to create a new configuration.",
        severity="error",
    ),
    LogError(
        pattern=r"invalid.?yaml|yaml.?parse|syntax.?error",
        message="Configuration syntax error",
        explanation="Your config file has invalid YAML syntax.",
        suggestion="Check config.yaml for typos. Use a YAML validator to find errors.",
        severity="error",
    ),
    LogError(
        pattern=r"permission.?denied|EACCES|access.?denied",
        message="Permission denied",
        explanation="OpenClaw doesn't have permission to access a file or directory.",
        suggestion="Check file permissions. On Unix: chmod 755 ~/.openclaw",
        severity="error",
    ),
    LogError(
        pattern=r"out.?of.?memory|ENOMEM|memory.?limit",
        message="Out of memory",
        explanation="The system ran out of available memory.",
        suggestion="Close other applications. Consider increasing system RAM.",
        severity="error",
    ),
    LogError(
        pattern=r"model.?not.?found|invalid.?model",
        message="AI model not found",
        explanation="The specified AI model doesn't exist or isn't available.",
        suggestion="Check the model name in your config. Use 'openclaw models' to see available options.",
        severity="error",
    ),
    LogError(
        pattern=r"context.?length|token.?limit|too.?long",
        message="Context length exceeded",
        explanation="Your message or conversation is too long for the AI model.",
        suggestion="Try a shorter message or start a new conversation.",
        severity="warning",
    ),
    LogError(
        pattern=r"skill.?failed|skill.?error",
        message="Skill execution failed",
        explanation="One of OpenClaw's skills encountered an error.",
        suggestion="Check the skill's configuration. Try disabling and re-enabling the skill.",
        severity="warning",
    ),
    LogError(
        pattern=r"channel.?disconnected|channel.?error",
        message="Messaging channel error",
        explanation="There's a problem with a messaging channel (WhatsApp, Telegram, etc.).",
        suggestion="Re-authenticate the channel. Check your API tokens.",
        severity="warning",
    ),
]


class LogsCheck(BaseCheck):
    """Check OpenClaw logs for common errors and explain them."""
    
    name = "Logs"
    description = "Parses logs for errors with explanations"
    
    # How far back to look in logs
    MAX_LOG_AGE_HOURS = 24
    MAX_ERRORS_TO_SHOW = 5
    
    def __init__(self):
        self._log_dir: Path | None = None
        self._log_files: list[Path] = []
        self._found_errors: list[tuple[LogError, str, Path]] = []
    
    def _find_log_directory(self) -> Path | None:
        """Find OpenClaw log directory."""
        home = Path.home()
        
        possible_paths = [
            home / ".openclaw" / "logs",
            home / ".openclaw" / "log",
            home / ".config" / "openclaw" / "logs",
        ]
        
        if sys.platform == "win32":
            possible_paths.extend([
                home / "AppData" / "Local" / "openclaw" / "logs",
                home / "AppData" / "Roaming" / "openclaw" / "logs",
            ])
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return path
        
        return None
    
    def _find_log_files(self, log_dir: Path) -> list[Path]:
        """Find recent log files."""
        log_files = []
        cutoff_time = datetime.now() - timedelta(hours=self.MAX_LOG_AGE_HOURS)
        
        # Look for common log file patterns
        patterns = ["*.log", "*.txt", "error*", "openclaw*"]
        
        for pattern in patterns:
            for log_file in log_dir.glob(pattern):
                if log_file.is_file():
                    try:
                        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if mtime > cutoff_time:
                            log_files.append(log_file)
                    except Exception:
                        pass
        
        return sorted(log_files, key=lambda f: f.stat().st_mtime, reverse=True)
    
    def _parse_log_file(self, log_file: Path) -> list[tuple[LogError, str]]:
        """Parse a log file for known error patterns."""
        errors_found = []
        
        try:
            # Read last portion of large files
            max_bytes = 100 * 1024  # 100KB max per file
            
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                # Seek to end minus max_bytes for large files
                f.seek(0, 2)  # Go to end
                file_size = f.tell()
                if file_size > max_bytes:
                    f.seek(file_size - max_bytes)
                    f.readline()  # Skip partial line
                else:
                    f.seek(0)
                
                content = f.read()
            
            # Check each error pattern
            for error in ERROR_PATTERNS:
                if re.search(error.pattern, content, re.IGNORECASE):
                    # Find the actual line containing the error
                    for line in content.split("\n"):
                        if re.search(error.pattern, line, re.IGNORECASE):
                            errors_found.append((error, line.strip()[:100]))
                            break
                    else:
                        errors_found.append((error, ""))
        
        except Exception:
            pass
        
        return errors_found
    
    def run(self) -> CheckResult:
        """Run the logs check."""
        self._log_dir = self._find_log_directory()
        self._log_files = []
        self._found_errors = []
        
        if not self._log_dir:
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASS,
                message="No log directory found (OK if OpenClaw is new)",
                details="Logs will appear in ~/.openclaw/logs/ after using OpenClaw",
            )
        
        self._log_files = self._find_log_files(self._log_dir)
        
        if not self._log_files:
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASS,
                message="No recent logs found",
                details=f"Checked {self._log_dir} for logs from last {self.MAX_LOG_AGE_HOURS}h",
            )
        
        # Parse each log file
        for log_file in self._log_files[:5]:  # Check up to 5 most recent
            errors = self._parse_log_file(log_file)
            for error, line in errors:
                self._found_errors.append((error, line, log_file))
        
        if not self._found_errors:
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASS,
                message=f"No errors in recent logs ({len(self._log_files)} files checked)",
                details=f"Log directory: {self._log_dir}",
            )
        
        # Count by severity
        error_count = sum(1 for e, _, _ in self._found_errors if e.severity == "error")
        warning_count = sum(1 for e, _, _ in self._found_errors if e.severity == "warning")
        
        status = CheckStatus.FAIL if error_count > 0 else CheckStatus.WARN
        
        # Build details
        unique_errors = {}
        for error, line, file in self._found_errors:
            if error.message not in unique_errors:
                unique_errors[error.message] = (error, line, file)
        
        details_lines = []
        for msg, (error, line, file) in list(unique_errors.items())[:self.MAX_ERRORS_TO_SHOW]:
            details_lines.append(f"• {error.message}: {error.explanation}")
        
        return CheckResult(
            name=self.name,
            status=status,
            message=f"Found {len(unique_errors)} issue(s) in logs",
            details="\n".join(details_lines),
            fix_suggestions=[e.suggestion for e, _, _ in list(unique_errors.values())[:3]],
        )
    
    def fix(self) -> bool:
        """Display detailed error explanations."""
        from ..console import console, print_suggestion
        
        if not self._found_errors:
            console.print("[green]No errors found in logs![/green]")
            return True
        
        console.print("\n[bold]Log Error Analysis[/bold]\n")
        
        # Group by unique error
        unique_errors = {}
        for error, line, file in self._found_errors:
            if error.message not in unique_errors:
                unique_errors[error.message] = (error, line, file)
        
        for i, (msg, (error, line, file)) in enumerate(unique_errors.items(), 1):
            severity_color = "red" if error.severity == "error" else "yellow"
            
            console.print(f"[bold {severity_color}]{i}. {error.message}[/bold {severity_color}]")
            console.print(f"   [dim]File: {file.name}[/dim]")
            if line:
                console.print(f"   [dim]Line: {line[:80]}...[/dim]" if len(line) > 80 else f"   [dim]Line: {line}[/dim]")
            console.print()
            console.print(f"   [white]What happened:[/white] {error.explanation}")
            console.print(f"   [green]How to fix:[/green] {error.suggestion}")
            console.print()
        
        return False
