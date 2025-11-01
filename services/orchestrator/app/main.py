from app.routers import tts
from app.routers import flow
from app.routers import tenants
from app.routers import scripts
from app.ari.url import build_ari_ws_url, build_ari_basic_header
from app.state import ws
from app.routers import health
import os, time, base64, threading, traceback, logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI(title="M-Voice Orchestrator", version="0.1.0")


app.include_router(health.router)
app.include_router(tenants.router)
app.include_router(scripts.router)
app.include_router(tts.router)
app.include_router(flow.router)
# Logger
log = logging.getLogger("mvoice.orch")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_is_ws_connected = False
_stop = False
_last_event_ts = 0.0
_ws_restarts = 0

def _build_ws_url():
    u = os.getenv("ARI_USERNAME", "mvoice")
    p = os.getenv("ARI_PASSWORD", "mvoice8908!#")
    appname = os.getenv("ARI_APP", "mvoice")
    base = os.getenv("ARI_URL", "http://edge:8088/ari").rstrip("/")

    scheme = "wss" if base.startswith("https://") else "ws"
    host = base.split("://", 1)[1]
    if not host.endswith("/ari"):
        host += "/ari"
    url = f"{scheme}://{host}/events?app={appname}&subscribeAll=true"
    token = base64.b64encode(f"{u}:{p}".encode()).decode()
    headers = [f"Authorization: Basic {token}"]
    return url, headers

def _ws_forever():
    """
    Persistent ARI WebSocket with keepalives and bounded backoff.
    Presence is enough to keep Stasis(app) active.
    """
    global _is_ws_connected, _ws_restarts
    import websocket  # websocket-client

    backoff = 1
    while not _stop:
        try:
            url, headers = _build_ws_url()
            log.info("WS: connecting to %s", url)
            _ws_restarts += 1

            def on_open(ws):
                global _is_ws_connected
                _is_ws_connected = True
                try:
                    app.state.is_ws_connected = True
                except Exception:
                    pass
                log.info("WS: connected")

            def on_close(ws, code, msg):
                global _is_ws_connected
                _is_ws_connected = False
                log.warning("WS: closed code=%s msg=%s", code, msg)

            def on_error(ws, err):
                global _is_ws_connected
                _is_ws_connected = False
                log.error("WS error: %s", err)

            def on_message(ws, _msg):
                # Presence; record we've seen traffic
                try:
                    ws.mark_event()
                except Exception:
                    pass
                global _last_event_ts
                _last_event_ts = time.time()
                try:
                    if _msg and isinstance(_msg, (str, bytes)):
                        s = _msg if isinstance(_msg, str) else _msg.decode(errors="ignore")
                        log.info("WS evt: %s", s[:200])
                except Exception:
                    pass

            ws = websocket.WebSocketApp(
                build_ari_ws_url(),
                header=[build_ari_basic_header()],
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )
            wst = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 20, "ping_timeout": 10}, daemon=True)
            wst.start()
            ws.run_forever(ping_interval=20, ping_timeout=10)
        except Exception:
            _is_ws_connected = False
            log.error("WS: exception\n%s", traceback.format_exc())

        time.sleep(min(backoff, 30))
        backoff = min(backoff * 2, 30)

@app.on_event("startup")
def _startup():
    log.info("Starting WS background thread…")
    t = threading.Thread(target=_ws_forever, daemon=True)
    t.start()

@app.on_event("shutdown")
def _shutdown():
    global _stop
    _stop = True
    log.info("Stopping WS background thread…")

@app.get("/health")
def health():
    return JSONResponse({"ws_connected": _is_ws_connected})

@app.get("/ready")
def ready():
    """Readiness: WS must be up and (best-effort) we saw an event in last 60s."""
    ok = _is_ws_connected and (time.time() - _last_event_ts < 60 if _last_event_ts else True)
    status = 200 if ok else 503
    return PlainTextResponse("ready" if ok else "not-ready", status_code=status)

@app.get("/metrics")
def metrics():
    """Tiny text metrics."""
    lines = [
        f'mvoice_ws_connected {int(_is_ws_connected)}',
        f'mvoice_ws_restarts {_ws_restarts}',
        f'mvoice_last_event_ts {_last_event_ts or 0.0}',
    ]
    return PlainTextResponse("\n".join(lines), media_type="text/plain")
