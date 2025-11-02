#!/usr/bin/env bash
set -euo pipefail

# --- 1) Symlinks sicherstellen ---
mkdir -p /usr/share/asterisk/sounds /usr/share/asterisk/sounds/en /var/lib/asterisk/sounds/custom
ln -sfn /var/lib/asterisk/sounds/custom /usr/share/asterisk/sounds/custom
ln -sfn /var/lib/asterisk/sounds/custom /usr/share/asterisk/sounds/en/custom

# --- 2) Rechte auf Sounds/Cache (host-mounted) ---
chmod -R a+rwX /var/lib/asterisk/sounds/custom || true

# --- 3) Optional: Fallback vorwärmen, wenn Key vorhanden ---
if [[ -n "${ELEVENLABS_API_KEY:-}" ]]; then
  VOICE="${ELEVENLABS_VOICE:-21m00Tcm4TlvDq8ikWAM}"
  MODEL="${ELEVENLABS_MODEL:-eleven_multilingual_v2}"
  OUT_WAV="/var/lib/asterisk/sounds/custom/tts_fixed.wav"
  OUT_ALA="/var/lib/asterisk/sounds/custom/tts_fixed.alaw"
  if [[ ! -s "$OUT_WAV" || ! -s "$OUT_ALA" ]]; then
    TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
    curl -sS -f \
      -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
      -H "Accept: audio/mpeg" \
      -H "Content-Type: application/json" \
      --data "{\"text\":\"Dies ist die Fallback-Ansage. Das System ist erreichbar.\",\"model_id\":\"${MODEL}\"}" \
      "https://api.elevenlabs.io/v1/text-to-speech/${VOICE}" -o "$TMP" || true
    if [[ -s "$TMP" ]]; then
      sox -V0 -t mp3 "$TMP" -r 8000 -c 1 -e signed-integer -b 16 "$OUT_WAV" || true
      sox -V0 -t mp3 "$TMP" -r 8000 -c 1 -t al "$OUT_ALA" || true
      chown -R asterisk:asterisk /var/lib/asterisk/sounds || true
    fi
  fi
fi

# --- 4) Asterisk starten (original EntryPoint) ---
exec /entrypoint.sh "$@"
