import json, threading, time, urllib.parse
import requests
from websocket import create_connection

ARI_USER = "mvoice"
ARI_PASS = "mvoice8908!#"
BASE = "http://127.0.0.1:8088/ari"
APP = "mai"

def play(channel_id, media):
    qs = urllib.parse.urlencode({"media": media})
    requests.post(f"{BASE}/channels/{channel_id}/play?{qs}", auth=(ARI_USER, ARI_PASS), timeout=3)

def hangup(channel_id):
    requests.delete(f"{BASE}/channels/{channel_id}", auth=(ARI_USER, ARI_PASS), timeout=3)

def on_stasis_start(ev):
    ch = ev.get("channel", {})
    ch_id = ch.get("id")
    if not ch_id: return
    # kurze Begrüßung + Auswahl
    try:
        play(ch_id, "sound:hello-world")
        time.sleep(1.5)
        play(ch_id, "sound:beep")  # Platzhalter: „Bitte 1 oder 2 drücken“
    except Exception:
        pass

def on_dtmf(ev):
    ch = ev.get("channel", {})
    ch_id = ch.get("id")
    digit = ev.get("digit")
    if not ch_id or not digit: return
    try:
        if digit == "1":
            play(ch_id, "sound:auth-thankyou")
            time.sleep(1.0)
            hangup(ch_id)
        elif digit == "2":
            play(ch_id, "sound:vm-goodbye")
            time.sleep(1.0)
            hangup(ch_id)
        else:
            play(ch_id, "sound:beep")  # unbekannt -> nochmal Beep
    except Exception:
        pass

def main():
    # WebSocket für Events
    q = urllib.parse.urlencode({
        "app": APP,
        "api_key": f"{ARI_USER}:{ARI_PASS}",
        "subscribeAll": "true"
    })
    ws = create_connection(f"ws://127.0.0.1:8088/ari/events?{q}")
    while True:
        msg = ws.recv()
        ev = json.loads(msg)
        t = ev.get("type")
        if t == "StasisStart":
            on_stasis_start(ev)
        elif t == "ChannelDtmfReceived":
            on_dtmf(ev)

if __name__ == "__main__":
    main()
