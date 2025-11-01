from fastapi import APIRouter, Header, HTTPException
from app.store.tenants import get_tenant
from app.adapters.resolver import build_adapters

router = APIRouter(prefix="/flow", tags=["flow"])

@router.get("/hello")
async def hello_flow(x_tenant_id: str = Header(default="demo")):
    cfg = get_tenant(x_tenant_id)
    if not cfg:
        raise HTTPException(404, "tenant not found")
    stt, tts, llm = build_adapters(cfg)
    res = await llm.run([{"role":"user","content":"Sag Hallo!"}])
    # TTS Stream würde Audio-Bytes liefern – hier nur count als Beispiel
    audio_chunks = 0
    async for _ in tts.synth_stream(res["text"], cfg.tts.voice):
        audio_chunks += 1
    return {"tenant": cfg.id, "llm_text": res["text"], "audio_chunks": audio_chunks}
