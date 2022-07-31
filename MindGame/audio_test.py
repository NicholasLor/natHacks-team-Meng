import eeg_boiler
import os
import sys

# set up eeg before pygame while loop
inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer = eeg_boiler.setup_eeg()

# get path of audio file to play
dir_path = os.path.dirname(os.path.realpath(__file__))
sound_path = os.path.join(dir_path, 'trapshit.wav')

try:
    while True:

        # call jump boolean func
        jump_boolean = eeg_boiler.run_eeg(inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer)
        
        if (jump_boolean):

            # play sound
            print("REAL TRAP SHIT")
            os.system('afplay "{}"'.format(sound_path))

except KeyboardInterrupt:
    print('Closing!')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


# print(muses)
# Note: Streaming is synchronous, so code here will not execute until after the stream has been closed
print('Stream has ended')