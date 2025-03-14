from collections.abc import Callable
from functools import wraps
import time
from typing import Any, TypeVar, cast

from rich import box
from rich.columns import Columns
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text
import typer

from .client import SignalRGBClient
from .exceptions import (
    APIError,
    ConnectionError,
    NotFoundError,
    SignalRGBException,
)

PANEL_WIDTH = 100

app = typer.Typer(help="SignalRGB CLI")
console = Console()

ICONS = {
    "effect": "🌠",
    "preset": "🎨",
    "layout": "🖼️",
    "canvas": "🖥️",
    "audio": "🎵",
    "video": "🎬",
    "input": "🕹️",
    "meters": "📊",
}

STATUS_EMOJIS = {
    "enabled": "✨",
    "disabled": "🌑",
    "warning": "⚠️",
    "error": "🚫",
}

# Global variable to track Full RGB mode
FULL_RGB_MODE = False

# RGB Gradient colors for full RGB mode
GRADIENT_COLORS = [
    "#ff99cc",
    "#ff66b2",
    "#ff4da6",
    "#ff3399",
    "#ff66ff",
    "#cc33ff",
    "#9933ff",
    "#6600cc",
    "#3333ff",
    "#3399ff",
    "#33ccff",
    "#33ffcc",
    "#33ff99",
    "#33ff66",
    "#99ff33",
    "#ccff33",
    "#ffff33",
    "#ffcc33",
    "#ff9933",
    "#ff6633",
    "#ff3333",
    "#ff3366",
]

# Color palette for normal mode
NORMAL_PALETTE = {
    "primary": "bright_magenta",
    "secondary": "bright_cyan",
    "title": "bright_magenta",
    "subtitle": "bright_cyan",
    "label": "deep_sky_blue1",
    "value": "light_sea_green",
    "description": "grey70",
    "parameter": "orchid",
    "parameter_value": "medium_spring_green",
    "border": "bright_blue",
    "accent": "bright_green",
    "info": "bright_blue",
    "error": "bright_red",
}

# Purple color for table borders
BORDER_COLOR = "purple"


class FlexibleTable(Table):
    """A Table that adjusts its width based on the console width."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.original_width = kwargs.get("width")

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        if self.original_width is not None and options.max_width is not None:
            self.width = min(self.original_width, options.max_width)
        yield from super().__rich_console__(console, options)


def generate_gradient_markup(colors: list[str], steps: int) -> list[str]:
    """Generate a list of color codes for gradient effect."""
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


def apply_gradient_to_text(text: str, colors: list[str], line_offset: int = 0) -> Text:
    """Apply gradient coloring to text using Rich's Text object."""
    gradient = generate_gradient_markup(colors, len(text))
    styled_text = Text()

    for i, char in enumerate(text):
        color = gradient[(i + line_offset) % len(gradient)]
        styled_text.append(char, style=f"{color}")

    return styled_text


def color_gradient(text: str, colors: list[str], line_number: int = 0) -> Text:
    """Apply color gradient or normal coloring based on mode."""
    return apply_gradient_to_text(text, colors, line_number)


def print_rgb(message: str, style: str = "primary") -> None:
    """Print message with appropriate coloring based on mode."""
    if FULL_RGB_MODE:
        styled_message = color_gradient(message, GRADIENT_COLORS)
        console.print(styled_message)
    else:
        console.print(message, style=NORMAL_PALETTE[style])


def get_client(ctx: typer.Context) -> SignalRGBClient:
    """Get the SignalRGB client from the Typer context."""
    return cast(SignalRGBClient, ctx.obj)


F = TypeVar("F", bound=Callable[..., Any])


def handle_exceptions(func: F) -> F:
    """Decorator to handle exceptions in CLI commands."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            print_rgb(f"{STATUS_EMOJIS['error']} Connection Error: {e!s}", "error")
            raise typer.Exit(code=1) from e
        except APIError as e:
            print_rgb(f"{STATUS_EMOJIS['error']} API Error: {e!s}", "error")
            raise typer.Exit(code=1) from e
        except NotFoundError as e:
            print_rgb(f"{STATUS_EMOJIS['error']} Not Found: {e!s}", "error")
            raise typer.Exit(code=1) from e
        except SignalRGBException as e:
            print_rgb(f"{STATUS_EMOJIS['error']} Error: {e!s}", "error")
            raise typer.Exit(code=1) from e

    return cast(F, wrapper)


def get_column_widths(items: list[tuple[str, str]]) -> tuple[int, int]:
    """Calculate column widths based on content."""
    max_label_width = max(len(key) for key, _ in items)
    label_column_width = max(max_label_width, 20)  # Minimum width of 20 characters
    value_column_width = (PANEL_WIDTH // 2) - label_column_width - 4  # 4 for padding and separators
    return label_column_width, value_column_width


def create_section(content: list[tuple[str, str]], width: int) -> FlexibleTable:
    label_column_width, value_column_width = get_column_widths(content)

    table = FlexibleTable(show_header=False, padding=(0, 1), expand=False, box=None, width=width)
    table.add_column(style=NORMAL_PALETTE["label"], width=label_column_width, no_wrap=True)
    table.add_column(style=NORMAL_PALETTE["value"], width=value_column_width)

    for i, (label, value) in enumerate(content):
        if FULL_RGB_MODE:
            label_text = apply_gradient_to_text(label, GRADIENT_COLORS, line_offset=i)
            value_text = apply_gradient_to_text(value, GRADIENT_COLORS, line_offset=i)
            table.add_row(label_text, value_text)
        else:
            table.add_row(label, value)
    return table


def create_effect_panel(effect: Any, title: str) -> Panel:
    """Create a panel displaying effect details with an enhanced layout."""

    # Info Section
    info = create_section(
        [
            ("ID", effect.id),
            ("Name", effect.attributes.name),
            ("Publisher", effect.attributes.publisher or "N/A"),
        ],
        PANEL_WIDTH // 2,  # Set width to half the panel width
    )

    # Capabilities Section
    capabilities = create_section(
        [
            (
                "Uses Audio",
                STATUS_EMOJIS["enabled"] if effect.attributes.uses_audio else STATUS_EMOJIS["disabled"],
            ),
            (
                "Uses Video",
                STATUS_EMOJIS["enabled"] if effect.attributes.uses_video else STATUS_EMOJIS["disabled"],
            ),
            (
                "Uses Input",
                STATUS_EMOJIS["enabled"] if effect.attributes.uses_input else STATUS_EMOJIS["disabled"],
            ),
            (
                "Uses Meters",
                STATUS_EMOJIS["enabled"] if effect.attributes.uses_meters else STATUS_EMOJIS["disabled"],
            ),
        ],
        (PANEL_WIDTH // 2) - 5,
    )

    # Combine info and capabilities side by side
    top_section = Columns([info, capabilities], expand=True)

    # Description Section
    description = effect.attributes.description or "N/A"
    description_text = description
    if FULL_RGB_MODE:
        description_text = apply_gradient_to_text(description, GRADIENT_COLORS)

    # Combine all sections
    content = Group(top_section, "", description_text)  # Empty string adds a blank line

    return Panel(
        content,
        title=color_gradient(f"{ICONS['effect']} {title}", GRADIENT_COLORS),
        expand=False,
        border_style=NORMAL_PALETTE["border"],
        width=PANEL_WIDTH,
    )


def create_param_table(parameters: dict[str, Any]) -> Panel:
    """Create a table displaying effect parameters with enhanced layout."""
    label_column_width, value_column_width = get_column_widths(list(parameters.items()))

    table = FlexibleTable(box=None, show_header=False, expand=False, width=PANEL_WIDTH // 2)

    table.add_column(style=NORMAL_PALETTE["parameter"], width=label_column_width, no_wrap=True)
    table.add_column(style=NORMAL_PALETTE["parameter_value"], width=value_column_width)

    param_items = list(parameters.items())
    mid_point = len(param_items) // 2 + len(param_items) % 2

    for i, (key, value) in enumerate(param_items[:mid_point]):
        label, formatted_value = format_parameter(key, value)
        if FULL_RGB_MODE:
            label_text = apply_gradient_to_text(label, GRADIENT_COLORS, line_offset=i)
            if isinstance(formatted_value, str) and "■■■■" not in formatted_value:
                value_text = apply_gradient_to_text(formatted_value, GRADIENT_COLORS, line_offset=i)
                table.add_row(label_text, value_text)
            else:
                table.add_row(label_text, formatted_value)
        else:
            table.add_row(label, formatted_value)

    return Panel(
        Columns([table], expand=True, equal=True),
        title=color_gradient(f"{ICONS['effect']} Parameters", GRADIENT_COLORS),
        expand=False,
        border_style=NORMAL_PALETTE["border"],
        width=PANEL_WIDTH,
    )


def format_parameter(key: Any, value: Any) -> tuple[str, str | Text]:
    """Format parameter based on its structure."""
    if isinstance(value, dict) and "label" in value and "value" in value:
        return value["label"], format_parameter_value(value["value"], value.get("type"))
    return key, format_parameter_value(value)


def format_parameter_value(value: Any, param_type: str | None = None) -> str | Text:
    """Format parameter value based on its type."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if param_type == "color":
        return f"[{value}]■■■■[/]"  # Display a colored square
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return ", ".join(f"{k}: {v}" for k, v in value.items())
    if isinstance(value, list):
        return ", ".join(map(str, value))
    return str(value)  # Default case


def create_colorful_table(title: str, headers: list[str], rows: list[list[str]]) -> Table:
    """Create a colorful table with the given title, headers, and rows."""
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
                cell_text = Text(cell, style=NORMAL_PALETTE["secondary"])
            styled_row.append(cell_text)
        table.add_row(*styled_row)

    return table


# Effect commands
effect_app = typer.Typer(help="Manage effects", invoke_without_command=True)
app.add_typer(effect_app, name="effect")


@effect_app.callback(invoke_without_command=True)
@handle_exceptions
def effect(ctx: typer.Context, name: str | None = None) -> None:
    """Show details of the current effect or a specific effect."""
    if ctx.invoked_subcommand is None:
        client = get_client(ctx)
        effect = client.get_effect_by_name(name) if name else client.get_current_effect()
        console.print(create_effect_panel(effect, f"{effect.attributes.name}"))
        if effect.attributes.parameters:
            console.print(create_param_table(effect.attributes.parameters))


@effect_app.command(name="list")
@handle_exceptions
def list_effects(ctx: typer.Context) -> None:
    """List all available effects."""
    client = get_client(ctx)
    effects = client.get_effects()

    rows = [[e.attributes.name, e.id] for e in effects]
    table = create_colorful_table(f"{ICONS['effect']} Available Effects", ["Name", "ID"], rows)
    console.print(table)


@effect_app.command()
@handle_exceptions
def search(ctx: typer.Context, query: str) -> None:
    """Search for effects by name or description."""
    client = get_client(ctx)
    effects = client.get_effects()
    matched_effects = [
        e
        for e in effects
        if query.lower() in e.attributes.name.lower()
        or (e.attributes.description and query.lower() in e.attributes.description.lower())
    ]
    rows = [[e.attributes.name, e.attributes.description or "N/A"] for e in matched_effects]
    table = create_colorful_table(f"{ICONS['effect']} Search Results for '{query}'", ["Name", "Description"], rows)
    console.print(table)


@effect_app.command(name="apply")
@handle_exceptions
def apply_effect(ctx: typer.Context, name: str, preset: str | None = None) -> None:
    """Apply an effect, optionally with a preset."""
    client = get_client(ctx)
    client.apply_effect_by_name(name)
    if preset:
        client.apply_effect_preset(client.get_effect_by_name(name).id, preset)
    print_rgb(
        f"{ICONS['effect']} Applied effect: {name}" + (f" with preset: {preset}" if preset else ""),
        "accent",
    )


@effect_app.command(name="next_effect")
@handle_exceptions
def next_effect(ctx: typer.Context) -> None:
    """Apply the next effect in history."""
    client = get_client(ctx)
    effect = client.apply_next_effect()
    print_rgb(f"{ICONS['effect']} Applied next effect: {effect.attributes.name}", "accent")


@effect_app.command(name="previous_effect")
@handle_exceptions
def previous_effect(ctx: typer.Context) -> None:
    """Apply the previous effect in history."""
    client = get_client(ctx)
    effect = client.apply_previous_effect()
    print_rgb(f"{ICONS['effect']} Applied previous effect: {effect.attributes.name}", "accent")


@effect_app.command()
@handle_exceptions
def random(ctx: typer.Context) -> None:
    """Apply a random effect."""
    client = get_client(ctx)
    effect = client.apply_random_effect()
    print_rgb(f"{ICONS['effect']} Applied random effect: {effect.attributes.name}", "accent")


@effect_app.command()
@handle_exceptions
def cycle(
    ctx: typer.Context,
    duration: int = typer.Option(5, help="Duration to display each effect in seconds"),
) -> None:
    """Cycle through all effects."""
    client = get_client(ctx)
    effects = client.get_effects()
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task(f"{ICONS['effect']} Cycling effects...", total=len(effects))
        for effect in effects:
            client.apply_effect(effect.id)
            progress.update(
                task,
                advance=1,
                description=f"{ICONS['effect']} Applied: {effect.attributes.name}",
            )
            time.sleep(duration)
    print_rgb(f"{ICONS['effect']} Finished cycling through all effects", "accent")


@effect_app.command()
@handle_exceptions
def refresh(ctx: typer.Context) -> None:
    """Refresh the cached effects."""
    client = get_client(ctx)
    client.refresh_effects()
    print_rgb(f"{ICONS['effect']} Effects cache refreshed", "info")


# Preset commands
preset_app = typer.Typer(help="Manage presets", invoke_without_command=True)
app.add_typer(preset_app, name="preset")


@preset_app.callback(invoke_without_command=True)
@handle_exceptions
def preset(ctx: typer.Context, name: str | None = None) -> None:
    """Show details of the current preset or a specific preset."""
    if ctx.invoked_subcommand is None:
        client = get_client(ctx)
        current_effect = client.get_current_effect()
        presets = client.get_effect_presets(current_effect.id)
        if name:
            preset = next((p for p in presets if p.id == name), None)
            if preset:
                content = f"Preset: {preset.id}"
                content_display: str | Text = content
                if FULL_RGB_MODE:
                    content_display = apply_gradient_to_text(content, GRADIENT_COLORS)
                console.print(
                    Panel(
                        content_display,
                        title=color_gradient(f"{ICONS['preset']} Preset Information", GRADIENT_COLORS),
                        expand=False,
                        border_style=BORDER_COLOR,
                    )
                )


@preset_app.command(name="list")
@handle_exceptions
def list_presets(ctx: typer.Context) -> None:
    """List presets for the current effect."""
    client = get_client(ctx)
    current_effect = client.get_current_effect()
    presets = client.get_effect_presets(current_effect.id)
    rows = [[p.id] for p in presets]
    table = create_colorful_table(
        f"{ICONS['preset']} Presets for {current_effect.attributes.name}",
        ["Preset"],
        rows,
    )
    console.print(table)


@preset_app.command(name="apply")
@handle_exceptions
def apply_preset(ctx: typer.Context, preset_id: str) -> None:
    """Apply a preset to the current effect."""
    client = get_client(ctx)
    current_effect = client.get_current_effect()
    client.apply_effect_preset(current_effect.id, preset_id)
    print_rgb(
        f"{ICONS['preset']} Applied preset '{preset_id}' to effect '{current_effect.attributes.name}'",
        "accent",
    )


# Layout commands
layout_app = typer.Typer(help="Manage layouts", invoke_without_command=True)
app.add_typer(layout_app, name="layout")


@layout_app.callback(invoke_without_command=True)
@handle_exceptions
def layout(ctx: typer.Context, name: str | None = None) -> None:
    """Show details of the current layout or a specific layout."""
    if ctx.invoked_subcommand is None:
        client = get_client(ctx)
        if name:
            layouts = client.get_layouts()
            layout_obj = next((ll for ll in layouts if ll.id == name), None)
            if layout_obj:
                content = f"Layout: {layout_obj.id}"
                content_display: str | Text = content
                if FULL_RGB_MODE:
                    content_display = apply_gradient_to_text(content, GRADIENT_COLORS)
                console.print(
                    Panel(
                        content_display,
                        title=color_gradient(f"{ICONS['layout']} Layout Information", GRADIENT_COLORS),
                        expand=False,
                        border_style=BORDER_COLOR,
                    )
                )
            else:
                print_rgb(f"{STATUS_EMOJIS['error']} Layout '{name}' not found", "error")
                raise typer.Exit(code=1) from None
        else:
            current_layout = client.current_layout
            content_current = f"Current Layout: {current_layout.id}"
            content_display_current: str | Text = content_current
            if FULL_RGB_MODE:
                content_display_current = apply_gradient_to_text(content_current, GRADIENT_COLORS)
            console.print(
                Panel(
                    content_display_current,
                    title=color_gradient(f"{ICONS['layout']} Layout Information", GRADIENT_COLORS),
                    expand=False,
                    border_style=BORDER_COLOR,
                )
            )


@layout_app.command(name="list")
@handle_exceptions
def list_layouts(ctx: typer.Context) -> None:
    """List all available layouts."""
    client = get_client(ctx)
    layouts = client.get_layouts()
    rows = [[layout.id] for layout in layouts]
    table = create_colorful_table(f"{ICONS['layout']} Available Layouts", ["Layout ID"], rows)
    console.print(table)


@layout_app.command(name="set_layout")
@handle_exceptions
def set_layout(ctx: typer.Context, name: str) -> None:
    """Set the current layout."""
    client = get_client(ctx)
    client.current_layout = name  # type: ignore
    print_rgb(f"{ICONS['layout']} Set current layout to: {name}", "accent")


# Canvas commands
canvas_app = typer.Typer(
    help="Manage canvas settings like brightness and enabled state.",
    invoke_without_command=True,
)
app.add_typer(canvas_app, name="canvas")


@canvas_app.callback(invoke_without_command=True)
@handle_exceptions
def canvas(ctx: typer.Context) -> None:
    """Show current canvas state."""
    if ctx.invoked_subcommand is None:
        client = get_client(ctx)
        enabled = client.enabled
        brightness = client.brightness

        # Prepare the data to be displayed in the table
        status = STATUS_EMOJIS["enabled"] if enabled else STATUS_EMOJIS["disabled"]
        rows = [
            ["Canvas State", f"{status} {'Enabled' if enabled else 'Disabled'}"],
            ["Brightness", f"{brightness}%"],
        ]

        # Use create_colorful_table to create the table
        table = create_colorful_table(
            f"{ICONS['canvas']} Canvas Information",
            headers=["Property", "Value"],
            rows=rows,
        )

        # Print the table in a panel
        console.print(table)


@canvas_app.command()
@handle_exceptions
def brightness(ctx: typer.Context, value: int | None = typer.Argument(None, min=0, max=100)) -> None:
    """Get or set the brightness level."""
    client = get_client(ctx)
    if value is not None:
        client.brightness = value
        print_rgb(f"{ICONS['canvas']} Set brightness to: {value}%", "accent")
    else:
        print_rgb(f"{ICONS['canvas']} Current brightness: {client.brightness}%", "info")


@canvas_app.command()
@handle_exceptions
def enable(ctx: typer.Context) -> None:
    """Enable the canvas."""
    client = get_client(ctx)
    client.enabled = True
    print_rgb(f"{ICONS['canvas']} Canvas {STATUS_EMOJIS['enabled']} enabled", "accent")


@canvas_app.command()
@handle_exceptions
def disable(ctx: typer.Context) -> None:
    """Disable the canvas."""
    client = get_client(ctx)
    client.enabled = False
    print_rgb(f"{ICONS['canvas']} Canvas {STATUS_EMOJIS['disabled']} disabled", "accent")


@canvas_app.command()
@handle_exceptions
def toggle(ctx: typer.Context) -> None:
    """Toggle the canvas enabled state."""
    client = get_client(ctx)
    client.enabled = not client.enabled
    status = "enabled" if client.enabled else "disabled"
    emoji = STATUS_EMOJIS["enabled"] if client.enabled else STATUS_EMOJIS["disabled"]
    print_rgb(f"{ICONS['canvas']} Canvas {emoji} {status}", "accent")


@app.callback()
def main(
    ctx: typer.Context,
    host: str = typer.Option("localhost", help="SignalRGB API host"),
    port: int = typer.Option(16038, help="SignalRGB API port"),
    full_rgb: bool = typer.Option(False, "--full-rgb", help="Enable full RGB gradient mode for all output"),
) -> None:
    """Initialize SignalRGB client."""
    # Store RGB mode in a context variable instead of using global
    ctx.ensure_object(dict)
    ctx.obj = SignalRGBClient(host, port)
    # Store RGB mode in the context
    ctx.meta["full_rgb_mode"] = full_rgb
    # Still need to set global for backward compatibility
    # pylint: disable=global-statement
    global FULL_RGB_MODE
    FULL_RGB_MODE = full_rgb


# Function to set RGB mode for testing or programmatic use
def set_rgb_mode(enabled: bool) -> None:
    """Set the RGB mode programmatically.

    This is useful for testing or when using the CLI programmatically.

    Args:
        enabled: Whether to enable full RGB mode
    """
    # This is a utility function that needs to modify the global state
    # pylint: disable=global-statement
    global FULL_RGB_MODE
    FULL_RGB_MODE = enabled


if __name__ == "__main__":
    app()
