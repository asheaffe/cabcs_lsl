import asyncio
from websockets.asyncio.server import serve
import websockets
import aiofiles
from rich import print

async def main():
    # run lsl_app.py first
    lsl_app_process = await asyncio.create_subprocess_exec(
        'python', 'lsl_app/lsl_app.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await lsl_app_process.communicate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"[blue]Server stopped by keyboard interrupt[/blue]")