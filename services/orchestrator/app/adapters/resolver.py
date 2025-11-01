from typing import Tuple
from app.adapters.base import STTAdapter, TTSAdapter, LLMAdapter
from app.adapters.dummy_impl import DummySTT, DummyTTS, DummyLLM
from app.models.tenant import TenantConfig

# ElevenLabs TTS
from app.adapters.elevenlabs_tts import ElevenLabsTTS

# Platzhalter: hier später echte Engines importieren (Azure/OpenAI/Deepgram)
# from app.adapters.azure.stt import AzureSTT
# from app.adapters.openai.tts import OpenAITTS
# from app.adapters.deepgram.stt import DeepgramSTT
# from app.adapters.openai.llm import OpenAILLM

def build_adapters(cfg: TenantConfig) -> Tuple[STTAdapter, TTSAdapter, LLMAdapter]:
    # STT
    if cfg.stt.engine == "dummy":
        stt = DummySTT()
    else:
        # TODO: weitere STT Engines
        stt = DummySTT()

    # TTS
    if cfg.tts.engine == "elevenlabs":
        tts = ElevenLabsTTS()
    elif cfg.tts.engine == "dummy":
        tts = DummyTTS()
    else:
        # TODO: weitere TTS Engines
        tts = DummyTTS()

    # LLM
    if cfg.llm.engine == "dummy":
        llm = DummyLLM()
    else:
        # TODO: weitere LLM Engines
        llm = DummyLLM()

    return stt, tts, llm
