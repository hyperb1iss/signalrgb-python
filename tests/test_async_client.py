"""Tests for the AsyncSignalRGBClient class."""

from unittest.mock import Mock, patch

import httpx
from httpx import Response
import pytest

from signalrgb.async_client import AsyncSignalRGBClient
from signalrgb.exceptions import (
    APIError,
    ConnectionError,
)
from signalrgb.model import (
    Attributes,
    CurrentState,
    CurrentStateHolder,
    CurrentStateResponse,
    Effect,
    EffectDetailsResponse,
    EffectList,
    EffectListResponse,
    Links,
    SignalRGBResponse,
)


@pytest.fixture
async def async_client():
    """Create an AsyncSignalRGBClient instance for testing."""
    client = AsyncSignalRGBClient("testhost", 12345)
    yield client
    await client._client.aclose()


@pytest.mark.asyncio
async def test_get_effects(async_client):
    """Test getting a list of effects asynchronously."""
    effects = [
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
    response_data = EffectListResponse(
        api_version="1.0",
        id=123,
        method="GET",
        status="ok",
        data=EffectList(items=effects),
    ).to_dict()

    with patch.object(async_client._client, "request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = await async_client.get_effects()

        mock_request.assert_called_once_with("GET", "http://testhost:12345/api/v1/lighting/effects")
        assert len(result) == 2
        assert result[0].id == "effect1"
        assert result[1].id == "effect2"
        assert result[0].attributes.name == "Effect 1"
        assert result[1].attributes.name == "Effect 2"


@pytest.mark.asyncio
async def test_get_effect(async_client):
    """Test getting a specific effect asynchronously."""
    effect = Effect(
        id="effect1",
        type="lighting",
        attributes=Attributes(name="Effect 1"),
        links=Links(),
    )
    response_data = EffectDetailsResponse(
        api_version="1.0",
        id=123,
        method="GET",
        status="ok",
        data=effect,
    ).to_dict()

    with patch.object(async_client._client, "request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = await async_client.get_effect("effect1")

        mock_request.assert_called_once_with("GET", "http://testhost:12345/api/v1/lighting/effects/effect1")
        assert result.id == "effect1"
        assert result.attributes.name == "Effect 1"


@pytest.mark.asyncio
async def test_apply_effect(async_client):
    """Test applying an effect asynchronously."""
    response_data = SignalRGBResponse(
        api_version="1.0",
        id=123,
        method="POST",
        status="ok",
    ).to_dict()

    with patch.object(async_client._client, "request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        await async_client.apply_effect("effect1")

        mock_request.assert_called_once_with("POST", "http://testhost:12345/api/v1/lighting/effects/effect1/apply")


@pytest.mark.asyncio
async def test_get_brightness(async_client):
    """Test getting the brightness asynchronously."""
    state = CurrentStateHolder(
        attributes=CurrentState(name="Effect 1", enabled=True, global_brightness=75),
        id="effect1",
        links=Links(),
        type="lighting",
    )
    response_data = CurrentStateResponse(
        api_version="1.0",
        id=123,
        method="GET",
        status="ok",
        data=state,
    ).to_dict()

    with patch.object(async_client._client, "request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = await async_client.get_brightness()

        mock_request.assert_called_once_with("GET", "http://testhost:12345/api/v1/lighting")
        assert result == 75


@pytest.mark.asyncio
async def test_set_brightness(async_client):
    """Test setting the brightness asynchronously."""
    response_data = SignalRGBResponse(
        api_version="1.0",
        id=123,
        method="PATCH",
        status="ok",
    ).to_dict()

    with patch.object(async_client._client, "request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        await async_client.set_brightness(50)

        mock_request.assert_called_once_with(
            "PATCH",
            "http://testhost:12345/api/v1/lighting/global_brightness",
            json={"global_brightness": 50},
        )


@pytest.mark.asyncio
async def test_connect_error_handling(async_client):
    """Test handling of connection errors."""
    with patch.object(async_client._client, "request") as mock_request:
        mock_request.side_effect = httpx.ConnectError("Connection error")

        with pytest.raises(ConnectionError) as exc_info:
            await async_client.get_effects()

        assert "Connection error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_timeout_error_handling(async_client):
    """Test handling of timeout errors."""
    with patch.object(async_client._client, "request") as mock_request:
        mock_request.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(ConnectionError) as exc_info:
            await async_client.get_effects()

        assert "Request Timeout" in str(exc_info.value.title)


@pytest.mark.asyncio
async def test_http_error_handling(async_client):
    """Test handling of HTTP errors."""
    error_response = {"errors": [{"code": "404", "title": "Not Found", "detail": "Effect not found"}]}

    with patch.object(async_client._client, "request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = error_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "HTTP Error", request=Mock(), response=mock_response
        )
        mock_request.side_effect = httpx.HTTPStatusError("HTTP Error", request=Mock(), response=mock_response)

        with pytest.raises(APIError) as exc_info:
            await async_client.get_effects()

        assert "HTTP error" in str(exc_info.value)
        assert exc_info.value.error.code == "404"
        assert exc_info.value.error.title == "Not Found"
