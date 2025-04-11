"""
SMI ETG to LSL Integration (base code from Claude)
--------------------------
This code creates an LSL outlet that streams eye tracking data from SMI Eye Tracking Glasses.
Requirements:
- pylsl (Lab Streaming Layer for Python)
- iViewNG SDK (SMI's Python API)
"""
import sys
import time
import random
from pylsl import StreamInfo, StreamOutlet, local_clock
import pylsl as p
#import iViewNG  # Import the SMI iViewNG SDK

class SMI_ETG:
    def __init__(self, stream_name="SMI_ETG_EyeTracker", stream_type="Gaze"):
        """Initialize the SMI ETG to LSL interface"""
        self.connected = False
        self.outlet = None
        
        # Define LSL stream parameters
        self.stream_name = stream_name
        self.stream_type = stream_type
        self.channel_count = 8  # x, y for each eye + pupil diameter + additional data
        self.channel_format = 'float32'
        self.sampling_rate = 120  # Typical SMI ETG sampling rate (adjust as needed)
        
        # Define channel labels for the stream
        self.channel_labels = [
            "GazeX_Left", "GazeY_Left", 
            "GazeX_Right", "GazeY_Right",
            "PupilDiameter_Left", "PupilDiameter_Right",
            "Confidence_Left", "Confidence_Right"
        ]
        
        # Initialize LSL stream
        self.initialize_lsl()

    def initialize_lsl(self):
        """Initialize the LSL outlet for streaming eye tracking data"""
        try:
            # Create a new StreamInfo and outlet
            self.info = StreamInfo(
                name=self.stream_name,
                type=self.stream_type,
                channel_count=self.channel_count,
                nominal_srate=self.sampling_rate,
                channel_format=self.channel_format,
                source_id='smi_etg_001'  # Unique identifier for this device
            )
            
            # Add channel metadata
            channels = self.info.desc().append_child("channels")
            for label in self.channel_labels:
                channels.append_child("channel").append_child_value("label", label)
                
            # Create the outlet, this makes the stream discoverable
            self.outlet = StreamOutlet(self.info)

            # stream name: SMI_EyeTracker
            print(f"LSL outlet '{self.stream_name}' created successfully.")
            
        except Exception as e:
            print(f"Error creating LSL outlet: {e}")
            sys.exit(1)

    def on_gaze_data(self, data):
        """Collect data to push to stream"""
        try:
            # https://github.com/chkothe/pylsl/blob/master/examples/SendDataAdvanced.py
            sample = [random.random(), random.random(), random.random(), random.random(),
                      random.random(), random.random(), random.random(), random.random()]
            timestamp = local_clock()-0.125     # samples actually 125ms old
            self.outlet.push_sample(sample, timestamp)
            
        except Exception as e:
            print(f"Error in processing gaze data: {e}")

# Example usage
if __name__ == "__main__":
    # Create the ETG-LSL bridge
    etg_lsl = SMI_ETG(stream_name="SMI_EyeTracker", stream_type="Gaze")
    
    print("Streaming eye tracking data to LSL. Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping...")