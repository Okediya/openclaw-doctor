"""Network connectivity check."""

import httpx

from .base import BaseCheck, CheckResult, CheckStatus


class NetworkCheck(BaseCheck):
    """Check network connectivity to AI providers."""
    
    name = "Network"
    description = "Tests connectivity to AI providers"
    
    # Endpoints to test
    ENDPOINTS = {
        "Anthropic": "https://api.anthropic.com",
        "OpenAI": "https://api.openai.com",
        "Google AI": "https://generativelanguage.googleapis.com",
        "Groq": "https://api.groq.com",
    }
    
    def __init__(self):
        self._reachable: list[str] = []
        self._unreachable: list[str] = []
    
    def run(self) -> CheckResult:
        """Run the network connectivity check."""
        self._reachable = []
        self._unreachable = []
        
        for name, url in self.ENDPOINTS.items():
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.head(url)
                    # Any response (even 4xx for auth) means we can reach the server
                    self._reachable.append(name)
            except httpx.TimeoutException:
                self._unreachable.append(f"{name} (timeout)")
            except httpx.ConnectError:
                self._unreachable.append(f"{name} (connection failed)")
            except Exception as e:
                self._unreachable.append(f"{name} ({type(e).__name__})")
        
        if not self._reachable:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                message="Cannot reach any AI providers",
                details="All connection attempts failed",
                fix_suggestions=self._get_suggestions(),
            )
        
        if self._unreachable:
            return CheckResult(
                name=self.name,
                status=CheckStatus.WARN,
                message=f"Some providers unreachable: {', '.join(self._unreachable)}",
                details=f"Reachable: {', '.join(self._reachable)}",
                fix_suggestions=self._get_suggestions(),
            )
        
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            message="Network connectivity OK",
            details=f"Reachable: {', '.join(self._reachable)}",
        )
    
    def _get_suggestions(self) -> list[str]:
        """Get network troubleshooting suggestions."""
        return [
            "Check your internet connection",
            "If behind a proxy, configure HTTP_PROXY and HTTPS_PROXY",
            "Check if firewall is blocking outbound connections",
            "Try: curl https://api.anthropic.com to test manually",
        ]
    
    def fix(self) -> bool:
        """Cannot auto-fix network issues."""
        from ..console import print_suggestion
        
        print_suggestion(
            "Network Troubleshooting",
            self._get_suggestions()
        )
        return False
