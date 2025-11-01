import os
from typing import AsyncIterator, Dict, Any
import httpx

from .base import TTSAdapter

# ElevenLabs REST Streaming (Text-to-Speech v1)
# Wir fordern "ulaw_8000" an -> perfekt für Telephony (8k, µ-law)
# Docs: POST /v1/text-to-speech/{voice_id}
# Header: xi-api-key, Accept: audio/...
# Body: { text, model_id, voice_settings, ... }

_DEFAULT_MODEL = "eleven_multilingual_v2"

class ElevenLabsTTS(TTSAdapter):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY missing in environment")

    async def synth_stream(
        self,
        text: str,
        voice: str,
        **opts
    ) -> AsyncIterator[bytes]:
        """
        Streamt µ-law 8k Audio-Bytes (telephony-ready) in Chunks.
        voice: kann Voice-ID oder Name sein (wir nehmen ID).
        opts:
          - model_id: str (default: eleven_multilingual_v2)
          - stability, similarity_boost, style, use_speaker_boost (voice_settings)
          - latency (ignored; REST-Streaming nutzt Transfer-Encoding: chunked)
        """
        model_id: str = opts.get("model_id", _DEFAULT_MODEL)
        voice_settings: Dict[str, Any] = opts.get("voice_settings", {})

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        headers = {
            "xi-api-key": self.api_key,
            "Accept": "audio/ulaw;rate=8000"
        }
        payload: Dict[str, Any] = {
            "text": text,
            "model_id": model_id,
        }
        if voice_settings:
            payload["voice_settings"] = voice_settings

        # Stream via httpx (async)
        timeout = httpx.Timeout(30.0, read=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes():
                    if chunk:
                        yield chunk
