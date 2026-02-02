"""Common fix utilities."""

import subprocess
import sys


def run_command(cmd: list[str], timeout: int = 60) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, str(e)


def open_url(url: str) -> bool:
    """Open a URL in the default browser."""
    import webbrowser
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def is_admin() -> bool:
    """Check if running with admin/sudo privileges."""
    if sys.platform == "win32":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        import os
        return os.geteuid() == 0
