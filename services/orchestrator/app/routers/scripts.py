from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.store.tenants import get_tenant, upsert_tenant

router = APIRouter(prefix="/scripts", tags=["scripts"])

class ScriptBody(BaseModel):
    tenant_id: str
    prompt: str

@router.get("/{tenant_id}")
def get_script(tenant_id: str):
    t = get_tenant(tenant_id)
    if not t:
        raise HTTPException(404, "tenant not found")
    return {"tenant_id": t.id, "prompt": t.script_prompt}

@router.post("/")
def set_script(body: ScriptBody):
    t = get_tenant(body.tenant_id)
    if not t:
        raise HTTPException(404, "tenant not found")
    t.script_prompt = body.prompt
    upsert_tenant(t)
    return {"ok": True}
