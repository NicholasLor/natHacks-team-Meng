from muselsl import stream, list_muses
import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop
from setuptools import setup  # Module to receive EEG data
import utils  # Our own utility functions
from playsound import playsound
import os
import datetime
import time
import paho.mqtt.client as paho


def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))

# client.connect("broker.mqttdashboard.com", 1883)
#client.connect("https://test.mosquitto.org/", 8883)
def on_publish(client, userdata, mid):
    print("JUMP: "+str(mid))
 



# Handy little enum to make code more readable
class Band:
    Delta = 0
    Theta = 1
    Alpha = 2
    Beta = 3

# looks for Muse device and creates connection
def setup_eeg():
    """ EXPERIMENTAL PARAMETERS """
    # Modify these to change aspects of the signal processing

    # Length of the EEG data buffer (in seconds)
    # This buffer will hold last n seconds of data and be used for calculations
    BUFFER_LENGTH = 2

    # Length of the epochs used to compute the FFT (in seconds)
    EPOCH_LENGTH = 1

    # Amount of overlap between two consecutive epochs (in seconds)
    OVERLAP_LENGTH = 0.50

    # Amount to 'shift' the start of each next consecutive epoch
    SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH

    # Index of the channel(s) (electrodes) to be used
    # 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
    INDEX_CHANNEL = [0]

    # if __name__ == "__main__":


    """ 1. CONNECT TO EEG STREAM """

    # Search for active LSL streams
    print('Looking for an EEG stream...')
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) == 0:
        raise RuntimeError('Can\'t find EEG stream.')

    # Set active EEG stream to inlet and apply time correction
    print("Start acquiring data")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    #eeg_time_correction = inlet.time_correction()

    # Get the stream info and description
    info = inlet.info()
    description = info.desc()

    # Get the sampling frequency
    # This is an important value that represents how many EEG data points are
    # collected in a second. This influences our frequency band calculation.
    # for the Muse 2016, this should always be 256
    fs = int(info.nominal_srate())

    """ 2. INITIALIZE BUFFERS """

    # Initialize raw EEG data buffer
    eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), 1))
    filter_state = None  # for use with the notch filter

    # Compute the number of epochs in "buffer_length"
    #n_win_test = int(np.floor((BUFFER_LENGTH - EPOCH_LENGTH) /
                            #SHIFT_LENGTH + 1))

    # Initialize the band power buffer (for plotting)
    # bands will be ordered: [delta, theta, alpha, beta]
    #band_buffer = np.zeros((n_win_test, 4))

    """ 3. GET DATA """

    # The try/except structure allows to quit the while loop by aborting the
    # script with <Ctrl-C>
    print('Press Ctrl-C in the console to break the while loop.')

    return inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state

# returns jump_boolean that can be continuously called in while loop
def run_eeg(inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state):

    try:

        #MQTT CONNECTION PART outside loop
        
        client = paho.Client()
        client.on_connect = on_connect
        client = paho.Client()
        client.on_publish = on_publish
        client.connect("test.mosquitto.org", 1883)
        client.loop_start()


        # The following loop acquires data, computes band powers, and calculates neurofeedback metrics based on those band powers
        while True:


            """ 3.1 ACQUIRE DATA """
            # Obtain EEG data from the LSL stream
            eeg_data, timestamp = inlet.pull_chunk(
                timeout=1, max_samples=int(SHIFT_LENGTH * fs))
                #timeout=1, max_samples=int(1))
                #fs is 256
                #shift length is 0.05 right now 

            # Only keep the channel we're interested in
            ch_data = np.array(eeg_data)[:, INDEX_CHANNEL]
            # print(ch_data.shape)



            # jump_boolean = False

            min_val = np.min(ch_data)
            max_val = np.max(ch_data)
            
            jump_boolean = False

            if min_val < -250 or max_val > 250:
                jump_boolean = True
                #MQTT PART WITHIN THE LOOP 
                                #1st thing is the channel name
                client.publish("JUMP", "JUMP")
                time.sleep(0.2)


            # for debugging
            #print(max_val)


            #MQTT PUBLISHING PART 
            #return jump_boolean

    except KeyboardInterrupt:
        print('Closing!')

inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state = setup_eeg()

run_eeg(inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state)



### BOILER PLATE CODE BELOW: COPY INTO YOUR PROGRAM AND IMPLEMENT AS YOU WISH

# # ---------- sets up eeg before pygame while loop ------------
# inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer = eeg_boiler.setup_eeg()

# # ---------- call jump_boolean func -------------------
# jump_boolean = eeg_boiler.run_eeg(inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer)

