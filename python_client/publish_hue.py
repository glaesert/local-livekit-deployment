import asyncio
import colorsys
import logging
import os
from signal import SIGINT, SIGTERM

import numpy as np
from livekit import api, rtc

WIDTH, HEIGHT = 1280, 720

LIVEKIT_URL = "ws://localhost:7880"
LIVEKIT_API_KEY = "devkey"
LIVEKIT_API_SECRET = "secret"
LIVEKIT_ROOM_NAME = "my-room"

# ensure LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET are set
livekit_url = os.getenv("LIVEKIT_URL", LIVEKIT_URL)
livekit_api_key = os.getenv("LIVEKIT_API_KEY", LIVEKIT_API_KEY)
livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", LIVEKIT_API_SECRET)
livekit_room_name = os.getenv("LIVEKIT_ROOM_NAME", LIVEKIT_ROOM_NAME)

async def main(room: rtc.Room):
    print("CONFIG:")
    print(f"LIVEKIT_URL: {livekit_url}")
    print(f"LIVEKIT_API_KEY: {livekit_api_key}")
    print(f"LIVEKIT_API_SECRET: {livekit_api_secret}")
    print(f"LIVEKIT_ROOM_NAME: {livekit_room_name}")

    token = (
        api.AccessToken(
            api_key=livekit_api_key,
            api_secret=livekit_api_secret,
        )
        .with_identity("python-publisher")
        .with_name("Python Publisher")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=livekit_room_name,
            )
        )
        .to_jwt()
    )

    logging.info("connecting to %s", livekit_url)
    try:
        await room.connect(livekit_url, token)
        logging.info("connected to room %s", room.name)
    except rtc.ConnectError as e:
        logging.error("failed to connect to the room: %s", e)
        return

    # publish a track
    source = rtc.VideoSource(WIDTH, HEIGHT)
    track = rtc.LocalVideoTrack.create_video_track("hue", source)
    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_CAMERA
    publication = await room.local_participant.publish_track(track, options)
    logging.info("published track %s", publication.sid)

    asyncio.ensure_future(draw_color_cycle(source))


async def draw_color_cycle(source: rtc.VideoSource):
    argb_frame = rtc.ArgbFrame.create(rtc.VideoFormatType.FORMAT_ARGB, WIDTH, HEIGHT)
    arr = np.frombuffer(argb_frame.data, dtype=np.uint8)

    framerate = 1 / 30
    hue = 0.0

    while True:
        start_time = asyncio.get_event_loop().time()

        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        rgb = [(x * 255) for x in rgb]  # type: ignore

        argb_color = np.array(rgb + [255], dtype=np.uint8)
        arr.flat[::4] = argb_color[0]
        arr.flat[1::4] = argb_color[1]
        arr.flat[2::4] = argb_color[2]
        arr.flat[3::4] = argb_color[3]

        frame = rtc.VideoFrame(
            0, rtc.VideoRotation.VIDEO_ROTATION_0, argb_frame.to_i420()
        )

        source.capture_frame(frame)
        hue = (hue + framerate / 3) % 1.0

        code_duration = asyncio.get_event_loop().time() - start_time
        await asyncio.sleep(1 / 30 - code_duration)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.FileHandler("publish_hue.log"), logging.StreamHandler()],
    )

    loop = asyncio.get_event_loop()
    room = rtc.Room(loop=loop)

    async def cleanup():
        await room.disconnect()
        loop.stop()

    asyncio.ensure_future(main(room))
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, lambda: asyncio.ensure_future(cleanup()))

    try:
        loop.run_forever()
    finally:
        loop.close()