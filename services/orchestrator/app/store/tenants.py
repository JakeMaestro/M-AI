from typing import Dict, Optional
from app.models.tenant import TenantConfig, STTConfig, TTSConfig, LLMConfig

_TENANTS: Dict[str, TenantConfig] = {}

def upsert_tenant(cfg: TenantConfig) -> TenantConfig:
    _TENANTS[cfg.id] = cfg
    return cfg

def get_tenant(tid: str) -> Optional[TenantConfig]:
    return _TENANTS.get(tid)

def list_tenants():
    return list(_TENANTS.values())

def delete_tenant(tid: str) -> bool:
    return _TENANTS.pop(tid, None) is not None

# Default
if "demo" not in _TENANTS:
    upsert_tenant(TenantConfig(
        id="demo", name="Demo Tenant",
        stt=STTConfig(engine="dummy", lang="de-AT"),
        tts=TTSConfig(engine="dummy", voice="default"),
        llm=LLMConfig(engine="dummy", model="echo"),
        script_prompt="Du bist ein freundlicher Telefonassistent. Antworte kurz und präzise."
    ))
