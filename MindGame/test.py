import pygame
import sys
import eeg_boiler

pygame.init

game_name = 'Mind Game'
screen_width = 1200
screen_height = 700
ground_height = 617

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption(game_name)

# set up eeg before pygame while loop
inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer = eeg_boiler.setup_eeg()

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # refresh jump boolean from run eeg func
        jump_boolean = eeg_boiler.run_eeg(inlet, fs, SHIFT_LENGTH, INDEX_CHANNEL, EPOCH_LENGTH, BUFFER_LENGTH, OVERLAP_LENGTH, eeg_buffer, filter_state, band_buffer)

        if jump_boolean:
            print("JUMP")