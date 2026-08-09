import platform
import shutil
import subprocess


class ClaudeDiscovery:
    """Discovers local Claude Code CLI installations."""

    @staticmethod
    def is_installed() -> bool:
        # Use shutil.which to see if claude is in the system PATH
        # Sometimes it's installed via npm as 'claude'
        return (
            shutil.which("claude") is not None or shutil.which("claude.cmd") is not None
        )

    @staticmethod
    def get_executable_path() -> str | None:
        return shutil.which("claude") or shutil.which("claude.cmd")

    @staticmethod
    def get_version() -> str:
        exec_path = ClaudeDiscovery.get_executable_path()
        if not exec_path:
            return "unknown"

        try:
            result = subprocess.run(
                [exec_path, "--version"], capture_output=True, text=True, timeout=2, check=False
            )
            if result.returncode == 0:
                # The output might be something like "@anthropic-ai/claude-code 0.2.29"
                return result.stdout.strip()
            return "unknown"
        except (subprocess.SubprocessError, OSError):
            return "unknown"

    @staticmethod
    def get_platform() -> str:
        return platform.system()

    @staticmethod
    def get_metadata() -> dict[str, str]:
        return {
            "is_installed": str(ClaudeDiscovery.is_installed()),
            "executable_path": ClaudeDiscovery.get_executable_path() or "",
            "version": ClaudeDiscovery.get_version(),
            "os_platform": ClaudeDiscovery.get_platform(),
        }
