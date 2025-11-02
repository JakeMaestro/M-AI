from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
import logging, time, os, base64, traceback, threading

from app.util.leader import LeaderLock
from app.ari.url import build_ari_ws_url, build_ari_basic_header

# ---- Globals used by health router ----
_is_ws_connected = False
_last_event_ts = 0.0
_ws_restarts = 0

app = FastAPI(title="M-AI Orchestrator", version=os.getenv("APP_VERSION", "dev"))

# Routers (nach Globals importieren)
from app.routers import tenants, scripts, tts, flow, health  # noqa: E402
app.include_router(health.router)
app.include_router(tenants.router)
app.include_router(scripts.router)
app.include_router(tts.router)
app.include_router(flow.router)

# Logging
log = logging.getLogger("mvoice.orch")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

leader_lock = LeaderLock()
_stop_ws = False

def _ws_forever():
    """Persistent ARI WebSocket (best-effort). Presence reicht für Readiness."""
    global _is_ws_connected, _ws_restarts, _last_event_ts
    try:
        import websocket  # websocket-client
    except Exception as e:
        log.warning(f"websocket-client not available: {e}")
        return

    backoff = 1
    while not _stop_ws:
        try:
            url = build_ari_ws_url()
            headers = [build_ari_basic_header()]
            log.info("WS: connecting to %s", url)
            _ws_restarts += 1

            def on_open(ws):
                nonlocal backoff
                global _is_ws_connected
                _is_ws_connected = True
                backoff = 1
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
                global _last_event_ts
                _last_event_ts = time.time()
                try:
                    s = _msg if isinstance(_msg, str) else _msg.decode(errors="ignore")
                    log.debug("WS evt: %s", s[:200])
                except Exception:
                    pass

            ws = websocket.WebSocketApp(
                url,
                header=headers,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )
            ws.run_forever(ping_interval=20, ping_timeout=10)
        except Exception:
            _is_ws_connected = False
            log.error("WS: exception\n%s", traceback.format_exc())

        time.sleep(min(backoff, 30))
        backoff = min(backoff * 2, 30)

@app.on_event("startup")
async def _on_startup():
    try:
        await leader_lock.start()
    except Exception as e:
        log.warning("Leader lock start error: %s", e)
    threading.Thread(target=_ws_forever, name="ws-ari", daemon=True).start()

@app.on_event("shutdown")
async def _on_shutdown():
    global _stop_ws
    _stop_ws = True
    try:
        await leader_lock.stop()
    except Exception as e:
        log.warning("Leader lock stop error: %s", e)

@app.get("/metrics")
def metrics():
    lines = [
        f"mvoice_ws_connected {int(_is_ws_connected)}",
        f"mvoice_ws_restarts {_ws_restarts}",
        f"mvoice_last_event_ts {_last_event_ts or 0.0}",
    ]
    return PlainTextResponse("\n".join(lines), media_type="text/plain")
