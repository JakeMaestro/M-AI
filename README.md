
# M-Voice — SIP→Azure Speech MVP (Starter)

This repository is a **minimal, Docker-first scaffold** to build an MVP for a
phone-accessible AI assistant that connects SIP calls to Azure Speech and handles
simple workflows (e.g., restaurant reservations, pizza ordering, appointment booking).

> **Status:** Starter kit and placeholders — safe to commit to GitHub and iterate.

---

## What’s inside

- `docker-compose.yml` — runs all services for local/dev on a single Ubuntu host.
- `services/edge/` — SIP edge (Asterisk) config placeholders.
- `services/orchestrator/` — Python FastAPI app that:
  - Receives audio streams (via WebSocket / HTTP placeholders),
  - Calls Azure Speech (STT/TTS) — integration points defined,
  - Implements a **menu-based MVP**,
  - Emits call events + transcripts.
- `flows/` — Human-readable YAML **workflows** that non-engineers can edit.
- `config/.env.example` — All environment variables to copy to `.env`.
- `ops/github-actions/` — Example CI pipeline that lints & builds images.
- `docs/` — Architecture and operations notes.

---

## Quick start (dev)

1. **Prereqs on Ubuntu 22.04+**  
   ```bash
   sudo apt-get update
   sudo apt-get install -y git docker.io docker-compose-plugin
   sudo usermod -aG docker $USER && newgrp docker
   ```

2. **Clone & configure**  
   ```bash
   git clone <YOUR_GITHUB_FORK_URL> mvoice
   cd mvoice
   cp config/.env.example config/.env
   # Edit config/.env and fill in Azure keys & SIP trunk details
   ```

3. **Bring services up**  
   ```bash
   docker compose up -d --build
   docker compose logs -f orchestrator
   ```

4. **Sanity check**  
   - Visit `http://localhost:8080/docs` for the Orchestrator API (FastAPI docs).
   - Place a test call to your SIP DID (after you configure your trunk to the edge).

---

## MVP scope

- Inbound call → greeting → simple DTMF menu (1=Reservation, 2=Order, 3=Appointment).  
- Azure Speech STT for free-form slots (e.g., name, date, time, order items).  
- Azure Speech TTS for responses.  
- Store transcripts + outcomes in a local `sqlite` DB initially (Postgres later).

---

## Workflows (editable by customers)

Workflows live in `flows/*.yaml`. They define:
- Prompts and menus,
- Business hours (open/closed),
- Temporary messages (“Kebap ist aus”), and
- A toggle to **pause** the service per customer.

Non-technical users can change these with a small admin panel (to be added).

---

## Roadmap (suggested)

- Phase 0 (MVP): Menu IVR + STT/TTS + SQLite.
- Phase 1: Replace menu with intent routing; add Postgres + Redis.
- Phase 2: Multi-tenant config; customer Admin Portal (Next.js).
- Phase 3: Call recording, analytics, and queueing.
- Phase 4: High availability (2× edges + SBC) and regional scaling.

See `docs/architecture.md` for details.
