#!/usr/bin/env bash
set -euo pipefail
mkdir -p /var/log/mvoice
nohup python3 /opt/mai/ari_app.py >/var/log/mvoice/ari_app.log 2>&1 &
exec asterisk -f -vvv
