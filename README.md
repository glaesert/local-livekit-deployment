# Local LiveKit Deployment

## Setup
1. Start Docker Compose Deployment
    `docker compose -f livekit_local.yml up -d`
2. Generate Client Token
    `python ./python_client/generate_token.py`
3. Navigate to Web Client
    `http://localhost:8080`
4. Enter URL and Token
    - LiveKitURL: `ws://\<ip-of-livekit-host\>:7880`
    - Token: Enter generated token
5. Press Connect

## Notes
- Works on local machine and in local network
- Works with or without internet connection
    - If no internet available: Set `use_external_ip` in `livekit.yaml` to `false`
- LiveKit server must be started with `network_mode=host`
    - Otherwise, an internet connection is required
    - (Possible) reason: Clients must be able to find their host IP
        - In a Docker network this is only possible by connecting to a STUN server over the internet
    - TODO: Find way to deploy LiveKit server inside Docker network without the need for an internet connection