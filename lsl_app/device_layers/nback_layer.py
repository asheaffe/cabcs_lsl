import pygame
import pylsl
import numpy as np
import time

class NbackLayer:
    def __init__(self, stream_name="Nback", stream_type="Response", channel_count=1):
        self.info = pylsl.StreamInfo(
            name=stream_name,
            type=stream_type,
            channel_count=channel_count,
            channel_format=pylsl.cf_double64,
            source_id="nback_app"
        )

        # Define channel labels for the stream
        self.channel_labels = [
            "nback_marker"
        ]

        self.outlet = pylsl.StreamOutlet(self.info)

    def send_sample(self, marker):
        # convert to full list for correct sample format
        marker_codes = {
            "0/START": 100,
            "0/YES": 101,
            "0/NO": 102,
            "1/START": 110,
            "1/YES": 111,
            "1/NO": 112,
            "2/START": 120,
            "2/YES": 121,
            "2/NO": 122
        }
        
        self.outlet.push_sample([marker_codes[marker]])

if __name__ == "__main__":
    layer = NbackLayer()

    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping...")