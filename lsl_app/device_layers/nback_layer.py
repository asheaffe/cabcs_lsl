import pygame
import pylsl
import numpy as np

class NbackLayer:
    def __init__(self, stream_name="Nback", stream_type="Response", channel_count=9, sample_rate=0):
        self.info = pylsl.StreamInfo(
            name=stream_name,
            type=stream_type,
            channel_count=channel_count,
            nominal_srate=sample_rate,
            channel_format=pylsl.cf_float32,
            source_id="nback_app"
        )
        # self.response_map = {
        #     1: "YES",
        #     0: "NO",
        #     -1: "NO RESPONSE"
        # }

        # Define channel labels for the stream
        self.channel_labels = [
            "participant_id", "block_num",
            "trial_num", 
            #"symbol",
            "is_target", "response",
            "is_correct", "response_time"
            "raw_time", "n_level"
        ]

        self.outlet = pylsl.StreamOutlet(self.info)

    def send_sample(self, pid, results):
        # convert to full list for correct sample format
        full_sample = [pid, results["block"],
                       results["trial"],
                       #results["symbol"],
                       results["is_target"],
                       results["response"],
                       results["correct"],
                       results["response_time"],
                       results["raw_time"],
                       results["n_level"]]
        print(full_sample)
        self.outlet.push_sample(full_sample)

    # def send_marker(self, marker_value, time):  # ahhhhhhh probably need to get rid of this
    #     """Sends marker indicating the start of a block
        
    #     0: Start block
    #     1: Start jitter
    #     2: Button Press"""
    #     self.marker_dict = {0: "Start Block", 1: "Start Jitter", 2: "Button Press"}
    #     self.outlet.push_sample([marker_value, time])]

    # TODO: figure out how markers work and if I can replicate the above code in a global context