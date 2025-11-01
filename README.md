(PASTE HIER DEN NEUEN README TEXT REIN)

# 2. Änderungen anzeigen (optional)
git status
git diff README.md

# 3. Commit
git add README.md
git commit -m "docs: update README and troubleshooting steps"

# 4. Push zur main
git push origin main

# 5. Optional Release Tag erstellen
git tag -a v1.0.3 -m "v1.0.3 updated README and deployment instructions"
git push origin v1.0.3


# M-AI Voice Edge & Orchestrator

Dieses Projekt stellt eine modulare Voice-Agent Architektur bereit, bestehend aus:

| Komponente     | Aufgabe                                                                 |
|----------------|-------------------------------------------------------------------------|
| **edge**       | SIP Signalisierung + RTP Media Handling via Asterisk (PJSIP).           |
| **orchestrator** | Verbindung zum Asterisk ARI (WebSocket), Eventverarbeitung, State-Flow. |
| **client(s)**  | Stimm-Bots, Workflows, TTS / STT, Logik.                                |

---

## Start

```bash
docker compose up -d
Nach dem Start stehen folgende Health Endpoints zur Verfügung:

Endpoint	Beschreibung	Status-Kriterium
/healthz	lebt der Prozess?	Orchestrator gestartet
/healthz/deps	kann Orchestrator mit Edge sprechen?	HTTP erreichbar + ARI-Auth
/readyz	System betriebsbereit?	Edge gesund + ARI Auth + WebSocket verbunden

Beispiele
bash
Code kopieren
curl -s http://127.0.0.1:18080/healthz | jq .
curl -s http://127.0.0.1:18080/healthz/deps | jq .
curl -s http://127.0.0.1:18080/readyz | jq .
Asterisk ARI Zugang
ari.conf

ini
Code kopieren
[general]
enabled = yes
pretty = yes
allowed_origins = *

[mai]
type = user
read_only = no
password = mvoice8908!#
Orchestrator ARI WebSocket Verbindung
Die ARI-WebSocket-URL wird dynamisch generiert:

python
Code kopieren
ws://edge:8088/ari/events?app=mai&subscribeAll=true&api_key=mai:mvoice8908!#
(Inklusive URL-Sicherheit — Sonderzeichen werden korrekt encodiert.)

Wichtig:
Credential-Pass-Through erfolgt über docker-compose.yml:

yaml
Code kopieren
environment:
  ARI_HOST: edge
  ARI_PORT: "8088"
  ARI_USER: mai
  ARI_PASSWORD: mvoice8908!#
Readiness-Logik
Der Orchestrator wird erst als „bereit“ markiert, wenn:

Edge läuft und ist healthy

ARI HTTP Basic Auth funktioniert

WebSocket stabil verbunden

Dies wird über /readyz abgebildet:

json
Code kopieren
{
  "status": "ok",
  "edge_http_reachable": true,
  "ari_auth": true,
  "ws_connected": true
}
⚙️ Troubleshooting
1) /readyz zeigt "ari_auth": false
Ursache: ARI Credentials falsch, nicht übereinstimmend oder vergessen.

Check:

bash
Code kopieren
docker exec -t $(docker compose ps -q edge) asterisk -rx "http show status"
docker exec -t $(docker compose ps -q edge) awk 'NF && $1 !~ /^;/' /etc/asterisk/ari.conf
Fix:
docker-compose.yml und ari.conf müssen dieselben Werte haben.

2) Logs zeigen: Handshake status 401 Unauthorized
Ursache: WebSocket ohne Auth / falsches Password

Fix:
Stelle sicher, dass die WebSocket-URL api_key=user:pass enthält.

Soll so aussehen:

bash
Code kopieren
ws://edge:8088/ari/events?...&api_key=mai:mvoice8908!#
3) WebSocket disconnects alle ~60s
Ursache: Ping fehlt.

Fix:
ws.run_forever(ping_interval=20, ping_timeout=10) — bereits in Code umgesetzt.

4) Edge ist gesund, aber /readyz bleibt degraded
Ursache: Noch kein WS-Event → _last_event_ts nicht gesetzt.

Minimaler Test-Call auslösen:

bash
Code kopieren
EDGE_ID=$(docker compose ps -q edge)
docker exec -t "$EDGE_ID" asterisk -rx \
  'channel originate Local/43720270346@incoming application Echo'
✅ Status
Komponente	Zustand
Edge	Healthy
ARI Authentication	OK
WebSocket Verbindung	Stabil
Readiness Workflow	Aktiviert
