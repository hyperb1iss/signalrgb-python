import pytest
from aiohttp import ClientResponseError, ClientConnectorError
from asyncio import TimeoutError

from signalrgb.client import (
    SignalRGBClient,
    APIError,
    ConnectionError,
    EffectNotFoundError,
)
from signalrgb.model import Effect, Attributes, Links, Error


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
async def test_get_effects_error(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.side_effect = APIError("API Error")

    with pytest.raises(APIError):
        await client.get_effects()


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
async def test_get_effect_not_found(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.side_effect = APIError(
        "Not found", Error(title="Not Found", code="not_found")
    )

    with pytest.raises(EffectNotFoundError):
        await client.get_effect("nonexistent")


@pytest.mark.asyncio
async def test_get_effect_by_name(client, mocker):
    mock_get_effects = mocker.patch.object(SignalRGBClient, "get_effects")
    mock_get_effects.return_value = [
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
    ]
    mock_get_effect = mocker.patch.object(SignalRGBClient, "get_effect")
    mock_get_effect.return_value = Effect(
        id="effect1",
        type="lighting",
        attributes=Attributes(name="Test Effect 1"),
        links=Links(),
    )

    effect = await client.get_effect_by_name("Test Effect 1")

    assert effect.id == "effect1"
    assert effect.attributes.name == "Test Effect 1"
    mock_get_effects.assert_called_once()
    mock_get_effect.assert_called_once_with("effect1")


@pytest.mark.asyncio
async def test_get_effect_by_name_not_found(client, mocker):
    mock_get_effects = mocker.patch.object(SignalRGBClient, "get_effects")
    mock_get_effects.return_value = [
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
    ]

    with pytest.raises(EffectNotFoundError):
        await client.get_effect_by_name("Nonexistent Effect")


@pytest.mark.asyncio
async def test_get_current_effect(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.side_effect = [
        {
            "api_version": "1.0",
            "id": 1,
            "method": "GET",
            "status": "ok",
            "data": {
                "id": "effect1",
                "type": "lighting",
                "attributes": {"name": "Current Effect"},
                "links": {},
            },
        },
        {
            "api_version": "1.0",
            "id": 2,
            "method": "GET",
            "status": "ok",
            "data": {
                "id": "effect1",
                "type": "lighting",
                "attributes": {"name": "Current Effect"},
                "links": {},
            },
        },
    ]

    effect = await client.get_current_effect()

    assert effect.id == "effect1"
    assert effect.attributes.name == "Current Effect"
    assert mock_request.call_count == 2
    mock_request.assert_any_call("GET", "/api/v1/lighting")
    mock_request.assert_any_call("GET", "/api/v1/lighting/effects/effect1")


@pytest.mark.asyncio
async def test_apply_effect(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.return_value = {
        "api_version": "1.0",
        "id": 1,
        "method": "POST",
        "status": "ok",
    }

    await client.apply_effect("effect1")

    mock_request.assert_called_once_with("POST", "/api/v1/effects/effect1/apply")


@pytest.mark.asyncio
async def test_apply_effect_not_found(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.side_effect = APIError(
        "Not found", Error(title="Not Found", code="not_found")
    )

    with pytest.raises(EffectNotFoundError):
        await client.apply_effect("nonexistent")


@pytest.mark.asyncio
async def test_apply_effect_by_name(client, mocker):
    mock_get_effect_by_name = mocker.patch.object(SignalRGBClient, "get_effect_by_name")
    mock_get_effect_by_name.return_value = Effect(
        id="effect1",
        type="lighting",
        attributes=Attributes(name="Test Effect 1"),
        links=Links(apply="/api/v1/effects/effect1/apply"),
    )
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.return_value = {
        "api_version": "1.0",
        "id": 1,
        "method": "POST",
        "status": "ok",
    }

    await client.apply_effect_by_name("Test Effect 1")

    mock_get_effect_by_name.assert_called_once_with("Test Effect 1")
    mock_request.assert_called_once_with("POST", "/api/v1/effects/effect1/apply")


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


@pytest.mark.asyncio
async def test_connection_error(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.side_effect = ClientConnectorError(
        connection_key=mocker.Mock(ssl=None), os_error=OSError("Connection failed")
    )

    with pytest.raises(ConnectionError):
        await client.get_effects()


@pytest.mark.asyncio
async def test_timeout_error(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.side_effect = TimeoutError()

    with pytest.raises(ConnectionError):
        await client.get_effects()


@pytest.mark.asyncio
async def test_client_response_error(client, mocker):
    mock_request = mocker.patch.object(SignalRGBClient, "_request")
    mock_request.side_effect = ClientResponseError(
        request_info=mocker.Mock(real_url="http://test.com"),
        history=(),
        status=500,
        message="Internal Server Error",
    )

    with pytest.raises(APIError):
        await client.get_effects()
