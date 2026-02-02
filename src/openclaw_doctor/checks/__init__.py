"""Health checks package."""

from .base import BaseCheck, CheckResult, CheckStatus
from .nodejs import NodeJSCheck
from .openclaw import OpenClawCheck
from .docker import DockerCheck
from .system import SystemCheck
from .config import ConfigCheck
from .api_keys import APIKeysCheck
from .network import NetworkCheck

# All available checks in order
ALL_CHECKS: list[type[BaseCheck]] = [
    NodeJSCheck,
    OpenClawCheck,
    DockerCheck,
    SystemCheck,
    ConfigCheck,
    APIKeysCheck,
    NetworkCheck,
]

__all__ = [
    "BaseCheck",
    "CheckResult",
    "CheckStatus",
    "ALL_CHECKS",
    "NodeJSCheck",
    "OpenClawCheck",
    "DockerCheck",
    "SystemCheck",
    "ConfigCheck",
    "APIKeysCheck",
    "NetworkCheck",
]
