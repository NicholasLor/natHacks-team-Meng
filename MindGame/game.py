import pygame
import sys
from random import randint
import paho.mqtt.client as mqtt 

# display game runtime as score during gameplay
def display_score():
    current_time = int((pygame.time.get_ticks() - start_time)/100)
    time_surf = text_font.render("SCORE: " + f'{current_time}', False,(0,0,0))
    time_rect = time_surf.get_rect(center = (screen_width/5,screen_height/10))
    screen.blit(time_surf,time_rect)

# randomly generating enemy spawn
def obstacle_movement(obstacle_list):
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= enemy_vel
            screen.blit(enemy, obstacle_rect)
        obstacle_list = [obstacle for obstacle in obstacle_list if obstacle.x > -100]
        
        return obstacle_list
    else:
        return []

# controller for player and enemy collision, True will move game state to end game
def collision(player1, player2, obstacles):
    if obstacles:
        for obstacle_rect in obstacles:
            if player1.colliderect(obstacle_rect) or player2.colliderect(obstacle_rect):
                return True
    return False

pygame.init()

# SET UP GAME WINDOW
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

# player1 - create object and loads player 1 to the right
player1 = pygame.image.load('MindGame/graphics/brain_sprite_v1.png').convert_alpha()
player1_rect = player1.get_rect(midbottom = (250,ground_height))
player1_grav = 0
jump1 = False

# player2 - create object and loads player 2 to the left
player2 = pygame.image.load('MindGame/graphics/brain_sprite_v1.png').convert_alpha()
player2_rect = player2.get_rect(midbottom = (120,ground_height))
player2_grav = 0
jump2 = False

# enemy
enemy = pygame.image.load('MindGame/graphics/enemy_sprite.png').convert_alpha()
enemy_rect = enemy.get_rect(midbottom = (screen_width,ground_height))
enemy_pos = screen_width + 100
enemy_vel = 10

# populate obstacle list with enemy, at timer intervals
obstacle_rect_list = []
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1800)

# server for MUSE signal
mqttBroker = "test.mosquitto.org" 
port = 1883
try:
    client = mqtt.Client("Game")
    client.connect(mqttBroker, port)
    client.subscribe("Jump")
except:
    print("No connection to server")

# signal for player1 jump if using MUSE signal
eeg_signal = ''
counter = 0
def on_message(client, userdata, message):
    global eeg_signal
    eeg_signal = message.payload.decode("utf-8")

# access and subscribe to MUSE signal
client.loop_start()
client.subscribe("JUMP")

# game loop
while True:
    
    for event in pygame.event.get():
        #controller to quit game
        if event.type == pygame.QUIT:
            client.loop_stop
            pygame.quit()
            sys.exit()

        # controller for spawning two types of enemies
        if event.type == obstacle_timer and game_state == 1:
            if randint(0,2):    
                obstacle_rect_list.append(enemy.get_rect(midbottom = (randint(screen_width,screen_width*1.35),ground_height)))
            else:
                obstacle_rect_list.append(enemy.get_rect(midbottom = (randint(screen_width,screen_width*1.35),ground_height-150)))
        
    # game control for MUSE eeg signal, activates jump for player1
    client.on_message = on_message
    if(eeg_signal == "JUMP") and player1_rect.bottom >= ground_height:
        jump1 = True
        eeg_signal = ''
    # game control for keyboard play: player 1 via space key, player 2 via up key            
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and player1_rect.bottom >= ground_height:
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
        
        #load background
        screen.blit(background,(0,0))
        display_score()

        # set up player positions
        if jump1 == True:
            player1_grav = -25
        if jump2 == True:
            player2_grav = -25

        #player falls unless already on ground
        player1_grav += 1
        player1_rect.y += player1_grav
        if player1_rect.bottom >= ground_height:
            player1_rect.bottom = ground_height
        screen.blit(player1,player1_rect)

        player2_grav += 1
        player2_rect.y += player2_grav
        if player2_rect.bottom >= ground_height:
            player2_rect.bottom = ground_height
        screen.blit(player2,player2_rect)

        # set up enemy spawn
        obstacle_rect_list = obstacle_movement(obstacle_rect_list)

        # event for end game
        if(collision(player1_rect, player2_rect, obstacle_rect_list)):
            game_state = 2
            final_score = int((pygame.time.get_ticks() - start_time)/100)
            restart_timer = pygame.time.get_ticks() + 5000

    # end game screen
    elif(game_state == 2):
        screen.blit(background,(0,0))

        #resetting enemies and players
        obstacle_rect_list = []
        player1_rect.bottom = ground_height
        player2_rect.bottom = ground_height

        #displaying final score
        final_surf = text_font.render("FINAL SCORE: " + f'{final_score}', False,(0,0,0))
        final_rect = final_surf.get_rect(center = (screen_width/2,screen_height/2-100))
        screen.blit(final_surf,final_rect)

        #timer to restart
        if(restart_timer > pygame.time.get_ticks()):
            replay_surf = text_font.render("ABLE TO REPLAY IN: " + f'{int((restart_timer - pygame.time.get_ticks())/1000)}', False,(0,0,0))
        else:
            replay_surf = text_font.render("JUMP TO REPLAY", False,(0,0,0))
            # jump to restart
            if(jump1 == True or jump2 == True):
                game_state = 1
                start_time = pygame.time.get_ticks()
        replay_rect = final_surf.get_rect(center = (screen_width/2,screen_height/2))
        screen.blit(replay_surf,replay_rect)

    #updating display, setting tickrate
    pygame.display.update()
    clock.tick(60)

    #resetting jumps to False
    jump1 = False
    jump2 = False

    