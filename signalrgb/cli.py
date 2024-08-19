import typer
import time
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich import box
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn
from functools import wraps
import json
import wcwidth

from .client import (
    SignalRGBClient,
    SignalRGBException,
    ConnectionError,
    APIError,
    NotFoundError,
)

app = typer.Typer(help="SignalRGB CLI")
console = Console()

ICONS = {
    "effect": "🌈",
    "preset": "🎨",
    "layout": "🖼️",
    "canvas": "🖥️",
}

STATUS_EMOJIS = {
    "enabled": "✅",
    "disabled": "❌",
    "warning": "⚠️",
    "error": "🚫",
}


def color_gradient(text: str, start_color: str, end_color: str) -> Text:
    gradient = Text(text)
    gradient.stylize(f"bold {start_color}")
    for i in range(len(text)):
        gradient.stylize(
            f"color({start_color}) blend({end_color} {i / len(text)})", i, i + 1
        )
    return gradient


def get_client(ctx: typer.Context) -> SignalRGBClient:
    return ctx.obj


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            console.print(
                f"{STATUS_EMOJIS['error']} [bold red]Connection Error:[/bold red] {str(e)}"
            )
            raise typer.Exit(code=1)
        except APIError as e:
            console.print(
                f"{STATUS_EMOJIS['error']} [bold red]API Error:[/bold red] {str(e)}"
            )
            raise typer.Exit(code=1)
        except NotFoundError as e:
            console.print(
                f"{STATUS_EMOJIS['error']} [bold red]Not Found:[/bold red] {str(e)}"
            )
            raise typer.Exit(code=1)
        except SignalRGBException as e:
            console.print(
                f"{STATUS_EMOJIS['error']} [bold red]Error:[/bold red] {str(e)}"
            )
            raise typer.Exit(code=1)

    return wrapper


def get_string_width(s: str) -> int:
    return wcwidth.wcswidth(s)


def create_effect_panel(effect, title: str) -> Panel:
    content = "\n".join(
        [
            f"[bold cyan]ID:[/bold cyan] {effect.id}",
            f"[bold magenta]Name:[/bold magenta] {effect.attributes.name}",
            f"[bold green]Publisher:[/bold green] {effect.attributes.publisher or 'N/A'}",
            f"[bold yellow]Description:[/bold yellow] {effect.attributes.description or 'N/A'}",
            f"[bold blue]Uses Audio:[/bold blue] {STATUS_EMOJIS['enabled'] if effect.attributes.uses_audio else STATUS_EMOJIS['disabled']}",
            f"[bold blue]Uses Video:[/bold blue] {STATUS_EMOJIS['enabled'] if effect.attributes.uses_video else STATUS_EMOJIS['disabled']}",
            f"[bold blue]Uses Input:[/bold blue] {STATUS_EMOJIS['enabled'] if effect.attributes.uses_input else STATUS_EMOJIS['disabled']}",
            f"[bold blue]Uses Meters:[/bold blue] {STATUS_EMOJIS['enabled'] if effect.attributes.uses_meters else STATUS_EMOJIS['disabled']}",
        ]
    )
    return Panel(
        content,
        title=color_gradient(title, "cyan", "green"),
        expand=False,
        border_style="bold white",
    )


def create_param_table(parameters):
    json_str = json.dumps(parameters, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    return Panel(
        syntax,
        title=color_gradient("Effect Parameters", "yellow", "green"),
        border_style="bold white",
    )


def create_colorful_table(title: str, headers: List[str], rows: List[List[str]]):
    table = Table(title=color_gradient(title, "green", "yellow"), box=box.ROUNDED)
    for header_index, header in enumerate(headers):
        max_width = max(
            get_string_width(str(cell))
            for cell in [header] + [row[header_index] for row in rows]
        )
        table.add_column(header, style="bold magenta", width=max_width + 2)
    for i, row in enumerate(rows):
        style = "cyan" if i % 2 == 0 else "green"
        table.add_row(*row, style=style)
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
        console.print(
            create_effect_panel(
                effect, f"{ICONS['effect']} Effect: {effect.attributes.name}"
            )
        )
        if effect.attributes.parameters:
            console.print(create_param_table(effect.attributes.parameters))


@effect_app.command(name="list")
@handle_exceptions
def list_effects(ctx: typer.Context):
    """List all available effects."""
    client = get_client(ctx)
    effects = client.get_effects()
    rows = [[e.attributes.name, e.id] for e in effects]
    table = create_colorful_table(
        f"{ICONS['effect']} Available Effects", ["Name", "ID"], rows
    )
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
    rows = [
        [e.attributes.name, e.attributes.description or "N/A"] for e in matched_effects
    ]
    table = create_colorful_table(
        f"{ICONS['effect']} Search Results for '{query}'", ["Name", "Description"], rows
    )
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
        f"{ICONS['effect']} Applied effect: [bold cyan]{name}[/bold cyan]"
        + (f" with preset: [bold magenta]{preset}[/bold magenta]" if preset else "")
    )


@effect_app.command()
@handle_exceptions
def next(ctx: typer.Context):
    """Apply the next effect in history."""
    client = get_client(ctx)
    effect = client.apply_next_effect()
    console.print(
        f"{ICONS['effect']} Applied next effect: [bold cyan]{effect.attributes.name}[/bold cyan]"
    )


@effect_app.command()
@handle_exceptions
def previous(ctx: typer.Context):
    """Apply the previous effect in history."""
    client = get_client(ctx)
    effect = client.apply_previous_effect()
    console.print(
        f"{ICONS['effect']} Applied previous effect: [bold cyan]{effect.attributes.name}[/bold cyan]"
    )


@effect_app.command()
@handle_exceptions
def random(ctx: typer.Context):
    """Apply a random effect."""
    client = get_client(ctx)
    effect = client.apply_random_effect()
    console.print(
        f"{ICONS['effect']} Applied random effect: [bold cyan]{effect.attributes.name}[/bold cyan]"
    )


@effect_app.command()
@handle_exceptions
def cycle(
    ctx: typer.Context,
    duration: int = typer.Option(5, help="Duration to display each effect in seconds"),
):
    """Cycle through all effects."""
    client = get_client(ctx)
    effects = client.get_effects()
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task(
            f"{ICONS['effect']} [cyan]Cycling effects...", total=len(effects)
        )
        for effect in effects:
            client.apply_effect(effect.id)
            progress.update(
                task,
                advance=1,
                description=f"{ICONS['effect']} [cyan]Applied: [bold]{effect.attributes.name}",
            )
            time.sleep(duration)
    console.print(
        f"{ICONS['effect']} [bold green]Finished cycling through all effects[/bold green]"
    )


@effect_app.command()
@handle_exceptions
def refresh(ctx: typer.Context):
    """Refresh the cached effects."""
    client = get_client(ctx)
    client.refresh_effects()
    console.print(f"{ICONS['effect']} [bold green]Effects cache refreshed[/bold green]")


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
                content = f"Preset: [bold cyan]{preset.name}[/bold cyan]\nDescription: [italic]{preset.description or 'N/A'}[/italic]"
                console.print(
                    Panel(
                        content,
                        title=color_gradient(
                            f"{ICONS['preset']} Preset Information", "blue", "green"
                        ),
                        expand=False,
                        border_style="bold white",
                    )
                )
            else:
                console.print(
                    f"{STATUS_EMOJIS['error']} Preset '[bold]{name}[/bold]' not found for effect '[bold]{current_effect.attributes.name}[/bold]'"
                )
                raise typer.Exit(code=1)
        else:
            content = (
                f"[bold cyan]Current Effect:[/bold cyan] {current_effect.attributes.name}\n"
                f"[bold magenta]Available Presets:[/bold magenta] {', '.join(p.id for p in presets)}"
            )
            console.print(
                Panel(
                    content,
                    title=color_gradient(
                        f"{ICONS['preset']} Preset Information", "blue", "green"
                    ),
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
    rows = [[p.name, p.description or "N/A"] for p in presets]
    table = create_colorful_table(
        f"{ICONS['preset']} Presets for {current_effect.attributes.name}",
        ["Name", "Description"],
        rows,
    )
    console.print(table)


@preset_app.command(name="apply")
@handle_exceptions
def apply_preset(ctx: typer.Context, preset_name: str):
    """Apply a preset to the current effect."""
    client = get_client(ctx)
    current_effect = client.get_current_effect()
    client.apply_effect_preset(current_effect.id, preset_name)
    console.print(
        f"{ICONS['preset']} Applied preset '[bold cyan]{preset_name}[/bold cyan]' to effect '[bold magenta]{current_effect.attributes.name}[/bold magenta]'"
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
            layout = next((ll for ll in layouts if ll.id == name), None)
            if layout:
                content = f"Layout: [bold cyan]{layout.id}[/bold cyan]\nType: [bold magenta]{layout.type}[/bold magenta]"
                console.print(
                    Panel(
                        content,
                        title=color_gradient(
                            f"{ICONS['layout']} Layout Information", "blue", "green"
                        ),
                        expand=False,
                        border_style="bold white",
                    )
                )
            else:
                console.print(
                    f"{STATUS_EMOJIS['error']} Layout '[bold]{name}[/bold]' not found"
                )
                raise typer.Exit(code=1)
        else:
            current_layout = client.current_layout
            content = (
                f"[bold cyan]Current Layout:[/bold cyan] {current_layout.id}\n"
                f"[bold magenta]Type:[/bold magenta] {current_layout.type}"
            )
            console.print(
                Panel(
                    content,
                    title=color_gradient(
                        f"{ICONS['layout']} Layout Information", "blue", "green"
                    ),
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
    rows = [[ll.id, ll.type] for ll in layouts]
    table = create_colorful_table(
        f"{ICONS['layout']} Available Layouts", ["ID", "Type"], rows
    )
    console.print(table)


@layout_app.command()
@handle_exceptions
def set(ctx: typer.Context, name: str):
    """Set the current layout."""
    client = get_client(ctx)
    client.current_layout = name
    console.print(
        f"{ICONS['layout']} Set current layout to: [bold cyan]{name}[/bold cyan]"
    )


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
        status = STATUS_EMOJIS["enabled"] if enabled else STATUS_EMOJIS["disabled"]
        content = (
            f"[bold cyan]Canvas State:[/bold cyan] {status} {'Enabled' if enabled else 'Disabled'}\n"
            f"[bold magenta]Brightness:[/bold magenta] {brightness}%"
        )
        title = color_gradient(f"{ICONS['canvas']} Canvas Information", "blue", "green")
        panel = Panel(content, title=title, expand=False, border_style="bold white")
        console.print(panel)


@canvas_app.command()
@handle_exceptions
def brightness(
    ctx: typer.Context, value: Optional[int] = typer.Argument(None, min=0, max=100)
):
    """Get or set the brightness level."""
    client = get_client(ctx)
    if value is not None:
        client.brightness = value
        console.print(
            f"{ICONS['canvas']} Set brightness to: [bold cyan]{value}%[/bold cyan]"
        )
    else:
        console.print(
            f"{ICONS['canvas']} Current brightness: [bold cyan]{client.brightness}%[/bold cyan]"
        )


@canvas_app.command()
@handle_exceptions
def enable(ctx: typer.Context):
    """Enable the canvas."""
    client = get_client(ctx)
    client.enabled = True
    console.print(
        f"{ICONS['canvas']} Canvas {STATUS_EMOJIS['enabled']} [bold green]enabled[/bold green]"
    )


@canvas_app.command()
@handle_exceptions
def disable(ctx: typer.Context):
    """Disable the canvas."""
    client = get_client(ctx)
    client.enabled = False
    console.print(
        f"{ICONS['canvas']} Canvas {STATUS_EMOJIS['disabled']} [bold red]disabled[/bold red]"
    )


@canvas_app.command()
@handle_exceptions
def toggle(ctx: typer.Context):
    """Toggle the canvas enabled state."""
    client = get_client(ctx)
    client.enabled = not client.enabled
    status = "enabled" if client.enabled else "disabled"
    emoji = STATUS_EMOJIS["enabled"] if client.enabled else STATUS_EMOJIS["disabled"]
    color = "green" if client.enabled else "red"
    console.print(
        f"{ICONS['canvas']} Canvas {emoji} [bold {color}]{status}[/bold {color}]"
    )


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
