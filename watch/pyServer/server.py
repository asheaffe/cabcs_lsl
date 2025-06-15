import asyncio
from websockets.asyncio.server import serve
import websockets
import aiofiles
import sys
import os
from inputs import get_gamepad

# netstat -ano | findstr :8765
# windows + R -> resmon -> sort by pid and find the one from last step [[last number output]]

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lsl_app.device_layers.drt_layer import DRT_layer

movementRequest = False

# initialize DRT layer
drt = DRT_layer()

# Keep track of connected clients
connected_clients = set()

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\03[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'

async def echo(websocket):
    global movementRequest
    try:
        connected_clients.add(websocket)
        async for message in websocket:
            print(f"{GREEN}Received message from client!{RESET}")
            # Append mode (adds to the end)
            if not movementRequest:
                async with aiofiles.open("data.txt", "a") as f:
                    await f.write(f"{message}\n")
            else:
                async with aiofiles.open("requestedData.txt", "a") as f:
                    await f.write(f"{message}\n")
            if (message == "movement"):
                movementRequest = False
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"{RED}Client dc'd: {e}{RESET}")
        connected_clients.remove(websocket)
    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}")

async def send_periodic_messages():
    global movementRequest
    while True:
        print(f"len conn clients: {len(connected_clients)}")
        if len(connected_clients) > 0:
            movementRequest = True
            await asyncio.gather(*[client.send("EXECUTE_VIBRATION") for client in connected_clients])

            # send to lsl 
            drt.send_sample("STIM")
        await asyncio.sleep(10)
        

async def main():
    print(f"WebSocket server is running")
    # Create the periodic hello message task
    sendMsgs = asyncio.create_task(send_periodic_messages())
    async with serve(echo, "0.0.0.0", 8765) as server:
        sendMsgs
        await server.serve_forever()
        # # Start periodic message task
        # await asyncio.gather(server.wait_closed(), send_periodic_messages())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"{BLUE}Server stopped by keyboard interrupt{RESET}")

