from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

EngineName = Literal["azure", "openai", "elevenlabs", "deepgram", "dummy"]

class STTConfig(BaseModel):
    engine: EngineName = "dummy"
    lang: str = "de-AT"
    params: Dict[str, Any] = Field(default_factory=dict)

class TTSConfig(BaseModel):
    engine: EngineName = "dummy"
    voice: str = "default"  # für ElevenLabs: Voice-ID
    params: Dict[str, Any] = Field(default_factory=dict)

class LLMConfig(BaseModel):
    engine: EngineName = "dummy"
    model: str = "gpt-4o-mini"
    params: Dict[str, Any] = Field(default_factory=dict)

class TenantConfig(BaseModel):
    id: str
    name: str
    stt: STTConfig = STTConfig()
    tts: TTSConfig = TTSConfig()
    llm: LLMConfig = LLMConfig()
    script_prompt: Optional[str] = None
