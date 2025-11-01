#!/usr/bin/env bash
set -euo pipefail

mkdir -p /var/log/mvoice

# ARI App starten (hinten dran), Logfile sicherstellen
nohup python3 /opt/mai/ari_app.py > /var/log/mvoice/ari_app.log 2>&1 &

# Asterisk im Vordergrund (damit Container "gesund" bleibt)
exec asterisk -f -vvv
