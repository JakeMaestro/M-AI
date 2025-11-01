# M-AI (Edge + Orchestrator)

A minimal, reboot-tauglicher Voice/Telephony Edge mit Asterisk + ARI und ein leichtgewichtiger Orchestrator (FastAPI/Uvicorn).  
Ziel: stabile Inbound-Calls, ARI-App „mai“, sauberes Logging, Health-Gates und einfache Betriebsführung.

---

## Architektur

- **edge**  
  - Image: `m-voice-edge:v0.2.8`
  - Asterisk 18 + HTTP/ARI (`:8088`), SIP/UDP (`:5060`), RTP (`10000-10049/udp`)
  - ARI-App: `/opt/mai/ari_app.py` (Application Name: `mai`)
  - Dialplan: `extensions.conf` → `Stasis(mai,incoming)`; **Fallback** via `TryExec(...)`
  - Konfigurations-Mount **read-only**: `./services/edge/etc/asterisk:/etc/asterisk:ro`
  - Logs auf Host:  
    - Asterisk: `./services/edge/var/log/asterisk/{full,messages,security,queue_log}`  
    - ARI-App: `./services/edge/var/log/mvoice/ari_app.log`

- **orchestrator**  
  - Image-Name: `m-ai-orchestrator` (lokal gebaut)
  - Port: `18080->8080`
  - Konfiguration: `./config/.env`
  - Flows: `./flows:/app/flows:ro`

---

## Voraussetzungen

- Docker & Docker Compose
- Ubuntu 24.04 (getestet)
- Offener UDP-Portbereich `10000-10049` für RTP (Firewall)

---

## Installation / Update

```bash
# Klonen / Update
git clone https://github.com/JakeMaestro/M-AI.git ~/voiceai-public
cd ~/voiceai-public
git pull

# Build nur für Orchestrator (Edge ist pinbar)
docker compose build orchestrator

