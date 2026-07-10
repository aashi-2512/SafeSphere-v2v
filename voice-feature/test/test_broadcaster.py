import asyncio
import os
import websockets

BROADCASTER_TOKEN = input("Enter broadcaster token: ")

URL = f"ws://127.0.0.1:8000/ws/broadcast?token={BROADCASTER_TOKEN}"


async def main():

    async with websockets.connect(URL) as websocket:

        print("✅ Broadcaster connected")

        while True:

            fake_audio = os.urandom(320)

            await websocket.send(fake_audio)

            print("Sent 320 bytes")

            await asyncio.sleep(1)


asyncio.run(main())