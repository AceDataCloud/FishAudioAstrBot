"""Fish Audio speech and voice discovery tools for AstrBot."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import FishClient, FishError


class FishAudioPlugin(Star):
    """Expose one TTS call and public voice search to chat agents."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="fish_generate_speech")
    async def fish_generate_speech(
        self,
        event: AstrMessageEvent,
        text: str,
        reference_id: str = "",
        model: str = "s2-pro",
    ) -> str:
        """Generate one short MP3 from text. This call can incur a charge.

        Args:
            text(string): Words to speak, up to 4096 UTF-8 bytes.
            reference_id(string): Optional public or owned Fish voice ID.
            model(string): s1, s2-pro, or s2.1-pro.

        Returns:
            JSON with a finished MP3 URL and trace ID when available.
        """
        try:
            result = await FishClient(self.config.get("api_key", "")).synthesize(
                text, reference_id, model
            )
        except FishError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="fish_search_voices")
    async def fish_search_voices(
        self, event: AstrMessageEvent, title: str, language: str = "", limit: int = 5
    ) -> str:
        """Find public Fish voices for a later speech request.

        Args:
            title(string): Text to match in a public voice title.
            language(string): Optional language code such as zh or en.
            limit(number): Number of voices to return, 1 to 10.

        Returns:
            JSON with voice IDs, titles, languages, states, and tags.
        """
        try:
            result = await FishClient(self.config.get("api_key", "")).search_voices(
                title, language, limit
            )
        except FishError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)
