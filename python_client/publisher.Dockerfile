FROM python:3.12.0-bullseye

RUN pip install numpy livekit livekit-api

WORKDIR /client
COPY publish_hue.py .
