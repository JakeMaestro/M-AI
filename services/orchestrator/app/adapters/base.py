from typing import AsyncIterator, Protocol, Dict, Any, Optional

class STTAdapter(Protocol):
    async def start_stream(self, lang: str, **opts) -> AsyncIterator[str]:
        """Yield fortlaufend erkannte Textfragmente (partial/final)."""

    async def stop(self) -> None: ...

class TTSAdapter(Protocol):
    async def synth_stream(self, text: str, voice: str, **opts) -> AsyncIterator[bytes]:
        """Yield Audio-Chunks (z. B. PCM16/µ-law) für Streaming TTS."""

class LLMAdapter(Protocol):
    async def run(self, messages: list[Dict[str, Any]], tools: Optional[list[Dict]] = None, **opts) -> Dict[str, Any]:
        """Gibt strukturiertes Resultat (text + optional function_calls) zurück."""
