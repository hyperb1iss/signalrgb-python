# pylint: disable=duplicate-code
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from signalrgb.cli import app
from signalrgb.exceptions import SignalRGBException
from signalrgb.model import Attributes, Effect, EffectPreset, Layout, Links


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

    result = runner.invoke(app, ["effect", "list"])
    assert result.exit_code == 0
    assert "Effect 1" in result.output
    assert "Effect 2" in result.output
    assert "effect1" in result.output
    assert "effect2" in result.output


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
    mock_client.return_value.get_current_effect.return_value = mock_effect

    result = runner.invoke(app, ["effect"])
    assert result.exit_code == 0
    assert "Test Effect" in result.output
    assert "Test Publisher" in result.output
    assert "Test Description" in result.output
    assert "Uses Audio " in result.output
    assert "Uses Video " in result.output
    assert "Uses Input " in result.output
    assert "Uses Meters " in result.output


def test_current_effect(runner, mock_client):
    mock_effect = Effect(
        id="effect1",
        type="lighting",
        attributes=Attributes(
            name="Current Effect",
            publisher="Test Publisher",
            description="Test Description",
            uses_audio=True,
            uses_video=False,
            uses_input=True,
            uses_meters=False,
        ),
        links=Links(),
    )

    # Configure the mock to return the actual Effect object
    mock_client.return_value.get_current_effect.return_value = mock_effect

    result = runner.invoke(app, ["effect"])
    assert result.exit_code == 0
    assert "Current Effect" in result.output
    assert "effect1" in result.output
    assert "Test Publisher" in result.output
    assert "Test Description" in result.output
    assert "Uses Audio " in result.output
    assert "Uses Video " in result.output
    assert "Uses Input " in result.output
    assert "Uses Meters " in result.output


def test_apply_effect(runner, mock_client):
    result = runner.invoke(app, ["effect", "apply", "Test Effect"])
    assert result.exit_code == 0
    assert "Applied effect: Test Effect" in result.output


def test_search_effects(runner, mock_client):
    mock_effects = [
        Effect(
            id="effect1",
            type="lighting",
            attributes=Attributes(name="Test Effect 1", description="Description 1"),
            links=Links(),
        ),
        Effect(
            id="effect2",
            type="lighting",
            attributes=Attributes(name="Test Effect 2", description="Description 2"),
            links=Links(),
        ),
        Effect(
            id="effect3",
            type="lighting",
            attributes=Attributes(name="Another Effect", description="Description 3"),
            links=Links(),
        ),
    ]
    mock_client.return_value.get_effects.return_value = mock_effects

    result = runner.invoke(app, ["effect", "search", "Test"])
    assert result.exit_code == 0
    assert "Test Effect 1" in result.output
    assert "Test Effect 2" in result.output
    assert "Another Effect" not in result.output
    assert "Description 1" in result.output
    assert "Description 2" in result.output


def test_brightness(runner, mock_client):
    mock_client.return_value.brightness = 50

    result = runner.invoke(app, ["canvas", "brightness", "50"])
    assert result.exit_code == 0
    assert "Set brightness to:" in result.output
    assert "50" in result.output

    result = runner.invoke(app, ["canvas", "brightness"])
    assert result.exit_code == 0
    assert "Current brightness:" in result.output
    assert "50" in result.output


def test_enable(runner, mock_client):
    mock_client.return_value.enabled = True

    result = runner.invoke(app, ["canvas", "enable"])
    assert result.exit_code == 0
    assert "enabled" in result.output


def test_disable(runner, mock_client):
    mock_client.return_value.enabled = False

    result = runner.invoke(app, ["canvas", "disable"])
    assert result.exit_code == 0
    assert "disabled" in result.output


def test_error_handling(runner, mock_client):
    mock_client.return_value.get_effects.side_effect = SignalRGBException("Test error")

    result = runner.invoke(app, ["effect", "list"])
    assert result.exit_code == 1
    assert "Error: Test error" in result.output


def test_main_callback(runner, mock_client):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SignalRGB CLI" in result.output


def test_next_effect(runner, mock_client):
    mock_effect = Effect(
        id="next_effect",
        type="lighting",
        attributes=Attributes(name="Next Effect"),
        links=Links(),
    )
    mock_client.return_value.apply_next_effect.return_value = mock_effect

    result = runner.invoke(app, ["effect", "next_effect"])
    assert result.exit_code == 0
    assert "Applied next effect: Next Effect" in result.output


def test_previous_effect(runner, mock_client):
    mock_effect = Effect(
        id="previous_effect",
        type="lighting",
        attributes=Attributes(name="Previous Effect"),
        links=Links(),
    )
    mock_client.return_value.apply_previous_effect.return_value = mock_effect

    result = runner.invoke(app, ["effect", "previous_effect"])
    assert result.exit_code == 0
    assert "Applied previous effect: Previous Effect" in result.output


def test_random_effect(runner, mock_client):
    mock_effect = Effect(
        id="random_effect",
        type="lighting",
        attributes=Attributes(name="Random Effect"),
        links=Links(),
    )
    mock_client.return_value.apply_random_effect.return_value = mock_effect

    result = runner.invoke(app, ["effect", "random"])
    assert result.exit_code == 0
    assert "Applied random effect: Random Effect" in result.output


def test_refresh_effects(runner, mock_client):
    result = runner.invoke(app, ["effect", "refresh"])
    assert result.exit_code == 0
    assert "Effects cache refreshed" in result.output


def test_list_presets(runner, mock_client):
    mock_presets = [
        EffectPreset(id="preset1", type="preset"),
        EffectPreset(id="preset2", type="preset"),
    ]
    mock_client.return_value.get_current_effect.return_value = Effect(
        id="current_effect",
        type="lighting",
        attributes=Attributes(name="Current Effect"),
        links=Links(),
    )
    mock_client.return_value.get_effect_presets.return_value = mock_presets

    result = runner.invoke(app, ["preset", "list"])
    assert result.exit_code == 0
    assert "preset1" in result.output
    assert "preset2" in result.output


def test_apply_preset(runner, mock_client):
    mock_client.return_value.get_current_effect.return_value = Effect(
        id="current_effect",
        type="lighting",
        attributes=Attributes(name="Current Effect"),
        links=Links(),
    )

    result = runner.invoke(app, ["preset", "apply", "preset1"])
    assert result.exit_code == 0
    assert "Applied preset" in result.output
    assert "preset1" in result.output
    assert "Current Effect" in result.output


def test_list_layouts(runner, mock_client):
    mock_layouts = [
        Layout(id="layout1", type="layout"),
        Layout(id="layout2", type="layout"),
    ]
    mock_client.return_value.get_layouts.return_value = mock_layouts

    result = runner.invoke(app, ["layout", "list"])
    assert result.exit_code == 0
    assert "layout1" in result.output
    assert "layout2" in result.output
    assert "layout" in result.output


def test_set_layout(runner, mock_client):
    result = runner.invoke(app, ["layout", "set_layout", "layout1"])
    assert result.exit_code == 0
    assert "Set current layout to: layout1" in result.output


def test_canvas_info(runner, mock_client):
    mock_client.return_value.enabled = True
    mock_client.return_value.brightness = 75

    result = runner.invoke(app, ["canvas"])
    assert result.exit_code == 0
    assert "Canvas State" in result.output
    assert "Enabled" in result.output
    assert "Brightness" in result.output
    assert "75%" in result.output


def test_toggle_canvas(runner, mock_client):
    mock_client.return_value.enabled = False

    result = runner.invoke(app, ["canvas", "toggle"])
    assert result.exit_code == 0
    assert " enabled" in result.output

    mock_client.return_value.enabled = True

    result = runner.invoke(app, ["canvas", "toggle"])
    assert result.exit_code == 0
    assert " disabled" in result.output
