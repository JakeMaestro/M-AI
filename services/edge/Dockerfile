FROM m-voice-edge:v0.2.8

# Pakete für TTS/Convert
RUN apt-get update -qq && \
    apt-get install -y -qq jq sox libsox-fmt-all curl file && \
    rm -rf /var/lib/apt/lists/*

# Boot-Script + TTS-Script einspielen
COPY boot/voiceai-boot.sh /usr/local/bin/voiceai-boot.sh
COPY bin/tts_fetch.sh      /usr/local/bin/tts_fetch.sh
RUN chmod 0755 /usr/local/bin/voiceai-boot.sh /usr/local/bin/tts_fetch.sh

# Unser Boot-Script startet am Ende das originale /entrypoint.sh
ENTRYPOINT ["/usr/local/bin/voiceai-boot.sh"]
