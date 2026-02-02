"""Tests for OpenClaw Doctor health checks."""

import pytest

from openclaw_doctor.checks import (
    ALL_CHECKS,
    BaseCheck,
    CheckResult,
    CheckStatus,
    NodeJSCheck,
    SystemCheck,
    NetworkCheck,
)


class TestCheckResult:
    """Test CheckResult dataclass."""
    
    def test_passed_when_pass(self):
        result = CheckResult(
            name="Test",
            status=CheckStatus.PASS,
            message="OK",
        )
        assert result.passed is True
        assert result.is_warning is False
    
    def test_passed_when_warn(self):
        result = CheckResult(
            name="Test",
            status=CheckStatus.WARN,
            message="Warning",
        )
        assert result.passed is True
        assert result.is_warning is True
    
    def test_not_passed_when_fail(self):
        result = CheckResult(
            name="Test",
            status=CheckStatus.FAIL,
            message="Failed",
        )
        assert result.passed is False
        assert result.is_warning is False
    
    def test_to_dict(self):
        result = CheckResult(
            name="Test",
            status=CheckStatus.PASS,
            message="OK",
            details="Details here",
            can_auto_fix=True,
            fix_suggestions=["Fix 1", "Fix 2"],
        )
        d = result.to_dict()
        assert d["name"] == "Test"
        assert d["status"] == "pass"
        assert d["message"] == "OK"
        assert d["details"] == "Details here"
        assert d["can_auto_fix"] is True
        assert d["fix_suggestions"] == ["Fix 1", "Fix 2"]


class TestAllChecks:
    """Test that all checks are properly defined."""
    
    def test_all_checks_have_name(self):
        for check_class in ALL_CHECKS:
            assert hasattr(check_class, "name")
            assert check_class.name
    
    def test_all_checks_have_description(self):
        for check_class in ALL_CHECKS:
            assert hasattr(check_class, "description")
            assert check_class.description
    
    def test_all_checks_inherit_base(self):
        for check_class in ALL_CHECKS:
            assert issubclass(check_class, BaseCheck)
    
    def test_all_checks_have_run_method(self):
        for check_class in ALL_CHECKS:
            check = check_class()
            assert hasattr(check, "run")
            assert callable(check.run)
    
    def test_all_checks_have_fix_method(self):
        for check_class in ALL_CHECKS:
            check = check_class()
            assert hasattr(check, "fix")
            assert callable(check.fix)


class TestNodeJSCheck:
    """Test Node.js check."""
    
    def test_run_returns_check_result(self):
        check = NodeJSCheck()
        result = check.run()
        assert isinstance(result, CheckResult)
        assert result.name == "Node.js"
    
    def test_min_version_is_set(self):
        check = NodeJSCheck()
        assert check.min_version >= (18, 0, 0)


class TestSystemCheck:
    """Test System requirements check."""
    
    def test_run_returns_check_result(self):
        check = SystemCheck()
        result = check.run()
        assert isinstance(result, CheckResult)
        assert result.name == "System"
    
    def test_requirements_are_set(self):
        check = SystemCheck()
        assert check.MIN_RAM_GB >= 2
        assert check.MIN_DISK_GB >= 20
        assert check.MIN_CPU_CORES >= 2


class TestNetworkCheck:
    """Test Network connectivity check."""
    
    def test_run_returns_check_result(self):
        check = NetworkCheck()
        result = check.run()
        assert isinstance(result, CheckResult)
        assert result.name == "Network"
    
    def test_endpoints_defined(self):
        check = NetworkCheck()
        assert len(check.ENDPOINTS) > 0
        assert "Anthropic" in check.ENDPOINTS
