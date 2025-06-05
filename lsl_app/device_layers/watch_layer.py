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

async def server_code(websocket):
    print(f"[green]Client Connected![/green]")
    CLIENT = websocket
    
    sendMsgs = asyncio.create_task(run_DRT())

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
    
async def run_DRT():
    for i in range(10):
        await asyncio.sleep(10)
        await CLIENT.send("EXECUTE_VIBRATION")

async def main():
    server = await serve(server_code, "0.0.0.0", 8765)
    await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"[blue]Server stopped by keyboard interrupt[/blue]")