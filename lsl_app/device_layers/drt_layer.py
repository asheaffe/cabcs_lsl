import sys
import time
import random
from pylsl import StreamInfo, StreamOutlet, local_clock
import pylsl as p
#import iViewNG  # Import the SMI iViewNG SDK

class DRT_layer:
    def __init__(self, stream_name="Detection-Response", stream_type="DRT"):
        
        self.info = p.StreamInfo(
            name = stream_name,
            type = stream_type,
            channel_count = 1,
            channel_format = p.cf_double64
        )

        # Define channel labels for the stream
        self.channel_labels = [
            "drt_marker"
        ]
        
        # Initialize LSL stream
        self.outlet = p.StreamOutlet(self.info)

    def send_sample(self, marker):
        self.outlet.push_sample([marker])

if __name__ == "__main__":
    # Create the ETG-LSL bridge
    layer = DRT_layer()
    #etg_lsl.pupil_dilation()
    
    print("Streaming DRT data to LSL...")
    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping...")