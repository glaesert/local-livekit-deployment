FROM node:21-bullseye

RUN apt update && apt upgrade -y
RUN apt install -y git 
RUN apt install -y npm
RUN npm install -g pnpm

RUN git clone https://github.com/livekit/client-sdk-js.git

WORKDIR /client-sdk-js/example
RUN pnpm install