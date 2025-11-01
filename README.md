# M-AI Voice Edge & Orchestrator

Dieses Projekt stellt eine modulare Voice-Agent Architektur bereit, bestehend aus:

| Komponente       | Aufgabe                                                                 |
|------------------|-------------------------------------------------------------------------|
| **edge**         | SIP Signalisierung + RTP Media Handling via Asterisk (PJSIP).           |
| **orchestrator** | Verbindung zu Asterisk ARI (WebSocket), Eventverarbeitung, Stateflow.   |
| **client(s)**    | Stimm-Bots, Workflows, TTS / STT, Business-Logik.                       |

---

## 🚀 Start

```bash
docker compose up -d
Nach dem Start stehen folgende Health Endpoints bereit:

Endpoint	Beschreibung	Zustandskriterium
/healthz	Prozess lebt	Orchestrator läuft
/healthz/deps	Edge + ARI HTTP Auth erreichbar	System Grundfunktionen ok
/readyz	Vollständig bereit (inkl. WebSocket verbunden)	produktionsbereit

Beispiele
bash
Code kopieren
curl -s http://127.0.0.1:18080/healthz | jq .
curl -s http://127.0.0.1:18080/healthz/deps | jq .
curl -s http://127.0.0.1:18080/readyz | jq .
🔐 Asterisk ARI Konfiguration (/etc/asterisk/ari.conf)
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
🔗 ARI WebSocket Verbindung
Die Verbindung wird automatisch generiert:

bash
Code kopieren
ws://edge:8088/ari/events?app=mai&subscribeAll=true&api_key=mai:mvoice8908!#
Sonderzeichen (!) und (#) werden korrekt encodiert, daher stabil.

🧩 Orchestrator ARI Credentials (docker-compose.yml)
yaml
Code kopieren
environment:
  ARI_HOST: edge
  ARI_PORT: "8088"
  ARI_USER: mai
  ARI_PASSWORD: mvoice8908!#
✅ Readiness-Logik
Der Orchestrator meldet sich erst ready, wenn:

Edge läuft und ist healthy

ARI HTTP Basic Auth erfolgreich

WebSocket stabil verbunden

Mindestens ein ARI-Event empfangen wurde (State aktiv)

Beispiel /readyz Output:

json
Code kopieren
{
  "status": "ok",
  "edge_http_reachable": true,
  "ari_auth": true,
  "ws_connected": true
}
🛠 Troubleshooting
1) /readyz zeigt "ari_auth": false
Ursache: Credentials zwischen ari.conf und docker-compose.yml stimmen nicht überein.

Check:

bash
Code kopieren
docker exec -t $(docker compose ps -q edge) asterisk -rx "http show status"
docker exec -t $(docker compose ps -q edge) awk 'NF && $1 !~ /^;/' /etc/asterisk/ari.conf
2) Logs zeigen:
lua
Code kopieren
Handshake status 401 Unauthorized
Fix: Stelle sicher, dass die URL &api_key=user:pass enthält.

3) WebSocket Disconnects alle 60s
Fix: Ist bereits gelöst → run_forever(ping_interval=20, ping_timeout=10) aktiv.

4) /readyz bleibt degraded obwohl alles läuft
Ursache: Noch kein WS-Event → _last_event_ts nicht gesetzt.

Test-Anruf auslösen:

bash
Code kopieren
EDGE_ID=$(docker compose ps -q edge)
docker exec -t "$EDGE_ID" asterisk -rx \
  'channel originate Local/43720270346@incoming application Echo'
🟢 Systemstatus
Komponente	Status
Edge	✅ Healthy
ARI Authentication	✅ OK
WebSocket Verbindung	✅ Stabil
Orchestrator Ready	✅ Aktiv

