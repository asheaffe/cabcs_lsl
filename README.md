# Lab Streaming Layer Setup for CABCS Project

## Overview

This repository contains all of the code for setting up the Lab Streaming Layer (LSL) for multiple devices. Additionally, the project includes utilities for creating .fif (Functional Image File) files compatible with MNE NIRS analysis.

## Key Files

- **lsl_app.py**: The main inlet application for receiving device streams.
- **etg_layer.py**: Provides an LSL stream for SMI Eyetracker Glasses.
- **transform_xdf.py**: Processes .xdf files and creates .fif files to be used in MNE NIRS analysis.

## Prerequisites

- Python 3.7+
- OxySoft
- NIC2
- iView ETG SDK
- LabRecorder
- Required Python packages (listed in `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/cabcs_lsl.git
   cd cabcs_lsl
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Initial Setup

1. Open the Oxysoft and NIC2 applications and connect the fNIRS and EEG via bluetooth.
2. Ensure that the ETG glasses are connected via USB and start the iView ETG app to start running the server.
3. Start the Samsung watch and connect to the Localhost server
4. Open the MATB and Nback applications.
5. Run using Windows Powershell: ```python3 lsl_app/<device>_layer.py``` where ```<device>``` is replaced by the device name (i.e. etg, nback)
6. Run ```lsl_app.py```
7. Open LabRecorder and click **Update**.
   -   In the box under **Record from Streams** ensure that streams from all devices appear.
   -   Check that the **Study Root** leads to ```...\cabcs_lsl\lsl_app\data```
   -   If all devices appear in the box and the study root is the correct filepath, **Select All**

### Recording

1. In LabRecorder, select **Start** under **Recording Control**
2. Run the participant
3. In LabRecorder, select **Stop**
   - The .xdf files will automatically save to the data folder

### Data Processing

1. Using Windows Powershell run: ```python3.11 transform_xdf.py```
2. .fif files will populate in the corresponding device folders (i.e. eeg, fnirs, etg)

## Supported Devices

#### Natively Supported Devices

- Artinis fNIRS
- Enobio EEG

#### Non-Natively Supported Devices
_These devices require a layer which can be run using ```<device> _ layer.py```_

- SMI ETG glasses
- Samsung watch
