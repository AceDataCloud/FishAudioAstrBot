"""Small, single-call Fish Audio transport for AstrBot."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


API_BASE = "https://api.acedata.cloud"
MODELS = {"s1", "s2-pro", "s2.1-pro"}
MAX_TEXT_BYTES = 4096


class _NoRedirect(HTTPRedirectHandler):
    """Do not forward the configured key to a redirected destination."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        """Reject the redirect and let urllib raise an HTTP error."""
        return None


OPENER = build_opener(_NoRedirect)


class FishError(RuntimeError):
    """An error safe to show in an AstrBot conversation."""


class FishClient:
    """Generate one MP3 or find public reference voices."""

    def __init__(self, api_key: str) -> None:
        token = api_key.strip()
        if (
            not token
            or token.lower().startswith("bearer ")
            or token.startswith("platform-")
        ):
            raise FishError(
                "Set an Ace Data Cloud generation API key in plugin settings."
            )
        self._api_key = token

    def _request(
        self, path: str, *, payload: dict[str, Any] | None = None, model: str = ""
    ) -> tuple[dict[str, Any], str]:
        headers = {
            "Authorization": "Bearer " + self._api_key,
            "Accept": "application/json",
            "User-Agent": "AceDataCloudAstrBot/0.1.0",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if model:
            headers["model"] = model
        request = Request(
            API_BASE + path,
            data=json.dumps(payload).encode("utf-8") if payload is not None else None,
            headers=headers,
            method="POST" if payload is not None else "GET",
        )
        try:
            with OPENER.open(request, timeout=90) as response:
                body = json.load(response)
                trace_id = response.headers.get(
                    "x-trace-id", ""
                ) or response.headers.get("x-request-id", "")
        except HTTPError as exc:
            raise FishError(
                f"Ace Data Cloud returned HTTP {exc.code}. Check key access and request history."
            ) from None
        except (URLError, TimeoutError, OSError):
            raise FishError(
                "The API connection failed. Check request history before retrying speech generation."
            ) from None
        except (ValueError, UnicodeError):
            raise FishError(
                "The API returned invalid JSON. Check request history."
            ) from None
        if (
            not isinstance(body, dict)
            or body.get("success") is False
            or body.get("error")
        ):
            raise FishError("The Fish Audio request failed. Check request history.")
        return body, str(body.get("trace_id") or trace_id)

    async def synthesize(
        self, text: str, reference_id: str = "", model: str = "s2-pro"
    ) -> dict[str, Any]:
        """Submit one synchronous TTS request, without automatic paid retries."""
        text = text.strip()
        if not text or len(text.encode("utf-8")) > MAX_TEXT_BYTES:
            raise FishError(
                "Provide 1–4096 UTF-8 bytes of text for one speech request."
            )
        if model not in MODELS:
            raise FishError("Choose s1, s2-pro, or s2.1-pro.")
        if len(reference_id) > 128:
            raise FishError("The reference voice ID is too long.")
        payload = {"text": text, "format": "mp3"}
        if reference_id:
            payload["reference_id"] = reference_id
        body, trace_id = await asyncio.to_thread(
            self._request, "/fish/tts", payload=payload, model=model
        )
        audio_url = body.get("audio_url")
        parsed = urlsplit(audio_url) if isinstance(audio_url, str) else None
        if not parsed or parsed.scheme != "https" or not parsed.netloc:
            raise FishError(
                "No finished audio URL was returned. Check request history before generating again."
            )
        return {
            "status": "succeeded",
            "success": True,
            "audio_url": audio_url,
            "trace_id": trace_id,
            "model": model,
        }

    async def search_voices(
        self, title: str, language: str = "", limit: int = 5
    ) -> dict[str, Any]:
        """Find public voices without exposing raw provider records to the model."""
        title = title.strip()
        language = language.strip().lower()
        if not title or len(title) > 100:
            raise FishError("Provide a voice title search of 1–100 characters.")
        if len(language) > 12:
            raise FishError("The language filter is too long.")
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or not 1 <= limit <= 10
        ):
            raise FishError("Limit must be an integer from 1 to 10.")
        params = {"title": title, "page_size": limit, "page_number": 1}
        if language:
            params["language"] = language
        body, trace_id = await asyncio.to_thread(
            self._request, "/fish/model?" + urlencode(params)
        )
        items = body.get("items")
        if not isinstance(items, list):
            raise FishError("The voice catalog returned an unexpected format.")
        voices = [
            {
                "reference_id": item.get("_id", ""),
                "title": item.get("title", ""),
                "languages": item.get("languages", []),
                "state": item.get("state", ""),
                "tags": item.get("tags", [])[:5],
            }
            for item in items[:limit]
            if isinstance(item, dict) and isinstance(item.get("_id"), str)
        ]
        return {
            "status": "succeeded",
            "success": True,
            "trace_id": trace_id,
            "voices": voices,
        }
