import matplotlib.pyplot as plt
import numpy as np

import pyxdf
import mne

# TODO: This only reads in one file at a time. Is there a way to read in multiple .xdf files at once?
data, header = pyxdf.load_xdf("lsl_app/test.xdf")

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
        data = eeg_stream["time_series"].T
    else:
        print("fNIRS stream data not found")
        return None

    # extract data
    time_series = fnirs_stream['time_series']

    sfreq = float(fnirs_stream['info']['nominal_srate'][0])

    channel_num = time_series.shape[0]
    cnames = [f"S-D{i//2+1}_{['hbo', 'hbr'][i%2]}" for i in range(channel_num)]
    ctypes = ["nirs"] * channel_num

    # mne info object
    info = mne.create_info(cnames, sfreq, ctypes)

    raw = mne.io.RawArray(time_series, info)

    return raw

def main():
    ConvertEEG(data)
    ConvertfNIRS(data) 
    #print(FindStream(data, 'eeg'))

if __name__ == "__main__":
    main()