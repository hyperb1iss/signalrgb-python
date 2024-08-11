import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from signalrgb.cli import app
from signalrgb.client import SignalRGBException
from signalrgb.model import Effect, Attributes, Links


@pytest.fixture
def mock_client():
    with patch("signalrgb.cli.SignalRGBClient") as mock:
        yield mock


@pytest.fixture
def runner():
    return CliRunner()


def test_list_effects(runner, mock_client):
    mock_effects = [
        Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Effect 1"),
            links=Links(),
        ),
        Effect(
            id="effect2",
            type="lighting",
            attributes=Attributes(name="Effect 2"),
            links=Links(),
        ),
    ]
    mock_client.return_value.get_effects.return_value = mock_effects

    result = runner.invoke(app, ["list-effects"])
    assert result.exit_code == 0
    assert "Effect 1" in result.output
    assert "Effect 2" in result.output
    assert "Total effects: 2" in result.output


def test_get_effect(runner, mock_client):
    mock_effect = Effect(
        id="effect1",
        type="lighting",
        attributes=Attributes(
            name="Test Effect",
            publisher="Test Publisher",
            description="Test Description",
            uses_audio=True,
            uses_video=False,
            uses_input=True,
            uses_meters=False,
            parameters={"param1": "value1"},
        ),
        links=Links(apply="/api/v1/effects/effect1/apply"),
    )
    mock_client.return_value.get_effect_by_name.return_value = mock_effect

    result = runner.invoke(app, ["get-effect", "Test Effect"])
    assert result.exit_code == 0
    assert "Test Effect" in result.output
    assert "Test Publisher" in result.output
    assert "Test Description" in result.output
    assert "param1" in result.output
    assert "value1" in result.output


def test_current_effect(runner, mock_client):
    mock_effect = Effect(
        id="effect1",
        type="lighting",
        attributes=Attributes(name="Current Effect", publisher="Test Publisher"),
        links=Links(),
    )
    mock_client.return_value.get_current_effect.return_value = mock_effect

    result = runner.invoke(app, ["current-effect"])
    assert result.exit_code == 0
    assert "Current Effect" in result.output
    assert "Test Publisher" in result.output


def test_apply_effect(runner, mock_client):
    result = runner.invoke(app, ["apply-effect", "Test Effect"])
    assert result.exit_code == 0
    assert "Successfully applied effect: Test Effect" in result.output


def test_search_effects(runner, mock_client):
    mock_effects = [
        Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1"),
            links=Links(),
        ),
        Effect(
            id="effect2",
            type="lighting",
            attributes=Attributes(name="Test Effect 2"),
            links=Links(),
        ),
        Effect(
            id="effect3",
            type="lighting",
            attributes=Attributes(name="Another Effect"),
            links=Links(),
        ),
    ]
    mock_client.return_value.get_effects.return_value = mock_effects

    result = runner.invoke(app, ["search-effects", "Test"])
    assert result.exit_code == 0
    assert "Test Effect 1" in result.output
    assert "Test Effect 2" in result.output
    assert "Another Effect" not in result.output
    assert "Found 2 matching effects" in result.output


def test_brightness(runner, mock_client):
    mock_client.return_value.brightness = 50

    result = runner.invoke(app, ["brightness", "50"])
    assert result.exit_code == 0
    assert "Brightness set to: 50" in result.output

    result = runner.invoke(app, ["brightness"])
    assert result.exit_code == 0
    assert "Current brightness: 50" in result.output


def test_enable(runner, mock_client):
    mock_client.return_value.enabled = True

    result = runner.invoke(app, ["enable"])
    assert result.exit_code == 0
    assert "Canvas enabled successfully" in result.output


def test_disable(runner, mock_client):
    mock_client.return_value.enabled = False

    result = runner.invoke(app, ["disable"])
    assert result.exit_code == 0
    assert "Canvas disabled successfully" in result.output


def test_error_handling(runner, mock_client):
    mock_client.return_value.get_effects.side_effect = SignalRGBException("Test error")

    result = runner.invoke(app, ["list-effects"])
    assert result.exit_code == 1
    assert "Error: Test error" in result.output


def test_version(runner):
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "SignalRGB CLI version:" in result.output


# Add more tests as needed
