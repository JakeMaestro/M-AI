from app.main import _is_ws_connected, _last_event_ts
import time
from fastapi import APIRouter
import os, socket, time

router = APIRouter()

def _tcp_check(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

@router.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "service": "m-ai-orchestrator",
        "time": int(time.time()),
        "version": os.getenv("APP_VERSION", "unknown"),
    }

@router.get("/healthz/deps")
def healthz_deps():
    edge_host = os.getenv("EDGE_HOST", "edge")
    edge_port = int(os.getenv("EDGE_HTTP_PORT", "8088"))
    edge_ok = _tcp_check(edge_host, edge_port)
    ari_ok  = _ari_auth_ok()
    return {
        "status": "ok" if (edge_ok and ari_ok) else "degraded",
        "edge_http_reachable": edge_ok,
        "ari_auth": ari_ok,
    }


import os, base64, urllib.request

def _ari_auth_ok() -> bool:
    host = os.getenv("ARI_HOST", "edge")
    port = os.getenv("ARI_PORT", "8088")
    user = os.getenv("ARI_USER", "mai")
    pwd  = os.getenv("ARI_PASSWORD", "mvoice8908!#")  # Testpasswort wie gewünscht
    req = urllib.request.Request(f"http://{host}:{port}/ari/applications")
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")
    try:
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


@router.get("/readyz")
def readyz():
    edge_ok = _tcp_check(os.getenv("EDGE_HOST", "edge"), int(os.getenv("EDGE_HTTP_PORT", "8088")))
    try:
        ari_ok = _ari_auth_ok()
    except NameError:
        # Falls _ari_auth_ok aus irgendeinem Grund fehlt, als degraded werten
        ari_ok = False
    ws_ok = bool(_is_ws_connected) and ( (time.time() - _last_event_ts) < 60 if _last_event_ts else True )
    return {
        "status": "ok" if (edge_ok and ari_ok and ws_ok) else "degraded",
        "edge_http_reachable": edge_ok,
        "ari_auth": ari_ok,
        "ws_connected": ws_ok,
    }
