import pygame
import pylsl
import time
import numpy as np

class NbackLayer:
    def __init__(self, stream_name="Nback", stream_type="Response", channel_count=2, sample_rate=0):
        self.info = pylsl.StreamInfo(
            name=stream_name,
            type=stream_type,
            channel_count=channel_count,
            nominal_srate=sample_rate,
            channel_format=pylsl.cf_float32,
            source_id="nback_app"
        )

        # Define channel labels for the stream
        self.channel_labels = [
            "sample",
            "marker"
        ]

        self.outlet = pylsl.StreamOutlet(self.info)

    def send_sample(self, data):
        if isinstance(data, (int, float)):
            data = [data]
        self.outlet.push_sample(data)

    def send_marker(self, marker_value):
        """Sends marker indicating the start of a block
        
        0: Start block
        1: Start jitter"""
        self.marker_dict = {0: "Start Block", 1: "Start Jitter"}
        self.outlet.push_sample([marker_value])