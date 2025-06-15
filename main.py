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

        try:
            # my personal laptop location
            labrecorder = await asyncio.create_subprocess_exec(
                "C:/Users/annsb/Downloads/LabRecorder-1.16.4-Win_amd64/LabRecorder/LabRecorder.exe",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            subprocesses.append(labrecorder)
        except:
            # lab computer location
            labrecorder = await asyncio.create_subprocess_exec(
                "C:/Users/HCI/Downloads/LabRecorder-1.16.4-Win_amd64/LabRecorder/LabRecorder.exe",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            subprocesses.append(labrecorder)
        
        layer = NbackLayer()
        
        win = visual.Window(
                    fullscr=False,
                    color='black',
                    units='height',
                    # size=[800, 600],
                    # allowGUI=True,
                    # allowStencil=False,
                    # useFBO=False,
                    # useRetina=False,
                    winType='pyglet'
                )

        nback_level = 0
        nback_app = asyncio.create_task(run_pygame_thread(marker_stream=layer, n_level=nback_level, block_num=1, win=win))
            # Run pygame in separate thread
            # pygame_thread = threading.Thread(target=run_pygame_thread, args=(layer, win))
            # pygame_thread.daemon = True
            # pygame_thread.start()

        # Keep async loop running
        # while pygame_thread.is_alive():
        #     await asyncio.sleep(1)

        # while True:
        #     await asyncio.sleep(1)

    # Ctrl+C to exit
    except KeyboardInterrupt:
        pass
    
    # Upon exiting, close all processes
    script.terminate()
    await script.wait()

    labrecorder.terminate()
    await labrecorder.wait()

    # layer.terminate()
    # await layer.wait()

    # nback_app.terminate()
    await nback_app #.wait()




if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())


    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

    