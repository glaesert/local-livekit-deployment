from livekit import api

LIVEKIT_URL = "ws://localhost:7880"
LIVEKIT_API_KEY = "devkey"
LIVEKIT_API_SECRET = "secret"

ROOM_NAME = "my-room"


if __name__ == "__main__":
    token = (
        api.AccessToken(
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        )
        .with_identity("web-client")
        .with_name("web-client")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=ROOM_NAME,
            )
        )
        .to_jwt()
    )
    
    print(token)
    