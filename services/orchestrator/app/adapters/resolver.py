from typing import Tuple
from app.adapters.base import STTAdapter, TTSAdapter, LLMAdapter
from app.adapters.dummy_impl import DummySTT, DummyTTS, DummyLLM
from app.models.tenant import TenantConfig

# Platzhalter: hier später echte Implementierungen importieren (Azure/OpenAI/…)
# from app.adapters.azure.stt import AzureSTT
# from app.adapters.azure.tts import AzureTTS
# from app.adapters.openai.llm import OpenAILLM
# usw.

def build_adapters(cfg: TenantConfig) -> Tuple[STTAdapter, TTSAdapter, LLMAdapter]:
    # STT
    if cfg.stt.engine == "dummy":
        stt = DummySTT()
    else:
        # TODO: echte Engines anhand cfg.stt.engine auswählen
        stt = DummySTT()

    # TTS
    if cfg.tts.engine == "dummy":
        tts = DummyTTS()
    else:
        tts = DummyTTS()

    # LLM
    if cfg.llm.engine == "dummy":
        llm = DummyLLM()
    else:
        llm = DummyLLM()

    return stt, tts, llm
