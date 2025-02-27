import asyncio
import websockets

async def listen():
    uri = "ws://127.0.0.1:8000/ws/messages/"  # Change IP to your Django server's address
    async with websockets.connect(uri) as websocket:
        print("Connected to server")        
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(listen())
