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

    def send_sample(self, marker, is_practice):

        if is_practice:
            return
        
        # convert to full list for correct sample format
        marker_codes = {
            "0/STANDING/START_BLOCK": 100,
            "1/STANDING/START_BLOCK": 101,
            "2/STANDING/START_BLOCK": 102,            
            "0/WALKING/START_BLOCK": 103,
            "1/WALKING/START_BLOCK": 104,
            "2/WALKING/START_BLOCK": 105,
            
            "0/STANDING/IS_TARGET": 106,
            "0/STANDING/NOT_TARGET": 107,
            "1/STANDING/IS_TARGET": 108,
            "1/STANDING/NOT_TARGET": 109,
            "2/STANDING/IS_TARGET": 110,
            "2/STANDING/NOT_TARGET": 111,

            "0/WALKING/IS_TARGET": 112,
            "0/WALKING/NOT_TARGET": 113,
            "1/WALKING/IS_TARGET": 114,
            "1/WALKING/NOT_TARGET": 115,
            "2/WALKING/IS_TARGET": 116,
            "2/WALKING/NOT_TARGET": 117,

            "0/STANDING/RESPONSE/A": 150,
            "0/STANDING/RESPONSE/B": 151,
            "1/STANDING/RESPONSE/A": 152,
            "1/STANDING/RESPONSE/B": 153,
            "2/STANDING/RESPONSE/A": 154,
            "2/STANDING/RESPONSE/B": 155,
            
            "0/STANDING/RESPONSE/A": 156,
            "0/STANDING/RESPONSE/B": 157,
            "1/STANDING/RESPONSE/A": 158,
            "1/STANDING/RESPONSE/B": 159,
            "2/STANDING/RESPONSE/A": 160,
            "2/STANDING/RESPONSE/B": 161,
            
            "0/STANDING/DRT_STIM": 170,
            "1/STANDING/DRT_STIM": 171,
            "2/STANDING/DRT_STIM": 172,
            "0/WALKING/DRT_STIM": 173,
            "1/WALKING/DRT_STIM": 174,
            "2/WALKING/DRT_STIM": 175,

            "0/STANDING/DRT_RESPONSE": 180,
            "1/STANDING/DRT_RESPONSE": 181,
            "2/STANDING/DRT_RESPONSE": 182,
            "0/WALKING/DRT_RESPONSE": 183,
            "1/WALKING/DRT_RESPONSE": 184,
            "2/WALKING/DRT_RESPONSE": 185,  

            "0/STANDING/REST": 190,
            "1/STANDING/REST": 191,
            "2/STANDING/REST": 192,
            "0/WALKING/REST": 193,
            "1/WALKING/REST": 194,
            "2/WALKING/REST": 195,   

            "0/STANDING/INSTRUCTION": 196,
            "1/STANDING/INSTRUCTION": 197,
            "2/STANDING/INSTRUCTION": 198,
            "0/WALKING/INSTRUCTION": 199,
            "1/WALKING/INSTRUCTION": 200,
            "2/WALKING/INSTRUCTION": 201,       
        }
        
        self.outlet.push_sample([marker_codes[marker]])

# if __name__ == "__main__":
#     layer = NbackLayer()

#     try:
#         while True:
#             time.sleep(1)
            
#     except KeyboardInterrupt:
#         print("Stopping...")