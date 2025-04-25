import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import re

# this is important for lab computer
site_packages = r'C:\Users\HCI\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.7_qbz5n2kfra8p0\LocalCache\local-packages\Python37\site-packages'
sys.path.append(site_packages)

import pyxdf
import mne

# TODO: This only reads in one file at a time. Is there a way to read in multiple .xdf files at once?
data, header = pyxdf.load_xdf("dummy_data/dummy1.xdf")

def PlotGraph(data):
    for stream in data:
        y = stream["time_series"]

        if isinstance(y, list):
            # list of strings, draw one vertical line for each marker
            for timestamp, marker in zip(stream["time_stamps"], y):
                plt.axvline(x=timestamp)
                print(f'Marker "{marker[0]}" @ {timestamp:.2f}s')
        elif isinstance(y, np.ndarray):
            # numeric data, draw as lines
            plt.plot(stream["time_stamps"], y)
        else:
            raise RuntimeError("Unknown stream format")

    plt.show()

def FindStream(data, stream_type):
    """
    Finds the data stream passed in stream_type (i.e. fNIRS, EEG, etc.)
    data: pyxdf data object
    stream_type: type of stream ('nirs', 'eeg', etc.) as used in LabRecorder
    """
    for i, stream in enumerate(data):
        print("STREAM TYPE: ", stream['info']['type'][0].lower())
        if stream_type in stream['info']['type'][0].lower():
            # return the stream if it exists
            return data[i]
    # else, return None
    return None

def ConvertEEG(data):
    # find EEG stream
    eeg_stream = FindStream(data, 'eeg')
    
    if eeg_stream is not None:
        data = eeg_stream["time_series"].T
    else:
        print("EEG stream data not found")
        return None
    
    # sampling frequency
    sfreq = float(eeg_stream["info"]["nominal_srate"][0])

    cnames = [f"EEG{i+1}" for i in range(data.shape[0])]
    ctypes = ["eeg"] * data.shape[0]

    # mne info object
    info = mne.create_info(cnames, sfreq, ctypes)

    # raw object
    raw = mne.io.RawArray(data, info)

    return raw

def ConvertfNIRS(data):
    # find fNIRS stream if index isn't provided
    # TODO: check that 'nirs' is the right type keyword
    fnirs_stream = FindStream(data, 'nirs')
    
    if fnirs_stream is not None:
        data = fnirs_stream["time_series"].T
    else:
        print("fNIRS stream data not found")
        return None

    # extract data
    time_series = fnirs_stream['time_series']

    sfreq = float(fnirs_stream['info']['nominal_srate'][0])

    channel_num = time_series.shape[0]
    cnames = [f"S-D{i//2+1}_{['hbo', 'hbr'][i%2]}" for i in range(channel_num)]
    ctypes = ["fnirs_fd_phase"] * channel_num

    # mne info object
    info = mne.create_info(cnames, sfreq, ctypes)

    raw = mne.io.RawArray(time_series, info)

    #snirf = mne.io.read_raw_snirf()

    return raw

def create_file(folder_path):
    """Creates a new file to write data to

    device: type of device used to measure (i.e. eeg, fnirs, etc.)"""
    files = os.listdir(folder_path)   # change this with real data
    prefix = "data_"

    pattern = re.compile(f"^{prefix}(\\d+).*$")
    matching_files = [f for f in files if pattern.match(f)]

    # Find the highest number
    max_num = 0
    for file in matching_files:
        match = pattern.match(file)
        if match:
            num = int(match.group(1))
            max_num = max(max_num, num)
    
    # Create the new file name with incremented number
    new_num = max_num + 1
    new_filename = f"{prefix}{str(new_num)}"
    new_filepath = os.path.join(folder_path, new_filename)

    with open(new_filepath, 'w') as file:
        file.write(f"{new_filename} created!")
    
    print(f"{new_filename} created!")

    return new_filepath

def write_data(filepath, data):
    with open(filepath, 'w') as file:
        for line in data:
            file.write(f"{line[0]}\t{line[1]}")

    print("data written to ", filepath)

def main():
    ConvertEEG(data)
    fnirs_data = ConvertfNIRS(data) 
    #create_file("dummy_data")
    filepath = os.path.join("dummy_data", "data_1")
    write_data(filepath, fnirs_data)
    #print(FindStream(data, 'eeg'))

if __name__ == "__main__":
    main()