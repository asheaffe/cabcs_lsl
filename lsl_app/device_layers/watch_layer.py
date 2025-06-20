import asyncio
import pylsl
from websockets.asyncio.server import serve
import websockets
import aiofiles
from rich import print
import json


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

hr_outlet   = create_lsl_outlet('HeartRate', 3, ['HR', 'hrStatus', 'IBI'], 1.0)  
acc_outlet  = create_lsl_outlet('Accelerometer', 3, ['accX', 'accY', 'accZ'], 25.0) 
temp_outlet = create_lsl_outlet('Temperature', 2, ['ambientTemp', 'objTemp'], .2)

global CLIENTS
CLIENTS = set()

async def receive_watch_data(socket):
    global CLIENTS
    CLIENTS.add(socket)
    if len(CLIENTS) == 1:
        print(f"[green]DRT Client Connected![/green]")    
    else:
        print(f"[green]Watch Client Connected![/green]")
        
    async for message in socket:
        if message == "EXECUTE_VIBRATION":
            for client in CLIENTS:                
                await client.send("EXECUTE_VIBRATION")                
        else:
            async with aiofiles.open("data.txt", "a") as f:
                await f.write(f"{message}\n")
            
            try:
                data = json.loads(message)                
            except Exception as e:
                print("[yellow]message not valid json. skipping.[/yellow]")
                        
            match data.get('name'):
                case "HR":                    
                    hr_outlet.push_sample([data['hr'], data['hrStatus'], data['iBI']])
                case "Accelerometer":
                    acc_outlet.push_sample([data['x'], data['y'], data['z']])
                case "Skin Temp":                     
                    temp_outlet.push_sample([data['ambientTemp'], data['objTemp']])
                case _:
                    print(f"[yellow]Unknown data type: {data.get('name')}[/yellow]")
                        
async def main():
    async with serve(receive_watch_data, "0.0.0.0", 8765) as server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"[blue]Server stopped by keyboard interrupt[/blue]")
    except Exception as e:
        print(f"[red]Fatal error: {e}[/red]")