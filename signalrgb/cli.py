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
            f"[bold purple]Image:[/bold purple] {effect.attributes.image or 'N/A'}",
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


@app.command()
def brightness(ctx: typer.Context, value: int = typer.Argument(None, min=0, max=100)):
    """Set or get the brightness level"""

    def command():
        client: SignalRGBClient = ctx.obj
        if value is not None:
            client.brightness = value
            console.print(
                f"[bold green]Brightness set to:[/bold green] [cyan]{value}[/cyan]"
            )
        else:
            current_brightness = client.brightness
            console.print(
                f"[bold green]Current brightness:[/bold green] [cyan]{current_brightness}[/cyan]"
            )

    handle_signalrgb_exception(command)


@app.command()
def list_presets(ctx: typer.Context, effect_name: str):
    """List available presets for a specific effect"""

    def command():
        client: SignalRGBClient = ctx.obj
        effect = client.get_effect_by_name(effect_name)
        presets = client.get_effect_presets(effect.id)
        table = Table(
            title=f"Presets for '{effect_name}'",
            box=box.ROUNDED,
            border_style="bold white",
        )
        table.add_column("Preset ID", style="bold cyan")
        table.add_column("Type", style="magenta")
        for preset in presets:
            table.add_row(preset["id"], preset["type"])
        console.print(table)
        console.print(f"Total presets: [bold green]{len(presets)}[/bold green]")

    handle_signalrgb_exception(command)


@app.command()
def apply_preset(ctx: typer.Context, effect_name: str, preset_id: str):
    """Apply a preset to a specific effect"""

    def command():
        client: SignalRGBClient = ctx.obj
        effect = client.get_effect_by_name(effect_name)
        client.apply_effect_preset(effect.id, preset_id)
        console.print(
            f"[bold green]Successfully applied preset:[/bold green] [cyan]{preset_id}[/cyan] to effect [cyan]{effect_name}[/cyan]"
        )

    handle_signalrgb_exception(command)


@app.command()
def next_effect(ctx: typer.Context):
    """Get information about the next effect in history"""

    def command():
        client: SignalRGBClient = ctx.obj
        next_effect = client.get_next_effect()
        if next_effect:
            console.print(create_effect_panel(next_effect, "[bold]Next Effect[/bold]"))
        else:
            console.print("[yellow]No next effect available[/yellow]")

    handle_signalrgb_exception(command)


@app.command()
def apply_next(ctx: typer.Context):
    """Apply the next effect in history or a random effect if there's no next effect"""

    def command():
        client: SignalRGBClient = ctx.obj
        new_effect = client.apply_next_effect()
        console.print(
            f"[bold green]Successfully applied next effect:[/bold green] [cyan]{new_effect.attributes.name}[/cyan]"
        )

    handle_signalrgb_exception(command)


@app.command()
def previous_effect(ctx: typer.Context):
    """Get information about the previous effect in history"""

    def command():
        client: SignalRGBClient = ctx.obj
        prev_effect = client.get_previous_effect()
        if prev_effect:
            console.print(
                create_effect_panel(prev_effect, "[bold]Previous Effect[/bold]")
            )
        else:
            console.print("[yellow]No previous effect available[/yellow]")

    handle_signalrgb_exception(command)


@app.command()
def apply_previous(ctx: typer.Context):
    """Apply the previous effect in history"""

    def command():
        client: SignalRGBClient = ctx.obj
        new_effect = client.apply_previous_effect()
        console.print(
            f"[bold green]Successfully applied previous effect:[/bold green] [cyan]{new_effect.attributes.name}[/cyan]"
        )

    handle_signalrgb_exception(command)


@app.command()
def apply_random(ctx: typer.Context):
    """Apply a random effect"""

    def command():
        client: SignalRGBClient = ctx.obj
        random_effect = client.apply_random_effect()
        console.print(
            f"[bold green]Successfully applied random effect:[/bold green] [cyan]{random_effect.attributes.name}[/cyan]"
        )

    handle_signalrgb_exception(command)


@app.command()
def enable(ctx: typer.Context):
    """Enable the canvas"""

    def command():
        client: SignalRGBClient = ctx.obj
        client.enabled = True
        console.print("[bold green]Canvas enabled successfully[/bold green]")

    handle_signalrgb_exception(command)


@app.command()
def disable(ctx: typer.Context):
    """Disable the canvas"""

    def command():
        client: SignalRGBClient = ctx.obj
        client.enabled = False
        console.print("[bold green]Canvas disabled successfully[/bold green]")

    handle_signalrgb_exception(command)


if __name__ == "__main__":
    app()
