"""Base check class and result types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class CheckStatus(Enum):
    """Status of a health check."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class CheckResult:
    """Result of a health check."""
    name: str
    status: CheckStatus
    message: str
    details: str | None = None
    can_auto_fix: bool = False
    fix_suggestions: list[str] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Check if the result is passing (pass or warn)."""
        return self.status in (CheckStatus.PASS, CheckStatus.WARN)
    
    @property
    def is_warning(self) -> bool:
        """Check if the result is a warning."""
        return self.status == CheckStatus.WARN
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "can_auto_fix": self.can_auto_fix,
            "fix_suggestions": self.fix_suggestions,
        }


class BaseCheck(ABC):
    """Base class for all health checks."""
    
    name: str = "Base Check"
    description: str = "A health check"
    
    @abstractmethod
    def run(self) -> CheckResult:
        """Run the health check and return the result."""
        pass
    
    @abstractmethod
    def fix(self) -> bool:
        """Attempt to fix the issue. Returns True if fixed."""
        pass
    
    def get_fix_callback(self) -> Callable[[], bool] | None:
        """Get a callback function for fixing the issue."""
        return self.fix
