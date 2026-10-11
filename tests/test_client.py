"""The billable request and voice-catalog boundaries."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from client import FishClient, FishError


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers = {"x-trace-id": "trace-fish"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


@pytest.mark.asyncio
async def test_tts_sends_model_header_and_one_billable_request():
    requests = []

    def fake_open(request, timeout):
        requests.append((request, timeout))
        return FakeResponse({"audio_url": "https://cdn.example.org/voice.mp3"})

    with patch("client.OPENER.open", side_effect=fake_open):
        result = await FishClient("test-key").synthesize(
            "Hello AstrBot", "public-voice", "s2.1-pro"
        )
    assert len(requests) == 1
    request, timeout = requests[0]
    assert request.full_url == "https://api.acedata.cloud/fish/tts"
    assert request.get_method() == "POST"
    assert request.get_header("Model") == "s2.1-pro"
    assert json.loads(request.data) == {
        "text": "Hello AstrBot",
        "format": "mp3",
        "reference_id": "public-voice",
    }
    assert timeout == 90
    assert result["audio_url"] == "https://cdn.example.org/voice.mp3"
    assert result["trace_id"] == "trace-fish"


@pytest.mark.asyncio
async def test_missing_audio_url_does_not_retry_generation():
    with (
        patch("client.OPENER.open", return_value=FakeResponse({})) as opening,
        pytest.raises(FishError, match="No finished audio URL"),
    ):
        await FishClient("test-key").synthesize("Hello")
    assert opening.call_count == 1


@pytest.mark.asyncio
async def test_voice_search_returns_only_public_fields():
    payload = {
        "items": [
            {
                "_id": "voice-1",
                "title": "Narrator",
                "languages": ["en"],
                "state": "trained",
                "tags": ["narration"],
                "author": {"nickname": "Private author"},
                "supplier": "internal-only",
            }
        ]
    }
    with patch("client.OPENER.open", return_value=FakeResponse(payload)) as opening:
        result = await FishClient("test-key").search_voices("Narrator", "en")
    request = opening.call_args.args[0]
    assert request.get_method() == "GET"
    assert "title=Narrator" in request.full_url
    assert "language=en" in request.full_url
    assert result["voices"] == [
        {
            "reference_id": "voice-1",
            "title": "Narrator",
            "languages": ["en"],
            "state": "trained",
            "tags": ["narration"],
        }
    ]


@pytest.mark.asyncio
async def test_invalid_input_never_reaches_api():
    with patch("client.OPENER.open") as opening:
        with pytest.raises(FishError):
            await FishClient("test-key").synthesize(" ")
        with pytest.raises(FishError):
            await FishClient("test-key").synthesize("Hi", model="unknown")
        with pytest.raises(FishError):
            await FishClient("test-key").search_voices("")
    assert opening.call_count == 0
