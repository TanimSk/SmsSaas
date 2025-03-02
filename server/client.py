import asyncio
import websockets

async def listen():
    uri = "ws://192.168.1.107:3000/ws/messages/"  # Change IP to your Django server's address
    async with websockets.connect(uri) as websocket:
        print("Connected to server")        
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(listen())
