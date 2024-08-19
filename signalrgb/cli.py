import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from functools import wraps

from .client import (
    SignalRGBClient,
    SignalRGBException,
    ConnectionError,
    APIError,
    NotFoundError,
)

app = typer.Typer(help="SignalRGB CLI")
console = Console()


def get_client(ctx: typer.Context) -> SignalRGBClient:
    return ctx.obj


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            console.print(f"[bold red]Connection Error:[/bold red] {str(e)}")
            raise typer.Exit(code=1)
        except APIError as e:
            console.print(f"[bold red]API Error:[/bold red] {str(e)}")
            raise typer.Exit(code=1)
        except NotFoundError as e:
            console.print(f"[bold red]Not Found:[/bold red] {str(e)}")
            raise typer.Exit(code=1)
        except SignalRGBException as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(code=1)

    return wrapper


def create_effect_panel(effect, title: str) -> Panel:
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


def create_param_table(parameters):
    table = Table(title="Effect Parameters", border_style="bold white")
    table.add_column("Parameter", style="bold cyan")
    table.add_column("Value", style="magenta")
    for key, value in parameters.items():
        table.add_row(str(key), str(value))
    return table


# Effect commands
effect_app = typer.Typer(help="Manage effects", invoke_without_command=True)
app.add_typer(effect_app, name="effect")


@effect_app.callback(invoke_without_command=True)
@handle_exceptions
def effect(ctx: typer.Context, name: Optional[str] = None):
    """Show details of the current effect or a specific effect."""
    if ctx.invoked_subcommand is None:
        client = get_client(ctx)
        effect = (
            client.get_effect_by_name(name) if name else client.get_current_effect()
        )
        console.print(create_effect_panel(effect, f"Effect: {effect.attributes.name}"))
        if effect.attributes.parameters:
            console.print(create_param_table(effect.attributes.parameters))


@effect_app.command(name="list")
@handle_exceptions
def list_effects(ctx: typer.Context):
    """List all available effects."""
    client = get_client(ctx)
    effects = client.get_effects()
    table = Table(title="Available Effects")
    table.add_column("Name", style="cyan")
    table.add_column("ID", style="magenta")
    for effect in effects:
        table.add_row(effect.attributes.name, effect.id)
    console.print(table)


@effect_app.command()
@handle_exceptions
def search(ctx: typer.Context, query: str):
    """Search for effects by name or description."""
    client = get_client(ctx)
    effects = client.get_effects()
    matched_effects = [
        e
        for e in effects
        if query.lower() in e.attributes.name.lower()
        or (
            e.attributes.description
            and query.lower() in e.attributes.description.lower()
        )
    ]
    table = Table(title=f"Search Results for '{query}'")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="magenta")
    for effect in matched_effects:
        table.add_row(effect.attributes.name, effect.attributes.description or "N/A")
    console.print(table)


@effect_app.command(name="apply")
@handle_exceptions
def apply_effect(ctx: typer.Context, name: str, preset: Optional[str] = None):
    """Apply an effect, optionally with a preset."""
    client = get_client(ctx)
    client.apply_effect_by_name(name)
    if preset:
        client.apply_effect_preset(client.get_effect_by_name(name).id, preset)
    console.print(
        f"Applied effect: {name}" + (f" with preset: {preset}" if preset else "")
    )


@effect_app.command()
@handle_exceptions
def next(ctx: typer.Context):
    """Apply the next effect in history."""
    client = get_client(ctx)
    effect = client.apply_next_effect()
    console.print(f"Applied next effect: {effect.attributes.name}")


@effect_app.command()
@handle_exceptions
def previous(ctx: typer.Context):
    """Apply the previous effect in history."""
    client = get_client(ctx)
    effect = client.apply_previous_effect()
    console.print(f"Applied previous effect: {effect.attributes.name}")


@effect_app.command()
@handle_exceptions
def random(ctx: typer.Context):
    """Apply a random effect."""
    client = get_client(ctx)
    effect = client.apply_random_effect()
    console.print(f"Applied random effect: {effect.attributes.name}")


@effect_app.command()
@handle_exceptions
def cycle(
    ctx: typer.Context,
    duration: int = typer.Option(5, help="Duration to display each effect in seconds"),
):
    """Cycle through all effects."""
    client = get_client(ctx)
    effects = client.get_effects()
    for effect in effects:
        client.apply_effect(effect.id)
        console.print(f"Applied effect: {effect.attributes.name}")
        typer.sleep(duration)


@effect_app.command()
@handle_exceptions
def refresh(ctx: typer.Context):
    """Refresh the cached effects."""
    client = get_client(ctx)
    client.refresh_effects()
    console.print("Effects cache refreshed")


# Preset commands
preset_app = typer.Typer(help="Manage presets", invoke_without_command=True)
app.add_typer(preset_app, name="preset")


@preset_app.callback(invoke_without_command=True)
@handle_exceptions
def preset(ctx: typer.Context, name: Optional[str] = None):
    """Show details of the current preset or a specific preset."""
    if ctx.invoked_subcommand is None:
        client = get_client(ctx)
        current_effect = client.get_current_effect()
        presets = client.get_effect_presets(current_effect.id)
        if name:
            preset = next((p for p in presets if p.name == name), None)
            if preset:
                console.print(
                    Panel(
                        f"Preset: {preset.name}\nDescription: {preset.description or 'N/A'}"
                    )
                )
            else:
                console.print(
                    f"Preset '{name}' not found for effect '{current_effect.attributes.name}'"
                )
                raise typer.Exit(code=1)
        else:
            console.print(
                Panel(
                    f"[bold cyan]Current Effect:[/bold cyan] {current_effect.attributes.name}\n"
                    f"[bold magenta]Available Presets:[/bold magenta] {', '.join(p.name for p in presets)}",
                    title="Preset Information",
                    expand=False,
                    border_style="bold white",
                )
            )


@preset_app.command(name="list")
@handle_exceptions
def list_presets(ctx: typer.Context):
    """List presets for the current effect."""
    client = get_client(ctx)
    current_effect = client.get_current_effect()
    presets = client.get_effect_presets(current_effect.id)
    table = Table(title=f"Presets for {current_effect.attributes.name}")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="magenta")
    for preset in presets:
        table.add_row(preset.name, preset.description or "N/A")
    console.print(table)


@preset_app.command(name="apply")
@handle_exceptions
def apply_preset(ctx: typer.Context, preset_name: str):
    """Apply a preset to the current effect."""
    client = get_client(ctx)
    current_effect = client.get_current_effect()
    client.apply_effect_preset(current_effect.id, preset_name)
    console.print(
        f"Applied preset '{preset_name}' to effect '{current_effect.attributes.name}'"
    )


# Layout commands
layout_app = typer.Typer(help="Manage layouts", invoke_without_command=True)
app.add_typer(layout_app, name="layout")


@layout_app.callback(invoke_without_command=True)
@handle_exceptions
def layout(ctx: typer.Context, name: Optional[str] = None):
    """Show details of the current layout or a specific layout."""
    if ctx.invoked_subcommand is None:
        client = get_client(ctx)
        if name:
            layouts = client.get_layouts()
            layout = next((l for l in layouts if l.id == name), None)
            if layout:
                console.print(Panel(f"Layout: {layout.id}\nType: {layout.type}"))
            else:
                console.print(f"Layout '{name}' not found")
                raise typer.Exit(code=1)
        else:
            current_layout = client.current_layout
            console.print(
                Panel(
                    f"[bold cyan]Current Layout:[/bold cyan] {current_layout.id}\n"
                    f"[bold magenta]Type:[/bold magenta] {current_layout.type}",
                    title="Layout Information",
                    expand=False,
                    border_style="bold white",
                )
            )


@layout_app.command(name="list")
@handle_exceptions
def list_layouts(ctx: typer.Context):
    """List all available layouts."""
    client = get_client(ctx)
    layouts = client.get_layouts()
    table = Table(title="Available Layouts")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    for layout in layouts:
        table.add_row(layout.id, layout.type)
    console.print(table)


@layout_app.command()
@handle_exceptions
def set(ctx: typer.Context, name: str):
    """Set the current layout."""
    client = get_client(ctx)
    client.current_layout = name
    console.print(f"Set current layout to: {name}")


# Canvas commands
canvas_app = typer.Typer(
    help="Manage canvas settings like brightness and enabled state.",
    invoke_without_command=True,
)
app.add_typer(canvas_app, name="canvas")


@canvas_app.callback(invoke_without_command=True)
@handle_exceptions
def canvas(ctx: typer.Context):
    """Show current canvas state."""
    if ctx.invoked_subcommand is None:
        client = get_client(ctx)
        enabled = client.enabled
        brightness = client.brightness
        console.print(
            Panel(
                f"[bold cyan]Canvas State:[/bold cyan] {'Enabled' if enabled else 'Disabled'}\n"
                f"[bold magenta]Brightness:[/bold magenta] {brightness}%",
                title="Canvas Information",
                expand=False,
                border_style="bold white",
            )
        )


@canvas_app.command()
@handle_exceptions
def brightness(
    ctx: typer.Context, value: Optional[int] = typer.Argument(None, min=0, max=100)
):
    """Get or set the brightness level."""
    client = get_client(ctx)
    if value is not None:
        client.brightness = value
        console.print(f"Set brightness to: {value}%")
    else:
        console.print(f"Current brightness: {client.brightness}%")


@canvas_app.command()
@handle_exceptions
def enable(ctx: typer.Context):
    """Enable the canvas."""
    client = get_client(ctx)
    client.enabled = True
    console.print("Canvas enabled")


@canvas_app.command()
@handle_exceptions
def disable(ctx: typer.Context):
    """Disable the canvas."""
    client = get_client(ctx)
    client.enabled = False
    console.print("Canvas disabled")


@canvas_app.command()
@handle_exceptions
def toggle(ctx: typer.Context):
    """Toggle the canvas enabled state."""
    client = get_client(ctx)
    client.enabled = not client.enabled
    console.print(f"Canvas {'enabled' if client.enabled else 'disabled'}")


@app.callback()
def main(
    ctx: typer.Context,
    host: str = typer.Option("localhost", help="SignalRGB API host"),
    port: int = typer.Option(16038, help="SignalRGB API port"),
):
    """Initialize SignalRGB client."""
    ctx.obj = SignalRGBClient(host, port)


if __name__ == "__main__":
    app()
