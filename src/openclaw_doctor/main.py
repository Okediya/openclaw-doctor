"""OpenClaw Doctor CLI - Main entry point."""

import json
import sys
from typing import Optional

import typer
from rich.json import JSON as RichJSON

from . import __version__
from .console import (
    console,
    create_progress,
    print_check_result,
    print_error,
    print_fix_action,
    print_header,
    print_success,
    print_summary,
)
from .checks import ALL_CHECKS, BaseCheck, CheckResult, CheckStatus

app = typer.Typer(
    name="openclaw-doctor",
    help="Diagnose, validate, and auto-fix OpenClaw AI assistant installations.",
    add_completion=False,
    invoke_without_command=True,
)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    fix: bool = typer.Option(
        False,
        "--fix",
        "-f",
        help="Attempt to automatically fix issues",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output results as JSON",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
    ),
) -> None:
    """
    OpenClaw Doctor - Diagnose, validate, and auto-fix OpenClaw installations.
    """
    if version:
        console.print(f"openclaw-doctor v{__version__}")
        raise typer.Exit()
    
    # If no subcommand is specified, run the doctor command
    if ctx.invoked_subcommand is None:
        ctx.invoke(doctor, fix=fix, verbose=verbose, json_output=json_output)


def run_all_checks(
    fix: bool = False,
    verbose: bool = False,
) -> tuple[list[CheckResult], int, int, int]:
    """Run all health checks and return results with counts."""
    results: list[CheckResult] = []
    passed = 0
    warnings = 0
    failed = 0
    
    with create_progress() as progress:
        task = progress.add_task("Running health checks...", total=len(ALL_CHECKS))
        
        for check_class in ALL_CHECKS:
            check: BaseCheck = check_class()
            progress.update(task, description=f"Checking {check.name}...")
            
            result = check.run()
            results.append(result)
            
            progress.advance(task)
    
    # Display results
    for result in results:
        print_check_result(
            name=result.name,
            passed=result.passed,
            message=result.message,
            warning=result.is_warning,
            details=result.details if verbose else None,
        )
        
        if result.status == CheckStatus.PASS:
            passed += 1
        elif result.status == CheckStatus.WARN:
            warnings += 1
        else:
            failed += 1
    
    # Run fixes if requested
    if fix:
        fixable_results = [r for r in results if not r.passed or r.is_warning]
        if fixable_results:
            console.print()
            console.rule("[bold magenta]Auto-Fix[/bold magenta]", style="magenta")
            console.print()
            
            for result in fixable_results:
                if result.can_auto_fix:
                    check_class = next(
                        (c for c in ALL_CHECKS if c.name == result.name),
                        None
                    )
                    if check_class:
                        check = check_class()
                        check.run()  # Re-run to populate state
                        print_fix_action(f"Attempting to fix: {result.name}")
                        success = check.fix()
                        if success:
                            print_success(f"{result.name} fixed!")
                        console.print()
                elif result.fix_suggestions:
                    console.print(f"[bold]{result.name}[/bold] - Manual fix required:")
                    for suggestion in result.fix_suggestions:
                        console.print(f"  [dim]•[/dim] {suggestion}")
                    console.print()
    
    return results, passed, warnings, failed


@app.command()
def doctor(
    fix: bool = typer.Option(
        False,
        "--fix",
        "-f",
        help="Attempt to automatically fix issues",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output results as JSON",
    ),
) -> None:
    """
    Run OpenClaw health checks.
    
    Diagnoses your OpenClaw installation and reports any issues.
    Use --fix to automatically resolve issues where possible.
    """
    if json_output:
        # Quiet mode for JSON output
        results: list[CheckResult] = []
        for check_class in ALL_CHECKS:
            check = check_class()
            result = check.run()
            results.append(result)
        
        output = {
            "version": __version__,
            "checks": [r.to_dict() for r in results],
            "summary": {
                "passed": sum(1 for r in results if r.status == CheckStatus.PASS),
                "warnings": sum(1 for r in results if r.status == CheckStatus.WARN),
                "failed": sum(1 for r in results if r.status == CheckStatus.FAIL),
            }
        }
        console.print(RichJSON(json.dumps(output, indent=2)))
        
        # Exit with error code if any checks failed
        if output["summary"]["failed"] > 0:
            raise typer.Exit(1)
        return
    
    # Normal output
    print_header()
    
    results, passed, warnings, failed = run_all_checks(fix=fix, verbose=verbose)
    
    print_summary(passed, warnings, failed)
    
    # Exit with error code if any checks failed
    if failed > 0:
        raise typer.Exit(1)


@app.command()
def check(
    name: str = typer.Argument(
        ...,
        help="Name of the check to run (nodejs, openclaw, docker, system, config, api_keys, network)",
    ),
    fix: bool = typer.Option(
        False,
        "--fix",
        "-f",
        help="Attempt to automatically fix issues",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """
    Run a specific health check.
    
    Available checks: nodejs, openclaw, docker, system, config, api_keys, network
    """
    # Find the check by name
    name_lower = name.lower().replace("-", "_").replace(" ", "_")
    check_class: Optional[type[BaseCheck]] = None
    
    name_map = {
        "nodejs": "Node.js",
        "node": "Node.js",
        "openclaw": "OpenClaw",
        "claw": "OpenClaw",
        "docker": "Docker",
        "system": "System",
        "config": "Config",
        "configuration": "Config",
        "api_keys": "API Keys",
        "apikeys": "API Keys",
        "keys": "API Keys",
        "network": "Network",
        "net": "Network",
    }
    
    target_name = name_map.get(name_lower)
    
    for cls in ALL_CHECKS:
        if cls.name == target_name or cls.name.lower() == name_lower:
            check_class = cls
            break
    
    if not check_class:
        print_error(f"Unknown check: {name}")
        console.print("\nAvailable checks:")
        for cls in ALL_CHECKS:
            console.print(f"  • {cls.name.lower().replace(' ', '_')} - {cls.description}")
        raise typer.Exit(1)
    
    print_header()
    
    check = check_class()
    result = check.run()
    
    print_check_result(
        name=result.name,
        passed=result.passed,
        message=result.message,
        warning=result.is_warning,
        details=result.details if verbose else None,
    )
    
    if fix and (not result.passed or result.is_warning):
        console.print()
        if result.can_auto_fix:
            print_fix_action(f"Attempting to fix: {result.name}")
            success = check.fix()
            if success:
                print_success(f"{result.name} fixed!")
        elif result.fix_suggestions:
            console.print("[bold]Manual fix required:[/bold]")
            for suggestion in result.fix_suggestions:
                console.print(f"  [dim]•[/dim] {suggestion}")
    
    if result.status == CheckStatus.FAIL:
        raise typer.Exit(1)


@app.command()
def list_checks() -> None:
    """List all available health checks."""
    console.print("\n[bold]Available Health Checks:[/bold]\n")
    
    for check_class in ALL_CHECKS:
        console.print(f"  [cyan]{check_class.name}[/cyan]")
        console.print(f"    {check_class.description}")
        console.print()


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
