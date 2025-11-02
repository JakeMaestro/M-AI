#!/usr/bin/env bash
set -euo pipefail
VOICE="${ELEVENLABS_VOICE:-21m00Tcm4TlvDq8ikWAM}"
MODEL="${ELEVENLABS_MODEL:-eleven_multilingual_v2}"
API_KEY="${ELEVENLABS_API_KEY:?ELEVENLABS_API_KEY missing}"
TEXT="${1:-}"
if [[ "${TEXT}" == "--text" ]]; then TEXT="${2:-}"; fi
if [[ -z "${TEXT}" ]]; then printf "%s" "custom/tts_fixed"; exit 0; fi
BASE_DIR="/var/lib/asterisk/sounds/custom/tts_cache"
mkdir -p "${BASE_DIR}"
HASH="$(printf "%s" "${VOICE}|${MODEL}|${TEXT}" | sha1sum | awk "{print \$1}")"
BASE="${BASE_DIR}/${HASH}"
if [[ ! -s "${BASE}.wav" || ! -s "${BASE}.alaw" ]]; then
  TMP="$(mktemp)"; trap "rm -f \"${TMP}\"" EXIT
  curl -sS -f --connect-timeout 3 --max-time 10 \
    -H "xi-api-key: ${API_KEY}" \
    -H "Accept: audio/mpeg" \
    -H "Content-Type: application/json" \
    --data "{\"text\":$(printf "%s" "${TEXT}" | jq -Rs .),\"model_id\":\"${MODEL}\"}" \
    "https://api.elevenlabs.io/v1/text-to-speech/${VOICE}" -o "${TMP}"
  sox -V0 -t mp3 "${TMP}" -r 8000 -c 1 -e signed-integer -b 16 "${BASE}.wav"
  sox -V0 -t mp3 "${TMP}" -r 8000 -c 1 -t al "${BASE}.alaw"
  chown asterisk:asterisk "${BASE}.wav" "${BASE}.alaw"
fi
printf "%s" "custom/tts_cache/${HASH}"
