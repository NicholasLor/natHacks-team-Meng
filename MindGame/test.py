import pygame
import sys
from muselsl import stream, list_muses
import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop
from setuptools import setup  # Module to receive EEG data
import utils  # Our own utility functions
# from playsound import playsound
# import os

pygame.init

game_name = 'Mind Game'
screen_width = 1200
screen_height = 700
ground_height = 617

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption(game_name)


def setup_eeg():
    """ EXPERIMENTAL PARAMETERS """
    # Modify these to change aspects of the signal processing

    # Length of the EEG data buffer (in seconds)
    # This buffer will hold last n seconds of data and be used for calculations
    BUFFER_LENGTH = 1

    # Length of the epochs used to compute the FFT (in seconds)
    EPOCH_LENGTH = 1

    # Amount of overlap between two consecutive epochs (in seconds)
    OVERLAP_LENGTH = 0.8

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
    eeg_time_correction = inlet.time_correction()

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
    n_win_test = int(np.floor((BUFFER_LENGTH - EPOCH_LENGTH) /
                            SHIFT_LENGTH + 1))

    # Initialize the band power buffer (for plotting)
    # bands will be ordered: [delta, theta, alpha, beta]
    band_buffer = np.zeros((n_win_test, 4))

    """ 3. GET DATA """

    # The try/except structure allows to quit the while loop by aborting the
    # script with <Ctrl-C>
    print('Press Ctrl-C in the console to break the while loop.')

    return inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer

def run_eeg(inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer):

    try:
        # The following loop acquires data, computes band powers, and calculates neurofeedback metrics based on those band powers
        # while True:

            """ 3.1 ACQUIRE DATA """
            # Obtain EEG data from the LSL stream
            eeg_data, timestamp = inlet.pull_chunk(
                timeout=1, max_samples=int(SHIFT_LENGTH * fs))

            # Only keep the channel we're interested in
            ch_data = np.array(eeg_data)[:, INDEX_CHANNEL]
            # print(ch_data.shape)

            # Update EEG buffer with the new data
            eeg_buffer, filter_state = utils.update_buffer(
                eeg_buffer, ch_data, notch=True,
                filter_state=filter_state)

            """ 3.2 COMPUTE BAND POWERS """
            # Get newest samples from the buffer
            data_epoch = utils.get_last_data(eeg_buffer,
                                            EPOCH_LENGTH * fs)

            # Compute band powers
            
            band_powers = utils.compute_band_powers(data_epoch, fs)
            band_buffer, _ = utils.update_buffer(band_buffer,
                                                np.asarray([band_powers]))

            # TODO print band power function to pandas csv
            

            # Compute the average band powers for all epochs in buffer
            # This helps to smooth out noise
            smooth_band_powers = np.mean(band_buffer, axis=0)

            # convert band power float to integer for terminal graph
            # new_array = np.multiply(band_powers,10)
            # band_power_int = new_array.astype(np.int)
            
            # print method with numbers
            # print('Delta: ', np.format_float_positional(band_powers[Band.Delta],precision=3),'|',band_power_int[Band.Delta]*"░")
            # print('Theta: ', np.format_float_positional(band_powers[Band.Theta],precision=3),"|",band_power_int[Band.Theta]*"░")
            # print('Alpha: ', np.format_float_positional(band_powers[Band.Alpha],precision=3),"|",band_power_int[Band.Theta]*"░")
            # print('Beta: ', np.format_float_positional(band_powers[Band.Beta],precision=3),"|",band_power_int[Band.Theta]*"░")
            # print("----------------------")

            # delta_band_str = band_power_int[Band.Delta]*"░"
            # theta_band_str = band_power_int[Band.Theta]*"░"
            # alpha_band_str = band_power_int[Band.Alpha]*"░"
            # beta_band_str = band_power_int[Band.Beta]*"░"

            # print method without numbers
            # print("********* RATCHET-ASS Terminal EEG Visualizer *********")
            # print('\n')
            # print(band_powers.shape)
            # print('Delta: ',len(delta_band_str)," ",delta_band_str)
            # print('Theta: ',len(theta_band_str)," ",theta_band_str)
            # print('Alpha: ',len(alpha_band_str)," ",alpha_band_str)
            # print('Beta : ',len(beta_band_str)," ",beta_band_str)
            # print('\n')

            # jump_boolean = False

            # if(len(delta_band_str)>5):
            #     jump_boolean = True
            #     # print("Jump: True")
            
            # print(jump_boolean)


            # print("--------------")
            # print(ch_data)
            # print("--------------")
            max_val = np.min(ch_data)
            
            jump_boolean = False

            if max_val < -250:
                jump_boolean = True
            
            return jump_boolean
            


            """ 3.3 COMPUTE NEUROFEEDBACK METRICS """
            # These metrics could also be used to drive brain-computer interfaces

            # Alpha Protocol:
            # Simple redout of alpha power, divided by delta waves in order to rule out noise
            # alpha_metric = smooth_band_powers[Band.Alpha] / \
            #     smooth_band_powers[Band.Delta]
            # #print('Alpha Relaxation: ', alpha_metric)

            # Beta Protocol:
            # Beta waves have been used as a measure of mental activity and concentration
            # This beta over theta ratio is commonly used as neurofeedback for ADHD
            # beta_metric = smooth_band_powers[Band.Beta] / \
            #     smooth_band_powers[Band.Theta]
            # print('Beta Concentration: ', beta_metric)

            # Alpha/Theta Protocol:
            # This is another popular neurofeedback metric for stress reduction
            # Higher theta over alpha is supposedly associated with reduced anxiety
            # theta_metric = smooth_band_powers[Band.Theta] / \
            #     smooth_band_powers[Band.Alpha]
            # print('Theta Relaxation: ', theta_metric)

    except KeyboardInterrupt:
        print('Closing!')

# set up eeg before pygame while loop
inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer = setup_eeg()


while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # refresh jump boolean from run eeg func
        jump_boolean = run_eeg(inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer)

        if jump_boolean:
            print("JUMP")