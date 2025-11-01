# M-AI Voice Edge & Orchestrator

Dieses Projekt stellt eine modulare Voice-Agent Architektur bereit, bestehend aus:

| Komponente       | Aufgabe                                                                 |
|------------------|-------------------------------------------------------------------------|
| **edge**         | SIP Signalisierung + RTP Media Handling via Asterisk (PJSIP).           |
| **orchestrator** | Verbindung zu Asterisk ARI (WebSocket), Eventverarbeitung, Stateflow.   |
| **client(s)**    | Stimm-Bots, Workflows, TTS / STT, Business-Logik.                       |

---

## 🏗 Architektur

```mermaid
flowchart LR
    Caller((📞 Anrufer)) --> SIP[Edge / Asterisk (PJSIP)]
    SIP --> ARI[(WebSocket / ARI Events)]
    ARI --> ORCH[Orchestrator (FastAPI + Stateflow)]
    ORCH --> AI[Client / Bot Services (LLM, STT, TTS)]
    AI --> ORCH
    ORCH --> SIP
🚀 Start
bash
Code kopieren
docker compose up -d
Nach dem Start stehen folgende Endpoints bereit:

Endpoint	Beschreibung	Zustand
/healthz	Prozess lebt	Orchestrator läuft
/healthz/deps	Edge + ARI HTTP Auth erreichbar	Basis-Funktion ok
/readyz	Vollständig bereit (inkl. stabiler WebSocket)	Produktionsbereit

Beispiele
bash
Code kopieren
curl -s http://127.0.0.1:18080/healthz | jq .
curl -s http://127.0.0.1:18080/healthz/deps | jq .
curl -s http://127.0.0.1:18080/readyz | jq .
🔐 Asterisk ARI Konfiguration
/etc/asterisk/ari.conf:

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
🔗 WebSocket Verbindung (automatisch generiert)
bash
Code kopieren
ws://edge:8088/ari/events?app=mai&subscribeAll=true&api_key=mai:mvoice8908!#
Credentials werden korrekt encodiert → Stabil auch mit Sonderzeichen.

🧩 Umgebungsvariablen (docker-compose.yml)
yaml
Code kopieren
environment:
  ARI_HOST: edge
  ARI_PORT: "8088"
  ARI_USER: mai
  ARI_PASSWORD: mvoice8908!#
✅ Readiness-Logik (wann /readyz == ok)
Edge ist healthy

ARI HTTP Auth erfolgreich

WebSocket stabil verbunden

Mindestens ein ARI Event empfangen

Beispiel /readyz Ausgabe:

json
Code kopieren
{
  "status": "ok",
  "edge_http_reachable": true,
  "ari_auth": true,
  "ws_connected": true
}
🛠 Troubleshooting
1) /readyz sagt "ari_auth": false
Credentials passen nicht.

bash
Code kopieren
docker exec -t $(docker compose ps -q edge) asterisk -rx "http show status"
docker exec -t $(docker compose ps -q edge) awk 'NF && $1 !~ /^;/' /etc/asterisk/ari.conf
2) In den Logs steht:
lua
Code kopieren
Handshake status 401 Unauthorized
Fix → Stelle sicher, dass die URL &api_key=user:pass enthält.

3) WebSocket Disconnects alle ~60s
Ist behoben → Ping aktiviert (run_forever(ping_interval=20, ping_timeout=10)).

4) /readyz bleibt degraded
Noch kein ARI-Event → Einfach Test-Call triggern:

bash
Code kopieren
EDGE_ID=$(docker compose ps -q edge)
docker exec -t "$EDGE_ID" asterisk -rx \
  'channel originate Local/43720270346@incoming application Echo'
🟢 Systemstatus Übersicht
Komponente	Status
Edge	✅ Healthy
ARI Authentication	✅ OK
WebSocket Verbindung	✅ Stabil
Orchestrator Ready	✅ Aktiv

