import click
from .client import SignalRGBClient, DEFAULT_PORT


@click.group()
@click.option("--host", default="localhost", help="SignalRGB API host")
@click.option("--port", default=DEFAULT_PORT, help="SignalRGB API port")
@click.pass_context
def cli(ctx, host, port):
    """Command line interface for SignalRGB API"""
    ctx.obj = SignalRGBClient(host, port)


@cli.command()
@click.pass_obj
def list_effects(client):
    """List all available effects"""
    effects = client.get_effects()
    for effect in effects:
        click.echo(f"{effect.id}: {effect.attributes.name}")


@cli.command()
@click.argument("effect_name")
@click.pass_obj
def get_effect(client, effect_name):
    """Get details of a specific effect"""
    effect = client.get_effect_by_name(effect_name)
    click.echo(f"ID: {effect.id}")
    click.echo(f"Name: {effect.attributes.name}")
    click.echo(f"Description: {effect.attributes.description}")
    click.echo(f"Publisher: {effect.attributes.publisher}")


@cli.command()
@click.pass_obj
def current_effect(client):
    """Get the current effect"""

    effect = client.get_current_effect()
    click.echo(f"Current effect: {effect.attributes.name} (ID: {effect.id})")


@cli.command()
@click.argument("effect_name")
@click.pass_obj
def apply_effect(client, effect_name):
    """Apply an effect"""

    client.apply_effect_by_name(effect_name)
    click.echo(f"Applied effect: {effect_name}")


if __name__ == "__main__":
    cli()
