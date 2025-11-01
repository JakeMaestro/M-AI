from fastapi import APIRouter, HTTPException
from app.models.tenant import TenantConfig
from app.store.tenants import upsert_tenant, get_tenant, list_tenants, delete_tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.get("/")
def list_all():
    return list_tenants()

@router.get("/{tenant_id}")
def fetch(tenant_id: str):
    cfg = get_tenant(tenant_id)
    if not cfg:
        raise HTTPException(404, "tenant not found")
    return cfg

@router.post("/")
def upsert(cfg: TenantConfig):
    return upsert_tenant(cfg)

@router.delete("/{tenant_id}")
def remove(tenant_id: str):
    if not delete_tenant(tenant_id):
        raise HTTPException(404, "tenant not found")
    return {"ok": True}
