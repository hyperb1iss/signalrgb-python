import pytest

from signalrgb.client import (
    SignalRGBClient,
)


@pytest.fixture
async def client():
    client = SignalRGBClient("testhost", 12345)
    yield client
    await client.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_get_effects(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.return_value = {
        "api_version": "1.0",
        "id": 1,
        "method": "GET",
        "status": "ok",
        "data": {
            "items": [
                {
                    "id": "effect1",
                    "type": "lighting",
                    "attributes": {"name": "Test Effect 1"},
                    "links": {},
                },
                {
                    "id": "effect2",
                    "type": "lighting",
                    "attributes": {"name": "Test Effect 2"},
                    "links": {},
                },
            ]
        },
    }

    effects = await client.get_effects()

    assert len(effects) == 2
    assert effects[0].id == "effect1"
    assert effects[1].id == "effect2"
    mock_request.assert_called_once_with("GET", "/api/v1/lighting/effects")


@pytest.mark.asyncio
async def test_get_effect(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.return_value = {
        "api_version": "1.0",
        "id": 1,
        "method": "GET",
        "status": "ok",
        "data": {
            "id": "effect1",
            "type": "lighting",
            "attributes": {"name": "Test Effect 1"},
            "links": {},
        },
    }

    effect = await client.get_effect("effect1")

    assert effect.id == "effect1"
    assert effect.attributes.name == "Test Effect 1"
    mock_request.assert_called_once_with("GET", "/api/v1/lighting/effects/effect1")


@pytest.mark.asyncio
async def test_refresh_effects(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.side_effect = [
        {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "items": [
                    {
                        "id": "effect1",
                        "type": "lighting",
                        "attributes": {"name": "Effect 1"},
                        "links": {},
                    },
                    {
                        "id": "effect2",
                        "type": "lighting",
                        "attributes": {"name": "Effect 2"},
                        "links": {},
                    },
                ]
            },
        },
        {
            "api_version": "1.0",
            "id": 2,
            "method": "GET",
            "status": "ok",
            "data": {
                "items": [
                    {
                        "id": "effect3",
                        "type": "lighting",
                        "attributes": {"name": "Effect 3"},
                        "links": {},
                    },
                    {
                        "id": "effect4",
                        "type": "lighting",
                        "attributes": {"name": "Effect 4"},
                        "links": {},
                    },
                ]
            },
        },
    ]

    # First call to get_effects
    effects1 = await client.get_effects()
    assert len(effects1) == 2
    assert effects1[0].id == "effect1"
    assert effects1[1].id == "effect2"

    # Second call to get_effects (should use cached result)
    effects2 = await client.get_effects()
    assert effects1 == effects2

    # Verify that _request was only called once
    assert mock_request.call_count == 1

    # Refresh effects
    client.refresh_effects()

    # Call get_effects again (should fetch new data)
    effects3 = await client.get_effects()
    assert len(effects3) == 2
    assert effects3[0].id == "effect3"
    assert effects3[1].id == "effect4"

    # Verify that _request was called twice in total
    assert mock_request.call_count == 2
