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

# Global variable to track Full RGB mode
FULL_RGB_MODE = False

# RGB Gradient
GRADIENT_COLORS = [
    "#ff99cc",  # Light Pink
    "#ff66b2",  # Pink
    "#ff4da6",  # Bright Pink
    "#ff3399",  # Hot Pink
    "#ff66ff",  # Magenta
    "#cc33ff",  # Soft Violet
    "#9933ff",  # Purple
    "#6600cc",  # Deep Purple
    "#3333ff",  # Indigo
    "#3399ff",  # Light Blue
    "#33ccff",  # Cyan
    "#33ffcc",  # Aqua
    "#33ff99",  # Mint
    "#33ff66",  # Lime Green
    "#99ff33",  # Bright Green
    "#ccff33",  # Yellow-Green
    "#ffff33",  # Yellow
    "#ffcc33",  # Gold
    "#ff9933",  # Orange
    "#ff6633",  # Bright Orange
    "#ff3333",  # Red
    "#ff3366",  # Pink-Red
]


# Purple color for table borders
BORDER_COLOR = "purple"


def generate_gradient_markup(colors: List[str], steps: int) -> List[str]:
    gradient = []
    segments = len(colors) - 1
    steps_per_segment = max(1, steps // segments)

    for i in range(segments):
        start_color = colors[i]
        end_color = colors[i + 1]
        for j in range(steps_per_segment):
            t = j / steps_per_segment
            r = int(int(start_color[1:3], 16) * (1 - t) + int(end_color[1:3], 16) * t)
            g = int(int(start_color[3:5], 16) * (1 - t) + int(end_color[3:5], 16) * t)
            b = int(int(start_color[5:7], 16) * (1 - t) + int(end_color[5:7], 16) * t)
            gradient.append(f"#{r:02x}{g:02x}{b:02x}")

    return gradient


def apply_gradient_to_text(text: str, colors: List[str], line_offset: int = 0) -> str:
    # Apply Rich's color styles for each character with a diagonal offset
    gradient = generate_gradient_markup(colors, len(text))
    styled_text = ""
    for i, char in enumerate(text):
        color = gradient[(i + line_offset) % len(gradient)]
        styled_text += f"[{color}]{char}[/]"
    return styled_text


def color_gradient(text: str, colors: List[str], line_number: int = 0) -> Text:
    if FULL_RGB_MODE:
        return apply_gradient_to_text(text, colors, line_number)
    else:
        return Text(text, style="bold green")


def print_rgb(message: str):
    if FULL_RGB_MODE:
        styled_message = color_gradient(message, GRADIENT_COLORS)
        console.print(styled_message)
    else:
        console.print(message)


def get_client(ctx: typer.Context) -> SignalRGBClient:
    return ctx.obj


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            print_rgb(f"{STATUS_EMOJIS['error']} Connection Error: {str(e)}")
            raise typer.Exit(code=1)
        except APIError as e:
            print_rgb(f"{STATUS_EMOJIS['error']} API Error: {str(e)}")
            raise typer.Exit(code=1)
        except NotFoundError as e:
            print_rgb(f"{STATUS_EMOJIS['error']} Not Found: {str(e)}")
            raise typer.Exit(code=1)
        except SignalRGBException as e:
            print_rgb(f"{STATUS_EMOJIS['error']} Error: {str(e)}")
            raise typer.Exit(code=1)

    return wrapper


def create_effect_panel(effect, title: str) -> Panel:
    content_lines = [
        f"ID: {effect.id}",
        f"Name: {effect.attributes.name}",
        f"Publisher: {effect.attributes.publisher or 'N/A'}",
        f"Description: {effect.attributes.description or 'N/A'}",
        f"Uses Audio: {STATUS_EMOJIS['enabled'] if effect.attributes.uses_audio else STATUS_EMOJIS['disabled']}",
        f"Uses Video: {STATUS_EMOJIS['enabled'] if effect.attributes.uses_video else STATUS_EMOJIS['disabled']}",
        f"Uses Input: {STATUS_EMOJIS['enabled'] if effect.attributes.uses_input else STATUS_EMOJIS['disabled']}",
        f"Uses Meters: {STATUS_EMOJIS['enabled'] if effect.attributes.uses_meters else STATUS_EMOJIS['disabled']}",
    ]
    if FULL_RGB_MODE:
        content = "\n".join(
            apply_gradient_to_text(line, GRADIENT_COLORS, line_offset=i)
            for i, line in enumerate(content_lines)
        )
    else:
        content = "\n".join(content_lines)
    return Panel(
        content,
        title=color_gradient(title, GRADIENT_COLORS),
        expand=False,
        border_style=BORDER_COLOR,
    )


def create_param_table(parameters):
    headers = ["Parameter", "Value"]
    rows = [
        [key, str(value) if not isinstance(value, bool) else ("Yes" if value else "No")]
        for key, value in parameters.items()
    ]

    table = create_colorful_table(
        title=f"{ICONS['effect']} Effect Parameters", headers=headers, rows=rows
    )

    return table


# Ensure that create_colorful_table is defined as follows:
def create_colorful_table(title: str, headers: List[str], rows: List[List[str]]):
    table = Table(
        title=color_gradient(title, GRADIENT_COLORS),
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        border_style=BORDER_COLOR,
        expand=True,
    )

    for header in headers:
        table.add_column(header)

    for i, row in enumerate(rows):
        styled_row = []
        for cell in row:
            if FULL_RGB_MODE:
                cell_text = apply_gradient_to_text(cell, GRADIENT_COLORS, line_offset=i)
            else:
                cell_text = Text(cell)
            styled_row.append(cell_text)
        table.add_row(*styled_row)

    return table


def create_colorful_table(title: str, headers: List[str], rows: List[List[str]]):
    table = Table(
        title=color_gradient(title, GRADIENT_COLORS),
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        border_style=BORDER_COLOR,
    )

    for header in headers:
        table.add_column(header)

    for i, row in enumerate(rows):
        styled_row = []
        for cell in row:
            if FULL_RGB_MODE:
                cell_text = apply_gradient_to_text(cell, GRADIENT_COLORS, line_offset=i)
            else:
                cell_text = Text(cell)
            styled_row.append(cell_text)
        table.add_row(*styled_row)

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
    print_rgb(
        f"{ICONS['effect']} Applied effect: {name}"
        + (f" with preset: {preset}" if preset else "")
    )


@effect_app.command()
@handle_exceptions
def next(ctx: typer.Context):
    """Apply the next effect in history."""
    client = get_client(ctx)
    effect = client.apply_next_effect()
    print_rgb(f"{ICONS['effect']} Applied next effect: {effect.attributes.name}")


@effect_app.command()
@handle_exceptions
def previous(ctx: typer.Context):
    """Apply the previous effect in history."""
    client = get_client(ctx)
    effect = client.apply_previous_effect()
    print_rgb(f"{ICONS['effect']} Applied previous effect: {effect.attributes.name}")


@effect_app.command()
@handle_exceptions
def random(ctx: typer.Context):
    """Apply a random effect."""
    client = get_client(ctx)
    effect = client.apply_random_effect()
    print_rgb(f"{ICONS['effect']} Applied random effect: {effect.attributes.name}")


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
            f"{ICONS['effect']} Cycling effects...", total=len(effects)
        )
        for effect in effects:
            client.apply_effect(effect.id)
            progress.update(
                task,
                advance=1,
                description=f"{ICONS['effect']} Applied: {effect.attributes.name}",
            )
            time.sleep(duration)
    print_rgb(f"{ICONS['effect']} Finished cycling through all effects")


@effect_app.command()
@handle_exceptions
def refresh(ctx: typer.Context):
    """Refresh the cached effects."""
    client = get_client(ctx)
    client.refresh_effects()
    print_rgb(f"{ICONS['effect']} Effects cache refreshed")


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
            preset = next((p for p in presets if p.id == name), None)
            if preset:
                content = f"Preset: {preset.id}\nType: {preset.type}"
                if FULL_RGB_MODE:
                    content = apply_gradient_to_text(content, GRADIENT_COLORS)
                console.print(
                    Panel(
                        content,
                        title=color_gradient(
                            f"{ICONS['preset']} Preset Information", GRADIENT_COLORS
                        ),
                        expand=False,
                        border_style=BORDER_COLOR,
                    )
                )
            else:
                print_rgb(
                    f"{STATUS_EMOJIS['error']} Preset '{name}' not found for effect '{current_effect.attributes.name}'"
                )
                raise typer.Exit(code=1)
        else:
            content = (
                f"Current Effect: {current_effect.attributes.name}\n"
                f"Available Presets: {', '.join(p.id for p in presets)}"
            )
            if FULL_RGB_MODE:
                content = apply_gradient_to_text(content, GRADIENT_COLORS)
            console.print(
                Panel(
                    content,
                    title=color_gradient(
                        f"{ICONS['preset']} Preset Information", GRADIENT_COLORS
                    ),
                    expand=False,
                    border_style=BORDER_COLOR,
                )
            )


@preset_app.command(name="list")
@handle_exceptions
def list_presets(ctx: typer.Context):
    """List presets for the current effect."""
    client = get_client(ctx)
    current_effect = client.get_current_effect()
    presets = client.get_effect_presets(current_effect.id)
    rows = [[p.id, p.type] for p in presets]
    table = create_colorful_table(
        f"{ICONS['preset']} Presets for {current_effect.attributes.name}",
        ["ID", "Type"],
        rows,
    )
    console.print(table)


@preset_app.command(name="apply")
@handle_exceptions
def apply_preset(ctx: typer.Context, preset_id: str):
    """Apply a preset to the current effect."""
    client = get_client(ctx)
    current_effect = client.get_current_effect()
    client.apply_effect_preset(current_effect.id, preset_id)
    print_rgb(
        f"{ICONS['preset']} Applied preset '{preset_id}' to effect '{current_effect.attributes.name}'"
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
                content = f"Layout: {layout.id}\nType: {layout.type}"
                if FULL_RGB_MODE:
                    content = apply_gradient_to_text(content, GRADIENT_COLORS)
                console.print(
                    Panel(
                        content,
                        title=color_gradient(
                            f"{ICONS['layout']} Layout Information", GRADIENT_COLORS
                        ),
                        expand=False,
                        border_style=BORDER_COLOR,
                    )
                )
            else:
                print_rgb(f"{STATUS_EMOJIS['error']} Layout '{name}' not found")
                raise typer.Exit(code=1)
        else:
            current_layout = client.current_layout
            content = (
                f"Current Layout: {current_layout.id}\n" f"Type: {current_layout.type}"
            )
            if FULL_RGB_MODE:
                content = apply_gradient_to_text(content, GRADIENT_COLORS)
            console.print(
                Panel(
                    content,
                    title=color_gradient(
                        f"{ICONS['layout']} Layout Information", GRADIENT_COLORS
                    ),
                    expand=False,
                    border_style=BORDER_COLOR,
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
    print_rgb(f"{ICONS['layout']} Set current layout to: {name}")


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
            f"Canvas State: {status} {'Enabled' if enabled else 'Disabled'}\n"
            f"Brightness: {brightness}%"
        )
        if FULL_RGB_MODE:
            content = apply_gradient_to_text(content, GRADIENT_COLORS)
        title = color_gradient(f"{ICONS['canvas']} Canvas Information", GRADIENT_COLORS)
        panel = Panel(content, title=title, expand=False, border_style=BORDER_COLOR)
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
        print_rgb(f"{ICONS['canvas']} Set brightness to: {value}%")
    else:
        print_rgb(f"{ICONS['canvas']} Current brightness: {client.brightness}%")


@canvas_app.command()
@handle_exceptions
def enable(ctx: typer.Context):
    """Enable the canvas."""
    client = get_client(ctx)
    client.enabled = True
    print_rgb(f"{ICONS['canvas']} Canvas {STATUS_EMOJIS['enabled']} enabled")


@canvas_app.command()
@handle_exceptions
def disable(ctx: typer.Context):
    """Disable the canvas."""
    client = get_client(ctx)
    client.enabled = False
    print_rgb(f"{ICONS['canvas']} Canvas {STATUS_EMOJIS['disabled']} disabled")


@canvas_app.command()
@handle_exceptions
def toggle(ctx: typer.Context):
    """Toggle the canvas enabled state."""
    client = get_client(ctx)
    client.enabled = not client.enabled
    status = "enabled" if client.enabled else "disabled"
    emoji = STATUS_EMOJIS["enabled"] if client.enabled else STATUS_EMOJIS["disabled"]
    print_rgb(f"{ICONS['canvas']} Canvas {emoji} {status}")


@app.callback()
def main(
    ctx: typer.Context,
    host: str = typer.Option("localhost", help="SignalRGB API host"),
    port: int = typer.Option(16038, help="SignalRGB API port"),
    full_rgb: bool = typer.Option(
        False, "--full-rgb", help="Enable full RGB gradient mode for all output"
    ),
):
    """Initialize SignalRGB client."""
    global FULL_RGB_MODE
    FULL_RGB_MODE = full_rgb
    ctx.obj = SignalRGBClient(host, port)


if __name__ == "__main__":
    app()
