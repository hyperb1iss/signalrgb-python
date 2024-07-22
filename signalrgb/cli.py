import os
from typing import Dict, Any

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .client import DEFAULT_PORT, SignalRGBClient, SignalRGBException
from .model import Effect

app = typer.Typer(help="Command line interface for SignalRGB API")
console = Console()

# Use environment variables for host and port if available
DEFAULT_HOST = os.environ.get("SIGNALRGB_HOST", "localhost")
DEFAULT_PORT = int(os.environ.get("SIGNALRGB_PORT", DEFAULT_PORT))

# Attempt to get the version, use a fallback if not available
try:
    from importlib.metadata import version

    __version__ = version("signalrgb")
except ImportError:
    try:
        import pkg_resources

        __version__ = pkg_resources.get_distribution("signalrgb").version
    except Exception:
        __version__ = "unknown"


def version_callback(value: bool):
    if value:
        console.print(f"SignalRGB CLI version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()


@app.callback()
def callback(
    ctx: typer.Context,
    host: str = typer.Option(DEFAULT_HOST, help="SignalRGB API host"),
    port: int = typer.Option(DEFAULT_PORT, help="SignalRGB API port"),
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit",
    ),
):
    """Initialize SignalRGB client"""
    ctx.obj = SignalRGBClient(host, port)


def create_effect_panel(effect: Effect, title: str) -> Panel:
    """Create a panel with effect details."""
    content = "\n".join(
        [
            f"[bold cyan]ID:[/bold cyan] {effect.id}",
            f"[bold magenta]Name:[/bold magenta] {effect.attributes.name}",
            f"[bold green]Publisher:[/bold green] {effect.attributes.publisher or 'N/A'}",
            f"[bold yellow]Description:[/bold yellow] {effect.attributes.description or 'N/A'}",
            f"[bold blue]Uses Audio:[/bold blue] {effect.attributes.uses_audio}",
            f"[bold blue]Uses Video:[/bold blue] {effect.attributes.uses_video}",
            f"[bold blue]Uses Input:[/bold blue] {effect.attributes.uses_input}",
            f"[bold blue]Uses Meters:[/bold blue] {effect.attributes.uses_meters}",
        ]
    )
    return Panel(content, title=title, expand=False, border_style="bold white")


def create_param_table(parameters: Dict[str, Any]) -> Table:
    """Create a table with effect parameters."""
    table = Table(title="Effect Parameters", box=box.ROUNDED, border_style="bold white")
    table.add_column("Parameter", style="bold cyan")
    table.add_column("Value", style="magenta")
    for key, value in parameters.items():
        table.add_row(str(key), str(value))
    return table


def handle_signalrgb_exception(func):
    try:
        func()
    except SignalRGBException as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def list_effects(
    ctx: typer.Context,
    sort_by: str = typer.Option("name", help="Sort effects by 'name' or 'id'"),
    reverse: bool = typer.Option(False, help="Reverse the sort order"),
):
    """List all available effects"""

    def command():
        client: SignalRGBClient = ctx.obj
        effects = client.get_effects()

        if sort_by == "name":
            effects.sort(key=lambda e: e.attributes.name.lower(), reverse=reverse)
        elif sort_by == "id":
            effects.sort(key=lambda e: e.id.lower(), reverse=reverse)

        table = Table(
            title="Available Effects", box=box.ROUNDED, border_style="bold white"
        )
        table.add_column("ID", style="bold cyan")
        table.add_column("Name", style="magenta")

        for effect in effects:
            table.add_row(effect.id, effect.attributes.name)

        console.print(table)
        console.print(f"Total effects: [bold green]{len(effects)}[/bold green]")

    handle_signalrgb_exception(command)


@app.command()
def get_effect(ctx: typer.Context, effect_name: str):
    """Get details of a specific effect"""

    def command():
        client: SignalRGBClient = ctx.obj
        effect = client.get_effect_by_name(effect_name)
        console.print(
            create_effect_panel(
                effect, f"[bold]Effect Details: [cyan]{effect_name}[/cyan][/bold]"
            )
        )
        if effect.attributes.parameters:
            console.print(create_param_table(effect.attributes.parameters))

    handle_signalrgb_exception(command)


@app.command()
def current_effect(ctx: typer.Context):
    """Get the current effect"""

    def command():
        client: SignalRGBClient = ctx.obj
        effect = client.get_current_effect()
        console.print(create_effect_panel(effect, "[bold]Current Effect[/bold]"))
        if effect.attributes.parameters:
            console.print(create_param_table(effect.attributes.parameters))

    handle_signalrgb_exception(command)


@app.command()
def apply_effect(ctx: typer.Context, effect_name: str):
    """Apply an effect"""

    def command():
        client: SignalRGBClient = ctx.obj
        client.apply_effect_by_name(effect_name)
        console.print(
            f"[bold green]Successfully applied effect:[/bold green] [cyan]{effect_name}[/cyan]"
        )

    handle_signalrgb_exception(command)


@app.command()
def search_effects(ctx: typer.Context, query: str):
    """Search for effects by name or description"""

    def command():
        client: SignalRGBClient = ctx.obj
        effects = client.get_effects()

        matched_effects = [
            effect
            for effect in effects
            if query.lower() in effect.attributes.name.lower()
            or (
                effect.attributes.description
                and query.lower() in effect.attributes.description.lower()
            )
        ]

        if matched_effects:
            table = Table(
                title=f"Search Results for '[cyan]{query}[/cyan]'",
                box=box.ROUNDED,
                border_style="bold white",
            )
            table.add_column("ID", style="bold cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Description", style="green")

            for effect in matched_effects:
                table.add_row(
                    effect.id,
                    effect.attributes.name,
                    Text(
                        (
                            (effect.attributes.description[:50] + "...")
                            if effect.attributes.description
                            else "N/A"
                        ),
                        overflow="ellipsis",
                    ),
                )

            console.print(table)
            console.print(
                f"Found [bold green]{len(matched_effects)}[/bold green] matching effects"
            )
        else:
            console.print(
                f"[yellow]No effects found matching '[cyan]{query}[/cyan]'[/yellow]"
            )

    handle_signalrgb_exception(command)


if __name__ == "__main__":
    app()
