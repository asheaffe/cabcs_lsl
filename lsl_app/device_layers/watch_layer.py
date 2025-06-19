import asyncio
import pylsl
from websockets.asyncio.server import serve
import websockets
import aiofiles
from rich import print

CLIENT = None

def create_lsl_outlet(name, channel_count, channel_names, sampling_rate):
    info = pylsl.StreamInfo(
        name=name,
        type='Biometrics',
        channel_count=channel_count,
        nominal_srate=sampling_rate,
        channel_format='float32',
        source_id=f'watch_{name}'
    )
    
    # Add channel metadata
    channels = info.desc().append_child("channels")
    for ch_name in channel_names:
        channels.append_child("channel").append_child_value("label", ch_name)
    
    outlet = pylsl.StreamOutlet(info)
    return outlet

hr_outlet   = create_lsl_outlet('HeartRate', 2, ['HR', 'IBI'], 1.0)  
hr_outlet   = create_lsl_outlet("HR", 1, ['HR', 'hr_status'], 1.0)
acc_outlet  = create_lsl_outlet('Accelerometer', 3, ['accX', 'accY', 'accZ'], 25.0) 
temp_outlet = create_lsl_outlet('Temperature', 1, ['ambientTemp', 'objTemp'], .2)

async def server_code():
    print(f"[green]Client Connected![/green]")
    CLIENT = websocket
    
    sendMsgs = asyncio.create_task(run_DRT())

    async with websockets.connect("ws://localhost:8765") as websocket:
        print("[green]Watch layer connected to server![/green]")
        async for message in websocket:
            
            async with aiofiles.open("data.txt", "a") as f:
                await f.write(f"{message}\n")

            match message['name']:
                case "Heart Rate":
                    hr_outlet.push_sample([message['hr'], message['hrStatus']])
                case "Accelerometer":
                    acc_outlet.push_sample([message['x'], message['y'], message['z']])
                case "Skin Temp": 
                    temp_outlet.push_sample([message['ambientTemp'], message['objTemp']])
    
async def process_watch_data(data):
    """Process watch data and send to LSL"""
    try:
        match data.get('name'):
            case "Heart Rate":
                hr_outlet.push_sample([message['hr'], message['hrStatus']])
            case "Accelerometer":
                acc_outlet.push_sample([message['x'], message['y'], message['z']])
            case "Skin Temp": 
                temp_outlet.push_sample([message['ambientTemp'], message['objTemp']])
            case _:
                print(f"[yellow]Unknown data type: {data.get('name')}[/yellow]")

    except KeyError as e:
        print(f"[red]Missing key in watch data: {e}[/red]")
    except Exception as e:
        print(f"[red]Error processing watch data: {e}[/red]")

async def run_DRT(websocket):
    try:
        async for message in websocket:
            async with aiofiles.open("data.txt", "a") as f:
                await f.write(f"{message}\n")

            if message == "EXECUTE VIBRATION":
                
                for i in range(10):
                    await asyncio.sleep(10)
                    await websocket.send("EXECUTE_VIBRATION")
                
            elif message.startswith('{'):
                try:
                    data = json.loads(message)
                    await process_watch_data(data)
                except json.JSONDecodeError:
                    print(f"[red]Failed to parse JSON: {message}[/red]")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[red]Connection closed: {e}[/red]")

async def main():
    uri = "ws://localhost:8765"
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            async with websockets.connect(uri) as websocket:
                print("[green]Successfully connected to server![/green]")
                
                # message handling
                message_handler = asyncio.create_task(run_DRT(websocket))
                
                # wait for task to complete
                done, pending = await asyncio.wait(
                    [message_handler],
                    return_when=asyncio.FIRST_COMPLETED
                )

                # cancel any remaining tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # check if any task had an exception
                for task in done:
                    if task.exception():
                        print(f"[red]Task failed with exception: {task.exception()}[/red]")

                break

        except ConnectionRefusedError:
            print(f"[red]Connection refused. Server may not be running[/red]")
            if attempt < max_retries -1:
                print(f"[yellow]Retrying in {retry_delay} seconds...[/yellow]")
                await asyncio.sleep(retry_delay)
            else:
                print("[red]Max retries reached. Exiting[/red]")

        except Exception as e:
            print(f"[red]Unexpected error: {e}[/red]")
            if attempt < max_retries - 1:
                print(f"[yellow]Retrying in {retry_delay} seconds...[/yellow]")
                await asyncio.sleep(retry_delay)
            else:
                print(f"[red]Max retries reached. Exiting[/red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"[blue]Server stopped by keyboard interrupt[/blue]")
    except Exception as e:
        print(f"[red]Fatal error: {e}[/red]")