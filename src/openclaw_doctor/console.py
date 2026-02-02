"""Rich console utilities for beautiful terminal output."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

# Global console instance
console = Console()


class StatusIcon:
    """Status icons for check results."""
    PASS = "[bold green]✓[/bold green]"
    FAIL = "[bold red]✗[/bold red]"
    WARN = "[bold yellow]![/bold yellow]"
    INFO = "[bold blue]ℹ[/bold blue]"
    FIX = "[bold magenta]⚡[/bold magenta]"


def print_header() -> None:
    """Print the OpenClaw Doctor header."""
    header = Panel(
        Text.from_markup(
            "[bold cyan]OpenClaw Doctor[/bold cyan] 🩺\n"
            "[dim]Diagnosing your OpenClaw installation[/dim]"
        ),
        box=box.ROUNDED,
        padding=(1, 2),
        style="cyan",
    )
    console.print(header)
    console.print()


def print_check_result(
    name: str,
    passed: bool,
    message: str,
    warning: bool = False,
    details: str | None = None,
) -> None:
    """Print a single check result."""
    if passed:
        icon = StatusIcon.WARN if warning else StatusIcon.PASS
    else:
        icon = StatusIcon.FAIL
    
    console.print(f"[{icon}] {message}")
    
    if details:
        console.print(f"    [dim]{details}[/dim]")


def print_fix_action(message: str) -> None:
    """Print a fix action message."""
    console.print(f"[{StatusIcon.FIX}] [magenta]Fixing:[/magenta] {message}")


def print_suggestion(title: str, steps: list[str]) -> None:
    """Print a suggestion box with steps to fix an issue."""
    suggestion_text = "\n".join(f"  {i+1}. {step}" for i, step in enumerate(steps))
    panel = Panel(
        suggestion_text,
        title=f"[bold yellow]💡 {title}[/bold yellow]",
        border_style="yellow",
        padding=(0, 1),
    )
    console.print(panel)


def print_summary(passed: int, warnings: int, failed: int) -> None:
    """Print the summary of all checks."""
    console.print()
    console.rule(style="dim")
    console.print()
    
    summary_parts = []
    if passed > 0:
        summary_parts.append(f"[green]{passed} passed[/green]")
    if warnings > 0:
        summary_parts.append(f"[yellow]{warnings} warning{'s' if warnings > 1 else ''}[/yellow]")
    if failed > 0:
        summary_parts.append(f"[red]{failed} failed[/red]")
    
    console.print(f"[bold]Summary:[/bold] {', '.join(summary_parts)}")
    
    if failed > 0 or warnings > 0:
        console.print()
        console.print("[dim]To fix issues, run:[/dim] [bold cyan]openclaw-doctor --fix[/bold cyan]")


def create_progress() -> Progress:
    """Create a progress spinner for running checks."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]Success:[/bold green] {message}")
