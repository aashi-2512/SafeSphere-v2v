import asyncio
import websockets

LISTENER_TOKEN = input("Enter listener token: ")

URL = f"ws://127.0.0.1:8000/ws/listen?token={LISTENER_TOKEN}"


async def main():
    async with websockets.connect(URL) as websocket:
        print("✅ Listener connected")

        while True:
            data = await websocket.recv()

            print(f"Received {len(data)} bytes")


asyncio.run(main())