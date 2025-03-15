#!/usr/bin/env python3
"""Release management script for SignalRGB Python."""

# ruff: noqa: E501, T201

import os
import re
import shutil
import subprocess
from subprocess import CompletedProcess
import sys

from colorama import Style, init
from wcwidth import wcswidth

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Constants
PROJECT_NAME = "SignalRGB Python"
REPO_NAME = "hyperb1iss/signalrgb-python"
PROJECT_LINK = f"https://github.com/{REPO_NAME}"
ISSUE_TRACKER = f"{PROJECT_LINK}/issues"

# ANSI Color Constants
COLOR_RESET = Style.RESET_ALL
COLOR_BORDER = "\033[38;2;75;0;130m"
COLOR_STAR = "\033[38;2;255;255;0m"
COLOR_ERROR = "\033[38;2;255;0;0m"
COLOR_SUCCESS = "\033[38;2;50;205;50m"
COLOR_BUILD_SUCCESS = "\033[38;2;255;215;0m"
COLOR_VERSION_PROMPT = "\033[38;2;147;112;219m"
COLOR_STEP = "\033[38;2;255;0;130m"
COLOR_WARNING = "\033[38;2;255;165;0m"

# Gradient colors for the banner
GRADIENT_COLORS = [
    (255, 0, 0),
    (0, 0, 255),
    (0, 255, 0),
    (0, 0, 255),
    (255, 0, 0),
]

# File paths
PYPROJECT_TOML = "pyproject.toml"
DOCS_INDEX = "docs/index.md"


def print_colored(message: str, color: str) -> None:
    """Print a message with a specific color."""
    print(f"{color}{message}{COLOR_RESET}")


def print_step(step: str) -> None:
    """Print a step in the process with a specific color."""
    print_colored(f"\n✨ {step}", COLOR_STEP)


def print_error(message: str) -> None:
    """Print an error message with a specific color."""
    print_colored(f"❌ Error: {message}", COLOR_ERROR)


def print_success(message: str) -> None:
    """Print a success message with a specific color."""
    print_colored(f"✅ {message}", COLOR_SUCCESS)


def print_warning(message: str) -> None:
    """Print a warning message with a specific color."""
    print_colored(f"⚠️  {message}", COLOR_WARNING)


def generate_gradient(colors: list[tuple[int, int, int]], steps: int) -> list[str]:
    """Generate a list of color codes for a smooth multi-color gradient."""
    gradient = []
    segments = len(colors) - 1
    steps_per_segment = max(1, steps // segments)

    for i in range(segments):
        start_color = colors[i]
        end_color = colors[i + 1]
        for j in range(steps_per_segment):
            t = j / steps_per_segment
            r = int(start_color[0] * (1 - t) + end_color[0] * t)
            g = int(start_color[1] * (1 - t) + end_color[1] * t)
            b = int(start_color[2] * (1 - t) + end_color[2] * t)
            gradient.append(f"\033[38;2;{r};{g};{b}m")

    return gradient


def strip_ansi(text: str) -> str:
    """Remove ANSI color codes from a string."""
    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", text)


def apply_gradient(text: str, gradient: list[str], line_number: int) -> str:
    """Apply gradient colors diagonally to text."""
    return "".join(f"{gradient[(i + line_number) % len(gradient)]}{char}" for i, char in enumerate(text))


def center_text(text: str, width: int) -> str:
    """Center text, accounting for ANSI color codes and Unicode widths."""
    visible_length = wcswidth(strip_ansi(text))
    padding = (width - visible_length) // 2
    return f"{' ' * padding}{text}{' ' * (width - padding - visible_length)}"


def center_block(block: list[str], width: int) -> list[str]:
    """Center a block of text within a given width."""
    return [center_text(line, width) for line in block]


def create_banner() -> str:
    """Create a FULL RGB banner with diagonal gradient."""
    banner_width = 80
    content_width = banner_width - 4  # Accounting for border characters
    cosmic_gradient = generate_gradient(GRADIENT_COLORS, banner_width)

    logo = [
        "███████╗██╗ ██████╗ ███╗   ██╗ █████╗ ██╗     ██████╗  ██████╗ ██████╗ ",
        "██╔════╝██║██╔════╝ ████╗  ██║██╔══██╗██║     ██╔══██╗██╔════╝ ██╔══██╗",
        "███████╗██║██║  ███╗██╔██╗ ██║███████║██║     ██████╔╝██║  ███╗██████╔╝",
        "╚════██║██║██║   ██║██║╚██╗██║██╔══██║██║     ██╔══██╗██║   ██║██╔══██╗",
        "███████║██║╚██████╔╝██║ ╚████║██║  ██║███████╗██║  ██║╚██████╔╝██████╔╝",
        "╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ",
        center_text("🐍 Python Client Library 🐍", content_width),
    ]

    centered_logo = center_block(logo, content_width)

    banner = [
        center_text(f"{COLOR_STAR}･ ｡ ☆ ∴｡　　･ﾟ*｡★･ ∴｡　　･ﾟ*｡☆ ･ ｡ ☆ ∴｡", banner_width),
        f"{COLOR_BORDER}╭{'─' * (banner_width - 2)}╮",
    ]

    for line_number, line in enumerate(centered_logo):
        gradient_line = apply_gradient(line, cosmic_gradient, line_number)
        banner.append(f"{COLOR_BORDER}│ {gradient_line} {COLOR_BORDER}│")

    release_manager_text = COLOR_STEP + "Release Manager"

    banner.extend(
        [
            f"{COLOR_BORDER}╰{'─' * (banner_width - 2)}╯",
            center_text(
                f"{COLOR_STAR}∴｡　　･ﾟ*｡☆ {release_manager_text}{COLOR_STAR} ☆｡*ﾟ･　 ｡∴",
                banner_width,
            ),
            center_text(f"{COLOR_STAR}･ ｡ ☆ ∴｡　　･ﾟ*｡★･ ∴｡　　･ﾟ*｡☆ ･ ｡ ☆ ∴｡", banner_width),
        ]
    )

    return "\n".join(banner)


def print_logo() -> None:
    """Print the banner/logo for the release manager."""
    print(create_banner())


def run_command(
    cmd: list[str], check: bool = False, capture_output: bool = False, text: bool = False
) -> CompletedProcess[str | bytes]:
    """
    Run a command safely with proper error handling.

    Args:
        cmd: Command and arguments to run
        check: Whether to check the return code
        capture_output: Whether to capture stdout/stderr
        text: Whether to return text instead of bytes

    Returns:
        CompletedProcess instance with command results
    """
    # Ensure the command exists in PATH
    if not shutil.which(cmd[0]):
        print_error(f"Command '{cmd[0]}' not found in PATH")
        sys.exit(1)

    try:
        # We're validating the command exists and controlling the input, so this is safe
        return subprocess.run(cmd, check=check, capture_output=capture_output, text=text)  # noqa: S603
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {' '.join(cmd)}")
            print_error(f"Error: {e}")
            sys.exit(1)
        raise


def run_git_command(
    args: list[str], check: bool = False, capture_output: bool = False, text: bool = False
) -> CompletedProcess[str | bytes]:
    """
    Run a git command safely.

    Args:
        args: Git subcommand and arguments
        check: Whether to check the return code
        capture_output: Whether to capture stdout/stderr
        text: Whether to return text instead of bytes

    Returns:
        CompletedProcess instance with command results
    """
    return run_command(["git", *args], check, capture_output, text)


def run_uv_command(
    args: list[str], check: bool = False, capture_output: bool = False, text: bool = False
) -> CompletedProcess[str | bytes]:
    """
    Run a uv command safely.

    Args:
        args: UV subcommand and arguments
        check: Whether to check the return code
        capture_output: Whether to capture stdout/stderr
        text: Whether to return text instead of bytes

    Returns:
        CompletedProcess instance with command results
    """
    return run_command(["uv", *args], check, capture_output, text)


def check_tool_installed(tool_name: str) -> None:
    """Check if a tool is installed."""
    if shutil.which(tool_name) is None:
        print_error(f"{tool_name} is not installed. Please install it and try again.")
        sys.exit(1)


def check_branch() -> None:
    """Ensure we're on the main branch."""
    result = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    current_branch = result.stdout.strip()
    if current_branch != "main":
        print_error("You must be on the main branch to release.")
        sys.exit(1)


def check_uncommitted_changes() -> None:
    """Check for uncommitted changes."""
    result = run_git_command(["diff-index", "--quiet", "HEAD", "--"], check=False)
    if result.returncode != 0:
        print_error("You have uncommitted changes. Please commit or stash them before releasing.")
        sys.exit(1)


def get_current_version() -> str:
    """Get the current version from pyproject.toml."""
    if not os.path.exists(PYPROJECT_TOML):
        print_error(f"{PYPROJECT_TOML} not found.")
        sys.exit(1)

    # Use a regex pattern to extract the version from pyproject.toml
    version_pattern = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)

    with open(PYPROJECT_TOML, encoding="utf-8") as f:
        content = f.read()

    match = version_pattern.search(content)
    if not match:
        print_error("Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def update_version(new_version: str) -> None:
    """Update the version in pyproject.toml."""
    if not os.path.exists(PYPROJECT_TOML):
        print_error(f"{PYPROJECT_TOML} not found.")
        sys.exit(1)

    with open(PYPROJECT_TOML, encoding="utf-8") as f:
        content = f.read()

    # Use a regex pattern to replace only the project version line
    version_pattern = re.compile(r'^(version\s*=\s*)"([^"]+)"', re.MULTILINE)
    updated_content = version_pattern.sub(f'\\1"{new_version}"', content)

    if content == updated_content:
        print_error("Failed to update version in pyproject.toml")
        sys.exit(1)

    with open(PYPROJECT_TOML, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print_success(f"Updated version in {PYPROJECT_TOML} to {new_version}")


def update_docs_version(new_version: str) -> None:
    """Update documentation version."""
    if not os.path.exists(DOCS_INDEX):
        print_warning(f"{DOCS_INDEX} not found. Skipping documentation version update.")
        return

    with open(DOCS_INDEX, encoding="utf-8") as f:
        content = f.read()

    # Use a more specific pattern to match only the version field
    version_pattern = re.compile(r"^(version:\s*)([^\s]+)", re.MULTILINE)

    # Use a lambda function for replacement to avoid the group reference issue
    def replace_version(match: re.Match[str]) -> str:
        return match.group(1) + new_version

    updated_content = version_pattern.sub(replace_version, content)

    if content == updated_content:
        print_warning(f"No version field found in {DOCS_INDEX} or version already up to date.")
        return

    with open(DOCS_INDEX, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print_success(f"Updated version in {DOCS_INDEX} to {new_version}")


def update_lockfile() -> None:
    """Update the uv.lock file to ensure it has the correct version of package."""
    print_step("Updating dependency lockfile")
    try:
        run_uv_command(["lock"], check=True)
        print_success("Updated uv.lock file")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to update lockfile: {e!s}")
        sys.exit(1)


def show_changes() -> bool:
    """Show changes and ask for confirmation."""
    print_warning("The following files will be modified:")
    run_git_command(["status", "--porcelain"])
    confirmation = input(
        f"{COLOR_VERSION_PROMPT}Do you want to proceed with these changes? (y/N): {COLOR_RESET}"
    ).lower()
    return confirmation == "y"


def commit_and_push(version: str) -> None:
    """Commit and push changes to the repository."""
    print_step("Committing and pushing changes")
    try:
        run_git_command(["add", PYPROJECT_TOML, DOCS_INDEX, "uv.lock"], check=True)
        run_git_command(["commit", "-m", f":rocket: Release version {version}"], check=True)
        run_git_command(["push"], check=True)
        run_git_command(["tag", f"v{version}"], check=True)
        run_git_command(["push", "--tags"], check=True)
        print_success(f"Changes committed and pushed for version {version}")
    except subprocess.CalledProcessError as e:
        print_error(f"Git operations failed: {e!s}")
        sys.exit(1)


def is_valid_version(version: str) -> bool:
    """Validate version format."""
    return re.match(r"^\d+\.\d+\.\d+$", version) is not None


def main() -> None:
    """Main function to handle the release process."""
    try:
        print_logo()
        print_step(f"Starting release process for {PROJECT_NAME}")

        for tool in ["git", "uv"]:
            check_tool_installed(tool)

        check_branch()
        check_uncommitted_changes()

        current_version = get_current_version()
        new_version = input(
            f"{COLOR_VERSION_PROMPT}Current version is {current_version}. What should the new version be? {COLOR_RESET}"
        )

        if not is_valid_version(new_version):
            print_error("Invalid version format. Please use semantic versioning (e.g., 1.2.3).")
            sys.exit(1)

        update_version(new_version)
        update_docs_version(new_version)
        update_lockfile()

        if not show_changes():
            print_error("Release cancelled.")
            sys.exit(1)

        commit_and_push(new_version)

        print_success(f"\n🎉✨ {PROJECT_NAME} v{new_version} has been successfully released! ✨🎉")
    except Exception as e:  # noqa: BLE001
        print_error(f"An unexpected error occurred: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
