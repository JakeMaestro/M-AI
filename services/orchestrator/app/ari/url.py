import os
import base64
from urllib.parse import quote

def build_ari_ws_url(app_name: str = "mai") -> str:
    host = os.getenv("ARI_HOST", "edge")
    port = os.getenv("ARI_PORT", "8088")
    user = os.getenv("ARI_USER", "mai")
    pwd  = os.getenv("ARI_PASSWORD", "mvoice8908!#")  # TESTPASSWORT
    u = quote(user, safe="")
    p = quote(pwd,  safe="")
    # Wichtig: api_key=user:pass ergänzen (Asterisk ARI akzeptiert das zuverlässig)
    return (f"ws://{host}:{port}/ari/events"
            f"?app={app_name}&subscribeAll=true&api_key={u}:{p}")

def build_ari_basic_header() -> str:
    user = os.getenv("ARI_USER", "mai")
    pwd  = os.getenv("ARI_PASSWORD", "mvoice8908!#")  # TESTPASSWORT
    token = base64.b64encode(f"{user}:{pwd}".encode("utf-8")).decode("ascii")
    return f"Authorization: Basic {token}"
