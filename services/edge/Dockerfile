FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Asterisk + Python Runtime + Tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      tzdata \
      asterisk asterisk-core-sounds-en asterisk-moh-opsound-wav \
      python3 python3-pip ca-certificates curl \
 && ln -fs /usr/share/zoneinfo/Europe/Vienna /etc/localtime \
 && dpkg-reconfigure --frontend noninteractive tzdata \
 && pip3 install --no-cache-dir requests websocket-client \
 && rm -rf /var/lib/apt/lists/*

# Asterisk-Configs ins Image
COPY etc/asterisk/ /etc/asterisk/

# ARI-App ins Image
COPY ari_app.py /opt/mai/ari_app.py

# Entrypoint für Autostart (ARI-App + Asterisk im Vordergrund)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
