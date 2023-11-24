FROM ubuntu:20.04

RUN apt update && apt upgrade -y && apt install -y curl

WORKDIR /livekit

RUN curl -sSL https://get.livekit.io >> livekit_install.sh | bash
RUN chmod +x livekit_install.sh
RUN ./livekit_install.sh
