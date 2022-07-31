import pygame
import sys
from random import randint

from muselsl import stream, list_muses
import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop
from setuptools import setup  # Module to receive EEG data
import utils  # Our own utility functions


# Handy little enum to make code more readable
class Band:
    Delta = 0
    Theta = 1
    Alpha = 2
    Beta = 3


def display_score():
    current_time = int((pygame.time.get_ticks() - start_time)/100)
    time_surf = text_font.render("SCORE: " + f'{current_time}', False,(0,0,0))
    time_rect = time_surf.get_rect(center = (screen_width/5,screen_height/10))
    screen.blit(time_surf,time_rect)


def obstacle_movement(obstacle_list):
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= enemy_vel
            screen.blit(enemy, obstacle_rect)
        obstacle_list = [obstacle for obstacle in obstacle_list if obstacle.x > -100]
        
        return obstacle_list
    else:
        return []


def collision(player, obstacles):
    if obstacles:
        for obstacle_rect in obstacles:
            if player.colliderect(obstacle_rect):
                return 2
    return 1

pygame.init()

#Variables
game_name = 'Mind Game'
screen_width = 1200
screen_height = 700
ground_height = 617

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption(game_name)
clock = pygame.time.Clock()
text_font = pygame.font.Font('MindGame/font/Pixeltype.ttf',50)
start_time = 0

#game_state: 0-start screen 1-game 2-game over screen
game_state = 0

# adding menu
main_menu = pygame.image.load('MindGame/graphics/main_menu.png').convert_alpha()

# adding background
background = pygame.image.load('MindGame/graphics/background.png').convert_alpha()


# player1
player1 = pygame.image.load('MindGame/graphics/brain_sprite_v1.png').convert_alpha()
player1_rect = player1.get_rect(midbottom = (150,ground_height))
player1_grav = 0
jump1 = False

# player2
player2 = pygame.image.load('MindGame/graphics/brain_sprite_v1.png').convert_alpha()
player2_rect = player1.get_rect(midbottom = (200,ground_height))
player2_grav = 0
jump2 = False

# enemy
enemy = pygame.image.load('MindGame/graphics/enemy_sprite.png').convert_alpha()
enemy_rect = enemy.get_rect(midbottom = (screen_width,ground_height))
enemy_pos = screen_width + 100
enemy_vel = 10

obstacle_rect_list = []

# obstacle timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1200)


# game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == obstacle_timer and game_state == 1:
            obstacle_rect_list.append(enemy.get_rect(midbottom = (randint(screen_width,screen_width*1.3),ground_height)))
        
        # #TODO handling for eeg input
        # #will have to bring it out of the event loop

        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE and player1_rect.bottom >= ground_height:
        #         player1_grav = -25

               
    keys = pygame.key.get_pressed()
    if jump_boolean and player1_rect.bottom >= ground_height:
        jump1 = True
    if keys[pygame.K_UP] and player2_rect.bottom >= ground_height:
        jump2 = True

    # start screen
    if(game_state == 0):
        screen.blit(main_menu,(0,0))
        if jump1 == True:
            game_state = 1
            start_time = pygame.time.get_ticks()

    # game play screen
    elif(game_state == 1):
        
        screen.blit(background,(0,0))
        display_score()

        if jump1 == True:
            player1_grav = -25

        player1_grav += 1
        player1_rect.y += player1_grav
        if player1_rect.bottom >= ground_height:
            player1_rect.bottom = ground_height
        screen.blit(player1,player1_rect)

        # screen.blit(enemy,enemy_rect)
        # enemy_rect.left -= enemy_vel
        # if(enemy_rect.left <= -100):
        #     enemy_rect.left = screen_width + 100

        # obstacle movement
        obstacle_rect_list = obstacle_movement(obstacle_rect_list)

        game_state = collision(player1_rect, obstacle_rect_list)

        # if(player1_rect.colliderect(enemy_rect)):
        #     game_state = 2

    # end game screen
    elif(game_state == 2):
        screen.fill('white')
        obstacle_rect_list = []
        # enemy_rect.left = screen_width + 100
        if(jump1 == True):
            game_state = 1
            start_time = pygame.time.get_ticks()

    
    pygame.display.update()
    clock.tick(60)
    jump1 = False