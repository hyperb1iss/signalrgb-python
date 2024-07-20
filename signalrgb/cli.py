import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box
from typing import Optional
from .client import SignalRGBClient, DEFAULT_PORT, SignalRGBException

app = typer.Typer(help="Command line interface for SignalRGB API")
console = Console()

@app.callback()
def callback(ctx: typer.Context,
             host: str = typer.Option("localhost", help="SignalRGB API host"),
             port: int = typer.Option(DEFAULT_PORT, help="SignalRGB API port")):
    """Initialize SignalRGB client"""
    ctx.obj = SignalRGBClient(host, port)

@app.command()
def list_effects(ctx: typer.Context):
    """List all available effects"""
    client: SignalRGBClient = ctx.obj
    try:
        effects = client.get_effects()
        table = Table(title="Available Effects", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Publisher", style="green")

        for effect in effects:
            table.add_row(effect.id, effect.attributes.name, effect.attributes.publisher or "N/A")

        console.print(table)
    except SignalRGBException as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command()
def get_effect(ctx: typer.Context, effect_name: str):
    """Get details of a specific effect"""
    client: SignalRGBClient = ctx.obj
    try:
        effect = client.get_effect_by_name(effect_name)
        panel = Panel(
            f"[bold cyan]ID:[/bold cyan] {effect.id}\n"
            f"[bold magenta]Name:[/bold magenta] {effect.attributes.name}\n"
            f"[bold green]Publisher:[/bold green] {effect.attributes.publisher or 'N/A'}\n"
            f"[bold yellow]Description:[/bold yellow] {effect.attributes.description or 'N/A'}\n"
            f"[bold blue]Uses Audio:[/bold blue] {effect.attributes.uses_audio}\n"
            f"[bold blue]Uses Video:[/bold blue] {effect.attributes.uses_video}\n"
            f"[bold blue]Uses Input:[/bold blue] {effect.attributes.uses_input}\n"
            f"[bold blue]Uses Meters:[/bold blue] {effect.attributes.uses_meters}",
            title="Effect Details",
            expand=False
        )
        console.print(panel)

        if effect.attributes.parameters:
            param_table = Table(title="Effect Parameters", box=box.ROUNDED)
            param_table.add_column("Parameter", style="cyan")
            param_table.add_column("Value", style="magenta")
            for key, value in effect.attributes.parameters.items():
                param_table.add_row(str(key), str(value))
            console.print(param_table)
    except SignalRGBException as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command()
def current_effect(ctx: typer.Context):
    """Get the current effect"""
    client: SignalRGBClient = ctx.obj
    try:
        effect = client.get_current_effect()
        panel = Panel(
            f"[bold cyan]ID:[/bold cyan] {effect.id}\n"
            f"[bold magenta]Name:[/bold magenta] {effect.attributes.name}\n"
            f"[bold green]Publisher:[/bold green] {effect.attributes.publisher or 'N/A'}",
            title="Current Effect",
            expand=False
        )
        console.print(panel)
    except SignalRGBException as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command()
def apply_effect(ctx: typer.Context, effect_name: str):
    """Apply an effect"""
    client: SignalRGBClient = ctx.obj
    try:
        client.apply_effect_by_name(effect_name)
        console.print(f"[bold green]Successfully applied effect:[/bold green] {effect_name}")
    except SignalRGBException as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    app()