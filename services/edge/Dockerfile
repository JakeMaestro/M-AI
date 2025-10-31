FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y asterisk asterisk-core-sounds-en asterisk-moh-opsound-wav \
                       wget curl iproute2 dnsutils && \
    mkdir -p /usr/lib/asterisk && \
    ln -s /usr/lib/x86_64-linux-gnu/asterisk/modules /usr/lib/asterisk/modules || true && \
    rm -rf /var/lib/apt/lists/*
CMD ["asterisk","-f","-vvv"]
