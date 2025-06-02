import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import re
import glob
from datetime import datetime, timezone, timedelta

# this is important for lab computer
site_packages = r'C:\Users\HCI\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.7_qbz5n2kfra8p0\LocalCache\local-packages\Python37\site-packages'
sys.path.append(site_packages)

import pyxdf
import mne

# TODO: After reading in xdf file move to another location (to indicate it has already been read)
FILEPATTERN = "dummy_data/*.xdf"
ID_TO_STREAM = {}
file_paths = glob.glob(FILEPATTERN)

if not file_paths:
    raise ValueError(f"No files matching pattern: {FILEPATTERN}")

for i, path in enumerate(file_paths):
    print(f"Loading file: {path}")
    data, header = pyxdf.load_xdf(path)

    ID_TO_STREAM[i] = (data, header)

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

def ConvertEEG(data_dict, pid):
    """Converts EEG data to a .fif file

    :param data_dict: dictionary of data read in with pid
    :param pid: id num of the data being read
    :return: raw data
    """
    # find EEG stream
    eeg_stream = FindStream(data_dict[pid][0], 'eeg')
    
    if eeg_stream is not None:
        data = eeg_stream["time_series"]

        if len(data) == 0:
            print("Warning: EEG time series is empty. No EEG file created.")
            return None
    else:
        print("EEG stream data not found")
        return None
    
    channel_num = int(eeg_stream['info']['channel_count'][0])
    #print(len(data), ", ", len(eeg_stream["time_series"]))

    # sampling frequency
    sfreq = float(eeg_stream["info"]["nominal_srate"][0])

    cnames = [f"EEG{i+1}" for i in range(channel_num)]
    ctypes = ["eeg"] * channel_num

    # mne info object
    info = mne.create_info(cnames, sfreq, ctypes)
    
    # raw object
    raw = mne.io.RawArray(data, info)

    # only save if there is data
    if raw.n_times > 0:
        # create a filepath for .fif file
        directory = FILEPATTERN.split("/")[0]
        filepath = f"{directory}/eeg/{pid}_eeg.fif"

        if not os.path.exists(filepath):
            os.makedirs(f"{directory}/eeg")
            print("EEG directory created.")
        
        # save as a .fif file
        raw.save(filepath, overwrite=True)

        print(f"Saved EEG data to {filepath}!")
    
    else:
        print("Cannot save Raw object with zero time points.")

    return raw

def ConvertfNIRS(data_dict, pid):
    """Converts fNIRS data to a .fif file

    :param data_dict: dictionary of data read in with pid
    :param pid: id num for the data being read
    :return: raw data
    """
    # find fNIRS stream if index isn't provided
    fnirs_stream = FindStream(data_dict[pid][0], 'nirs')
    
    if fnirs_stream is not None:
        data = fnirs_stream["time_series"].T
    else:
        print("fNIRS stream data not found")
        return None

    sfreq = float(fnirs_stream['info']['nominal_srate'][0])

    channel_num = data.shape[0]
    cnames = [f"S-D{i//2+1}_{['hbo', 'hbr'][i%2]}" for i in range(channel_num)]
    ctypes = ["fnirs_cw_amplitude"] * channel_num

    # mne info object
    info = mne.create_info(cnames, sfreq, ctypes)

    raw = mne.io.RawArray(data, info)
    
    # create a filepath for .fif file
    directory = FILEPATTERN.split("/")[0]
    filepath = f"{directory}/fnirs/{pid}_fnirs_raw.fif"

    if not os.path.exists(directory):
        os.makedirs(f"{directory}/fnirs")
        print("fNIRS directory created.")
    
    # save as a .fif file
    raw.save(filepath, overwrite=True)
    
    return raw

def ConvertETG(data_dict, pid):
    """Calculates Pupil Dilation and saves to .fif file (?)
    
    :param data_dict: dictionary of data read in with pid
    :param pid: id num for the data being read
    :return: raw data"""
    etg = FindStream(data_dict[pid][0], "gaze")
    print()
    
    if etg is not None:
        data = etg['time_series'].T
    else:
        print(f"ETG stream data not found. File ID: {pid}")
        return None
    
    # ik this is ugly i just dont care
    # PupilDiameter_Left is the fourth channel
    #left = data['info']['PupilDiameter_Left']

    left = data[6]
    right = data[7]

    print(f"Mean left eye diameter: {np.mean(left)}")
    print(f"Mean right eye diameter: {np.mean(right)}")

def see_data(raw_data):
    """Takes an MNE-Python Raw object and prints the important info for easier debugging"""
    data, times = raw_data[:, :]

    print(f"Time points: {times[:10]}...")
    print(f"Data shape: {data.shape}")

    # for i, ch_name in enumerate(raw_data.ch_names):
    #     print(f"Channel {ch_name}: {data[i, :5]}...")

def print_data(pid, stype, data_dict=ID_TO_STREAM):
    """Just prints raw data for debugging purposes
    
    :param files: dictionary with id mapped to data from file
    :param id: current id to read data from
    :param type: stream type (i.e. gaze, nirs, response)"""
    data = FindStream(data_dict[pid][0], stype)
    print()
    
    if data is not None:
        data = data['time_series'].T
    else:
        print(f"{stype} stream data not found. File ID: {pid}")
        return None
    
    print(data)

def create_file(folder_path, data_dict):
    """Creates a new file to write data to for each file read in

    folder_path: directory to create a file in"""
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
    
    # Create the new file name with incremented number for each file read in
    for i in range(len(data_dict)):
        pid = max_num + 1
        new_filename = f"{prefix}{str(pid)}"
        new_filepath = os.path.join(folder_path, new_filename)

        with open(new_filepath, 'w') as file:
            file.write(f"{new_filename} created!")
        
        print(f"{new_filename} created!")

        max_num += 1

    # return the number of data files created
    return len(data_dict)

def clear_data_files(folder_path):
    """Debugging function for clearing all data files during testing
    
    :folder_path: str path to folder containing files to delete
    :return: int number of files deleted, else None"""

    # first check if the file path exists
    if not os.path.exists(folder_path):
        print(f"Folder doesn't exist: {folder_path}")
        return None
    
    # get all files in the folder
    files = os.listdir(folder_path)   # change this with real data
    prefix = "data_"

    # regex matching files with "data_#"
    pattern = re.compile(f"^{prefix}(\\d+).*$")
    matching_files = [f for f in files if pattern.match(f)]

    # delete each matching file
    count = 0
    for file in matching_files:
        filepath = os.path.join(folder_path, file)
        try:
            # make sure it's a file
            if os.path.isfile(filepath):
                os.remove(filepath)
                count += 1
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")

    return count

def clear_fnirs_eeg(folder_path, type):
    """Debugging function for clearing fnirs/eeg fif files
    
    :param folder_path: str path to directory from which to delete files
    :param type: str either eeg or fnirs
    :return: count number of files deleted"""

    # first check if the file path exists
    if not os.path.exists(folder_path):
        print(f"Folder doesn't exist: {folder_path}")
        return None
    
    # get all files in the folder
    files = os.listdir(folder_path)   # change this with real data

    temp = folder_path.split("/")[1]

    if type == "eeg":
        temp = "_eeg.fif"
    if type == "fnirs":
        temp = "_fnirs_raw.fif"
    else:
        print(f"{temp} is not a valid file type")
        return None

    # regex matching files with "data_#"
    pattern = re.compile(f"(\\d+){temp}")
    matching_files = [f for f in files if pattern.match(f)]

    # delete each matching file
    count = 0
    for file in matching_files:
        filepath = os.path.join(folder_path, file)
        try:
            # make sure it's a file
            if os.path.isfile(filepath):
                os.remove(filepath)
                count += 1
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")

    return count

def write_data(filepath, data):
    with open(filepath, 'w') as file:
        for line in data:
            file.write(f"{line[0]}\t{line[1]}")

    print("data written to ", filepath)

# TODO: Other stream types [quality, markers, gaze] should have some kind of processing as well

def main():
    #ConvertEEG(data)
    
    num_files = create_file("dummy_data", ID_TO_STREAM)
    print(ID_TO_STREAM.keys())
    print_data(2, "response")
    # for id in range(num_files):
    #     #ConvertEEG(ID_TO_STREAM, id)
    #     #ConvertfNIRS(ID_TO_STREAM, id)
    #     ConvertETG(ID_TO_STREAM, id)

    #print(ID_TO_STREAM)
    clear_data_files("dummy_data")
    # clear_fnirs_eeg("dummy_data/fnirs", "fnirs")
    #clear_fnirs_eeg("dummy_data/eeg", "eeg")

if __name__ == "__main__":
    main()