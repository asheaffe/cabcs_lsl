import asyncio
import threading
import atexit
from websockets.asyncio.server import serve
from websockets.sync.client import connect

import socket
import websockets
import aiofiles
import glob
import sys
import time
import signal
import os
from psychopy import visual
from rich import print
from lsl_app.device_layers.nback_layer import NbackLayer
from watch.pyServer.server import Server
from nback_2025.nback import Nback
from qualtrics import Qualtrics

global subprocesses
subprocesses = []

global keep_running
keep_running = True     # keeping this here in case it becomes relevant again. always stays True

def signal_handler(sig, frame):
    #global keep_running
    print("Finishing current task and shutting down...")
    #keep_running = False

    # exit program when signal is received
    os._exit(0)

# signal handler
signal.signal(signal.SIGINT, signal_handler)

def clean_subprocesses():
    """Cleanup function at exit. Replaces need for gobbledygook at the end of main"""
    for proc in subprocesses:
        try:
            if hasattr(proc,'terminate') and proc.returncode is None:
                proc._transport.close()
        except:
            pass

# register cleanup
atexit.register(clean_subprocesses)

# async def run_pygame_thread(**kwargs):
#     """Run pygame in separate thread"""
#     try:           
#         await Nback(**kwargs) 
#     except Exception as e:
#         print(f"Pygame error: {e}")

async def main():
    try:
        script = await asyncio.create_subprocess_exec(
            'powershell', '-ExecutionPolicy', 'Bypass', '-File', 'processes.ps1',
            # stdout=asyncio.subprocess.PIPE,
            # stderr=asyncio.subprocess.PIPE
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

        sock = connect("ws://localhost:8765")
        
        #subprocesses.append(qualtrics)

        # keep receiving nback data until Ctrl+C
        while keep_running:
            # try:
                print("waiting for POST data...")

                # wait for POST request
                await qualtrics.data_received_event.wait()

                # extract data from json when POST is received
                qdata = qualtrics.json_data
                nback_level = int(qdata['field1'].split(" ")[1][0])
                if_walk = qdata['field1'].split(" ")[0]
                block_num = int(qdata['blockNum'])
                practice = bool(qdata["practice"])
                pid = int(qdata["pid"])

                print(f"STARTING NBACK LEVEL: {nback_level}     BLOCK #: {block_num}")
                print(f"PRACTICE: {practice}\tPID: {pid}\tif_walk: {if_walk}")

                win = visual.Window(
                            fullscr=False,
                            color='black',
                            units='height',
                            winType='pyglet'
                        )
            
                await asyncio.create_task(Nback(n_level=nback_level, 
                       block_num=block_num,                                              
                       pid=pid, 
                       practice=practice,
                       marker_stream=layer, 
                       win=win, 
                       DRT_socket=sock, 
                       walking=if_walk))                

                # reset event for next iteration
                qualtrics.data_received_event.clear()
            
            # except Exception as e:
            #     print(f"Error occurred: {e}")
            #     if not keep_running:
            #         break

    # Ctrl+C to exit
    except KeyboardInterrupt:
        print("Program interrupted by user")

    # except Exception as e:
    #     print(f"Error occurred: {e}")

    finally:
        print("Cleaning all subprocesses...")

        # close psychopy window
        if 'win' in locals():
            win.close()

        # close qualtrics
        if 'qualtrics' in locals():
            await qualtrics.cleanup()

        # close ngrok terminal
        if 'ngrok' in locals():
            await ngrok.cleanup()

        print("Cleanup complete")


        # forcibly exits
        #os._exit(0)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())

    