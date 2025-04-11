"""Example program to demonstrate how to read a multi-channel time-series
from LSL in a chunk-by-chunk manner (which is more efficient)."""

from pylsl import StreamInlet, resolve_byprop
import pylsl as p


def main():
    print("looking for streams...")
    streams = p.resolve_streams()

    # prob should store the inlets somehow but I don't wanna deal with this now lolol
    # inlets: List[Inlet] = []

    for info in streams:
        if info.type() == "Markers":
            if (
                info.nominal_srate() != p.IRREGULAR_RATE
                or info.channel_format() != p.cf_string
            ):
                print("Invalid marker stream " + info.name())
            print("Adding marker inlet: " + info.name())
            #inlets.append(info)
        elif (
            info.nominal_srate() != p.IRREGULAR_RATE
            and info.channel_format() != p.cf_string
        ):
            print("Adding data inlet: " + info.name())
            #inlets.append(info)

        else:
            print("Don't know what to do with stream " + info.name())

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    streams = resolve_byprop("type", "EEG")

    count = 0
    while True:
        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        # only print every 1000 chunks for visual purposes
        count += 1
        chunk, timestamps = inlet.pull_chunk()
        if count%1000 == 0 and timestamps:
            print("TIME: ", timestamps, " DATA: ", chunk)

# this works but output is not helpful/only streams EEG data
# def main():
#     # first resolve an EEG stream on the lab network
#     print("looking for an EEG stream...")
#     streams = resolve_byprop("type", "EEG")

#     # create a new inlet to read from the stream
#     inlet = StreamInlet(streams[0])

#     while True:
#         # get a new sample (you can also omit the timestamp part if you're not
#         # interested in it)
#         chunk, timestamps = inlet.pull_chunk()
#         if timestamps:
#             print(timestamps, chunk)


if __name__ == "__main__":
    main()