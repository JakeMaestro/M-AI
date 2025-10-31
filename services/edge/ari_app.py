import json, time, traceback, base64
import requests, websocket

ARI_HOST = "127.0.0.1"
ARI_PORT = 8088
APP      = "mai"
USER     = "mai"
PASS     = "mvoice8908!#"

BASE = f"http://{ARI_HOST}:{ARI_PORT}/ari"
WS   = f"ws://{ARI_HOST}:{ARI_PORT}/ari/events?app={APP}&subscribeAll=true"

s = requests.Session()
s.auth = (USER, PASS)
s.headers.update({"Content-Type":"application/json"})

def dbg(x): print(x, flush=True)

def answer(ch_id):
    r = s.post(f"{BASE}/channels/{ch_id}/answer"); r.raise_for_status()

def play(ch_id, media="sound:hello-world"):
    r = s.post(f"{BASE}/channels/{ch_id}/play", params={"media": media}); r.raise_for_status()

def on_event(evt):
    t = evt.get("type")
    if t == "StasisStart":
        ch = (evt.get("channel") or {})
        cid = ch.get("id")
        dbg(f"➡️  STASIS_START {cid}")
        try:
            answer(cid)
            time.sleep(0.2)
            play(cid, "sound:hello-world")
            dbg(f"✅ answered + playing hello-world (Channel bleibt offen) {cid}")
        except Exception as e:
            dbg(f"❌ error in StasisStart: {e}\n{traceback.format_exc()}")
    elif t == "StasisEnd":
        ch = (evt.get("channel") or {})
        dbg(f"⛔ STASIS_END {ch.get('id')}")

def ws_loop():
    # Basic-Auth per Header (um Sonderzeichen im PW nicht in der URL zu haben)
    token = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
    headers = [f"Authorization: Basic {token}"]

    while True:
        try:
            dbg(f"🔌 connecting WS {WS}")
            ws = websocket.create_connection(WS, header=headers, timeout=10)
            dbg("🎧 ARI WS connected")
            ws.settimeout(30)
            last_ping = time.time()
            while True:
                if time.time() - last_ping > 20:
                    try: ws.ping()
                    except Exception: pass
                    last_ping = time.time()
                raw = ws.recv()
                if not raw: 
                    continue
                evt = json.loads(raw)
                on_event(evt)
        except Exception as e:
            dbg(f"WS error: {e}; reconnect in 2s")
            time.sleep(2)

if __name__ == "__main__":
    dbg("🚀 ARI loop starting…")
    ws_loop()
