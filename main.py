import asyncio
import threading
import atexit
from websockets.asyncio.server import serve
import websockets
import aiofiles
import glob
import sys
import time
import os
from psychopy import visual
from rich import print
from lsl_app.device_layers.nback_layer import NbackLayer
from nback_2025.nback import Nback
from qualtrics import Qualtrics

global subprocesses
subprocesses = []

global nback_running
nback_running = None

def clean_subprocesses():
    """Cleanup function for silencing error messages on Ctrl+C"""
    for proc in subprocesses:
        try:
            proc.terminate()
        except Exception as e:
            print(f"Process terminated with exception: {e}")

# register cleanup
atexit.register(clean_subprocesses)

async def start_chunk(directory):
    """Runs a chunk of python files asynchronously
    
    :param directory: string dir that contain files to run"""
    files = glob.glob(directory)
    process = None

    # iterate over each globbed file and run it
    for file in files:
        process = await asyncio.create_subprocess_exec(
            'python', file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # print message that file started
        try:
            start_output = ""
            try:
                line = await asyncio.wait_for(
                    process.stdout.readline(),
                    timeout=2.0
                )

            except asyncio.TimeoutError:
                pass

            if process.returncode is None:
                print(f"{file} started successfully!")
                return process
            
            print(f"{file} exited with code {process.returncode}")

        except asyncio.TimeoutError:
            print(f"{file} failed to execute properly")
            return None

async def run_pygame_thread(**kwargs):
    """Run pygame in separate thread"""
    # try:           
    Nback(**kwargs) 
    # except Exception as e:
    #     print(f"Pygame error: {e}")

async def main():
    try:
        script = await asyncio.create_subprocess_exec(
            'powershell', '-ExecutionPolicy', 'Bypass', '-File', 'processes.ps1',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        subprocesses.append(script)

        layer = NbackLayer()

        try:
            # my personal laptop location
            labrecorder = await asyncio.create_subprocess_exec(
                "C:/Users/annsb/Downloads/LabRecorder-1.16.4-Win_amd64/LabRecorder/LabRecorder.exe",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            subprocesses.append(labrecorder)
        except FileNotFoundError as f:
            # lab computer location
            labrecorder = await asyncio.create_subprocess_exec(
                "C:/Users/HCI/Downloads/LabRecorder-1.16.4-Win_amd64/LabRecorder/LabRecorder.exe",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            subprocesses.append(labrecorder)

        # get post data from qualtrics 
        qualtrics = await Qualtrics.create()
        subprocesses.append(qualtrics)

        print("waiting for POST data...")

        await qualtrics.data_received_event.wait()
        
        qdata = qualtrics.json_data
        nback_level = int(qdata['field1'].split(" ")[1][0])
        block_num = int(qdata['blockNum'])

        win = visual.Window(
                    fullscr=False,
                    color='black',
                    units='height',
                    winType='pyglet'
                )

        nback_app = asyncio.create_task(run_pygame_thread(marker_stream=layer, n_level=nback_level, block_num=block_num, win=win))

        await nback_app 

    # Ctrl+C to exit
    except KeyboardInterrupt:
        print("Program interrupted by user")

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        print("Cleaning all subprocesses...")

        # close psychopy window
        if 'win' in locals():
            win.close()

        # close ngrok server
        if 'qualtrics' in locals():
            await qualtrics.cleanup()

        # Upon exiting, close all processes
        for process in subprocesses:
            try:
                if hasattr(process, 'terminate'):
                    process.terminate()
                    await process.wait()

            except Exception as e:
                print(f"Error terminating process: {e}")

        print("Cleanup complete")

        os._exit(0)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())

    