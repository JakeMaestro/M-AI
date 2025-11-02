from fastapi import APIRouter

router = APIRouter(prefix="/tts", tags=["tts"])

@router.get("/health")
def tts_health():
    return {"status": "ok", "engine": "stub"}
