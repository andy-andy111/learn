import time, os
from pynput import keyboard
from game_logic import *

key_pressed=dict()

# width = 137
# height = 15
height = 50
width = 150

running = True
player=Player(1, (height//2) + 1)
bullets=Bullets(4)
opponents = Opponents(2, width, height-1)

def Create_bullet():
    global bullets
    global player
    bullets.shoot(player.x,player.y)

def on_press(key):
    global key_pressed
    key_pressed[key]=True

def on_release(key):
    global key_pressed
    del key_pressed[key]

def handle_key():
    global running
    global bullets
    global player
    global key_pressed

    for key in key_pressed:
        if key == keyboard.Key.up:
            player.move_up()
        elif key == keyboard.Key.down:
            player.move_down()
        elif key == keyboard.Key.left:
            player.move_left()
        elif key == keyboard.Key.right:
            player.move_right()
        elif key == keyboard.Key.space:
            bullets.shoot(player.x,player.y)
        elif key == keyboard.Key.esc:
            running = False

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

wall=Wall(width, height-1)
world=World(width, height)
title=Title(width//2, height-1, 'The Gunman VS. The Invaders')
world.addObject(bullets)
world.addObject(player)
world.addObject(wall)
world.addObject(opponents)
world.addObject(title)
world.addColliable(BulletsOpponentsCollidable(bullets, opponents))
world.addColliable(PlayerOpponentsCollidable(player, opponents, world))
world.addColliable(WallPlayerCollidable(wall,player))
world.addColliable(WallBulletsCollidable(wall,bullets))
world.addColliable(WallOpponentsCollidable(wall,opponents))

try:
    os.system('stty -echo')

    while running and world.stage=='running':
        handle_key()
        world.run()
        world.show()
        time.sleep(1./30.)
finally:
    os.system('stty echo')
