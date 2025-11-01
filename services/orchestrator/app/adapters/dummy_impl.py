import asyncio
from .base import STTAdapter, TTSAdapter, LLMAdapter
from typing import AsyncIterator, Dict, Any, Optional, List

class DummySTT(STTAdapter):
    async def start_stream(self, lang: str, **opts) -> AsyncIterator[str]:
        for part in ["hallo", "ich", "bin", "da"]:
            await asyncio.sleep(0.05)
            yield part
    async def stop(self) -> None:
        return

class DummyTTS(TTSAdapter):
    async def synth_stream(self, text: str, voice: str, **opts) -> AsyncIterator[bytes]:
        # erzeugt nur Dummy-Frames
        for _ in range(5):
            await asyncio.sleep(0.02)
            yield b"\x00\x01" * 160

class DummyLLM(LLMAdapter):
    async def run(self, messages: List[Dict[str, Any]], tools: Optional[list] = None, **opts) -> Dict[str, Any]:
        last = messages[-1]["content"] if messages else ""
        return {"text": f"Echo: {last}", "tool_calls": []}
