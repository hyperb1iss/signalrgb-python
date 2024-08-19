"""
Command-line interface for the SignalRGB API.

This module provides a CLI for interacting with the SignalRGB API,
allowing users to manage effects, layouts, and various settings.
"""

import os
from typing import Dict, Optional
from functools import wraps
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .client import (
    DEFAULT_PORT,
    SignalRGBClient,
    SignalRGBException,
    ConnectionError,
    APIError,
    NotFoundError,
)
from .model import Effect, Layout

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
        import pkg_resources  # type: ignore

        __version__ = pkg_resources.get_distribution("signalrgb").version
    except Exception:
        __version__ = "unknown"


def version_callback(value: bool) -> None:
    """Callback to display the version and exit."""
    if value:
        console.print(f"SignalRGB CLI version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()


@app.callback()
def callback(
    ctx: typer.Context,
    host: str = typer.Option(DEFAULT_HOST, help="SignalRGB API host"),
    port: int = typer.Option(DEFAULT_PORT, help="SignalRGB API port"),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit",
    ),
) -> None:
    """Initialize SignalRGB client."""
    ctx.obj = SignalRGBClient(host, port)


def create_effect_panel(effect: Effect, title: str) -> Panel:
    """Create a panel with effect details.

    Args:
        effect: The Effect object to display.
        title: The title for the panel.

    Returns:
        A Rich Panel object containing the effect details.
    """
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


def create_param_table(parameters: Dict[str, str]) -> Table:
    """Create a table with effect parameters.

    Args:
        parameters: A dictionary of effect parameters.

    Returns:
        A Rich Table object containing the effect parameters.
    """
    table = Table(title="Effect Parameters", box=box.ROUNDED, border_style="bold white")
    table.add_column("Parameter", style="bold cyan")
    table.add_column("Value", style="magenta")
    for key, value in parameters.items():
        table.add_row(str(key), str(value))
    return table


def handle_signalrgb_exception(func: callable) -> callable:
    """Decorator to handle SignalRGB exceptions.

    This decorator catches SignalRGB exceptions and prints them in a user-friendly format.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SignalRGBException as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            if isinstance(e, ConnectionError):
                console.print(
                    "[yellow]Please check your network connection and SignalRGB server status.[/yellow]"
                )
            elif isinstance(e, APIError):
                console.print(
                    "[yellow]An API error occurred. Please try again later.[/yellow]"
                )
            elif isinstance(e, NotFoundError):
                console.print(
                    "[yellow]The specified effect was not found. Please check the effect name or ID.[/yellow]"
                )
            raise typer.Exit(code=1)

    return wrapper


@app.command()
@handle_signalrgb_exception
def list_effects(
    ctx: typer.Context,
    sort_by: str = typer.Option("name", help="Sort effects by 'name' or 'id'"),
    reverse: bool = typer.Option(False, help="Reverse the sort order"),
) -> None:
    """List all available effects."""
    client: SignalRGBClient = ctx.obj
    effects = client.get_effects()

    if sort_by == "name":
        effects.sort(key=lambda e: e.attributes.name.lower(), reverse=reverse)
    elif sort_by == "id":
        effects.sort(key=lambda e: e.id.lower(), reverse=reverse)

    table = Table(title="Available Effects", box=box.ROUNDED, border_style="bold white")
    table.add_column("ID", style="bold cyan")
    table.add_column("Name", style="magenta")

    for effect in effects:
        table.add_row(effect.id, effect.attributes.name)

    console.print(table)
    console.print(f"Total effects: [bold green]{len(effects)}[/bold green]")


@app.command()
@handle_signalrgb_exception
def get_effect(ctx: typer.Context, effect_name: str) -> None:
    """Get details of a specific effect."""
    client: SignalRGBClient = ctx.obj
    effect = client.get_effect_by_name(effect_name)
    console.print(
        create_effect_panel(
            effect, f"[bold]Effect Details: [cyan]{effect_name}[/cyan][/bold]"
        )
    )
    if effect.attributes.parameters:
        console.print(create_param_table(effect.attributes.parameters))


@app.command()
@handle_signalrgb_exception
def current_effect(ctx: typer.Context) -> None:
    """Get the current effect."""
    client: SignalRGBClient = ctx.obj
    effect = client.current_effect
    console.print(create_effect_panel(effect, "[bold]Current Effect[/bold]"))
    if effect.attributes.parameters:
        console.print(create_param_table(effect.attributes.parameters))


@app.command()
@handle_signalrgb_exception
def apply_effect(ctx: typer.Context, effect_name: str) -> None:
    """Apply an effect."""
    client: SignalRGBClient = ctx.obj
    client.apply_effect_by_name(effect_name)
    console.print(
        f"[bold green]Successfully applied effect:[/bold green] [cyan]{effect_name}[/cyan]"
    )


@app.command()
@handle_signalrgb_exception
def search_effects(ctx: typer.Context, query: str) -> None:
    """Search for effects by name or description."""
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
                    (effect.attributes.description[:50] + "...")
                    if effect.attributes.description
                    else "N/A",
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


@app.command()
@handle_signalrgb_exception
def brightness(
    ctx: typer.Context, value: Optional[int] = typer.Argument(None, min=0, max=100)
) -> None:
    """Set or get the brightness level."""
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


@app.command()
@handle_signalrgb_exception
def list_presets(ctx: typer.Context, effect_name: str) -> None:
    """List available presets for a specific effect."""
    client: SignalRGBClient = ctx.obj
    effect = client.get_effect_by_name(effect_name)
    presets = client.get_effect_presets(effect.id)
    table = Table(
        title=f"Presets for '{effect_name}'", box=box.ROUNDED, border_style="bold white"
    )
    table.add_column("Preset ID", style="bold cyan")
    table.add_column("Type", style="magenta")
    for preset in presets:
        table.add_row(preset["id"], preset["type"])
    console.print(table)
    console.print(f"Total presets: [bold green]{len(presets)}[/bold green]")


@app.command()
@handle_signalrgb_exception
def apply_preset(ctx: typer.Context, effect_name: str, preset_id: str) -> None:
    """Apply a preset to a specific effect."""
    client: SignalRGBClient = ctx.obj
    effect = client.get_effect_by_name(effect_name)
    client.apply_effect_preset(effect.id, preset_id)
    console.print(
        f"[bold green]Successfully applied preset:[/bold green] [cyan]{preset_id}[/cyan] to effect [cyan]{effect_name}[/cyan]"
    )


@app.command()
@handle_signalrgb_exception
def next_effect(ctx: typer.Context) -> None:
    """Get information about the next effect in history."""
    client: SignalRGBClient = ctx.obj
    next_effect = client.get_next_effect()
    if next_effect:
        console.print(create_effect_panel(next_effect, "[bold]Next Effect[/bold]"))
    else:
        console.print("[yellow]No next effect available[/yellow]")


@app.command()
@handle_signalrgb_exception
def apply_next(ctx: typer.Context) -> None:
    """Apply the next effect in history or a random effect if there's no next effect."""
    client: SignalRGBClient = ctx.obj
    new_effect = client.apply_next_effect()
    console.print(
        f"[bold green]Successfully applied next effect:[/bold green] [cyan]{new_effect.attributes.name}[/cyan]"
    )


@app.command()
@handle_signalrgb_exception
def previous_effect(ctx: typer.Context) -> None:
    """Get information about the previous effect in history."""
    client: SignalRGBClient = ctx.obj
    prev_effect = client.get_previous_effect()
    if prev_effect:
        console.print(create_effect_panel(prev_effect, "[bold]Previous Effect[/bold]"))
    else:
        console.print("[yellow]No previous effect available[/yellow]")


@app.command()
@handle_signalrgb_exception
def apply_previous(ctx: typer.Context) -> None:
    """Apply the previous effect in history."""
    client: SignalRGBClient = ctx.obj
    new_effect = client.apply_previous_effect()
    console.print(
        f"[bold green]Successfully applied previous effect:[/bold green] [cyan]{new_effect.attributes.name}[/cyan]"
    )


@app.command()
@handle_signalrgb_exception
def apply_random(ctx: typer.Context) -> None:
    """Apply a random effect."""
    client: SignalRGBClient = ctx.obj
    random_effect = client.apply_random_effect()
    console.print(
        f"[bold green]Successfully applied random effect:[/bold green] [cyan]{random_effect.attributes.name}[/cyan]"
    )


@app.command()
@handle_signalrgb_exception
def enable(ctx: typer.Context) -> None:
    """Enable the canvas."""
    client: SignalRGBClient = ctx.obj
    client.enabled = True
    console.print("[bold green]Canvas enabled successfully[/bold green]")


@app.command()
@handle_signalrgb_exception
def disable(ctx: typer.Context) -> None:
    """Disable the canvas."""
    client: SignalRGBClient = ctx.obj
    client.enabled = False
    console.print("[bold green]Canvas disabled successfully[/bold green]")


@app.command()
@handle_signalrgb_exception
def get_current_layout(ctx: typer.Context) -> None:
    """Get the current layout."""
    client: SignalRGBClient = ctx.obj
    current_layout = client.current_layout
    console.print(
        f"[bold green]Current layout:[/bold green] [cyan]{current_layout.id}[/cyan]"
    )


@app.command()
@handle_signalrgb_exception
def set_current_layout(ctx: typer.Context, layout_id: str) -> None:
    """Set the current layout."""
    client: SignalRGBClient = ctx.obj
    client.current_layout = layout_id
    console.print(
        f"[bold green]Successfully set current layout to:[/bold green] [cyan]{layout_id}[/cyan]"
    )


@app.command()
@handle_signalrgb_exception
def list_layouts(ctx: typer.Context) -> None:
    """List all available layouts."""
    client: SignalRGBClient = ctx.obj
    layouts = client.get_layouts()
    table = Table(title="Available Layouts", box=box.ROUNDED, border_style="bold white")
    table.add_column("Layout ID", style="bold cyan")
    table.add_column("Type", style="magenta")
    for layout in layouts:
        table.add_row(layout.id, layout.type)
    console.print(table)
    console.print(f"Total layouts: [bold green]{len(layouts)}[/bold green]")


def create_layout_panel(layout: Layout, title: str) -> Panel:
    """Create a panel with layout details.

    Args:
        layout: The Layout object to display.
        title: The title for the panel.

    Returns:
        A Rich Panel object containing the layout details.
    """
    content = "\n".join(
        [
            f"[bold cyan]ID:[/bold cyan] {layout.id}",
            f"[bold magenta]Type:[/bold magenta] {layout.type}",
        ]
    )
    return Panel(content, title=title, expand=False, border_style="bold white")


@app.command()
@handle_signalrgb_exception
def get_layout(ctx: typer.Context, layout_id: str) -> None:
    """Get details of a specific layout."""
    client: SignalRGBClient = ctx.obj
    layouts = client.get_layouts()
    layout = next((ll for ll in layouts if ll.id == layout_id), None)
    if layout:
        console.print(
            create_layout_panel(
                layout, f"[bold]Layout Details: [cyan]{layout_id}[/cyan][/bold]"
            )
        )
    else:
        console.print(f"[yellow]Layout '{layout_id}' not found.[/yellow]")


@app.command()
@handle_signalrgb_exception
def refresh_effects(ctx: typer.Context) -> None:
    """Refresh the cached effects."""
    client: SignalRGBClient = ctx.obj
    client.refresh_effects()
    console.print("[bold green]Effects cache refreshed successfully[/bold green]")


@app.command()
@handle_signalrgb_exception
def get_enabled_state(ctx: typer.Context) -> None:
    """Get the current enabled state of the canvas."""
    client: SignalRGBClient = ctx.obj
    enabled = client.enabled
    state = "enabled" if enabled else "disabled"
    console.print(f"[bold green]Canvas is currently [cyan]{state}[/cyan][/bold green]")


@app.command()
@handle_signalrgb_exception
def toggle_enabled(ctx: typer.Context) -> None:
    """Toggle the enabled state of the canvas."""
    client: SignalRGBClient = ctx.obj
    current_state = client.enabled
    new_state = not current_state
    client.enabled = new_state
    state = "enabled" if new_state else "disabled"
    console.print(f"[bold green]Canvas has been [cyan]{state}[/cyan][/bold green]")


@app.command()
@handle_signalrgb_exception
def effect_info(ctx: typer.Context, effect_name: str) -> None:
    """Get detailed information about a specific effect."""
    client: SignalRGBClient = ctx.obj
    effect = client.get_effect_by_name(effect_name)
    console.print(
        create_effect_panel(
            effect, f"[bold]Effect Information: [cyan]{effect_name}[/cyan][/bold]"
        )
    )

    if effect.attributes.parameters:
        console.print(create_param_table(effect.attributes.parameters))

    presets = client.get_effect_presets(effect.id)
    if presets:
        preset_table = Table(
            title="Available Presets", box=box.ROUNDED, border_style="bold white"
        )
        preset_table.add_column("Preset ID", style="bold cyan")
        preset_table.add_column("Type", style="magenta")
        for preset in presets:
            preset_table.add_column(preset["id"], preset["type"])
        console.print(preset_table)
    else:
        console.print("[yellow]No presets available for this effect.[/yellow]")


@app.command()
@handle_signalrgb_exception
def apply_effect_with_preset(
    ctx: typer.Context, effect_name: str, preset_id: str
) -> None:
    """Apply an effect with a specific preset."""
    client: SignalRGBClient = ctx.obj
    effect = client.get_effect_by_name(effect_name)
    client.apply_effect(effect.id)
    client.apply_effect_preset(effect.id, preset_id)
    console.print(
        f"[bold green]Successfully applied effect [cyan]{effect_name}[/cyan] with preset [cyan]{preset_id}[/cyan][/bold green]"
    )


@app.command()
@handle_signalrgb_exception
def cycle_effects(
    ctx: typer.Context,
    duration: int = typer.Option(5, help="Duration to display each effect in seconds"),
) -> None:
    """Cycle through all available effects."""
    client: SignalRGBClient = ctx.obj
    effects = client.get_effects()

    with typer.progressbar(effects, label="Cycling through effects") as progress:
        for effect in progress:
            client.apply_effect(effect.id)
            console.print(
                f"[bold green]Applied effect:[/bold green] [cyan]{effect.attributes.name}[/cyan]"
            )
            typer.sleep(duration)

    console.print("[bold green]Finished cycling through all effects[/bold green]")


if __name__ == "__main__":
    app()
