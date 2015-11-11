from cave import Cave
import matplotlib.path as path
import numpy as np
import pdb
import pygame
from pygame.locals import *
import random
from sprites import *
import time


EXPLOSION_IMG = 'explosion.png'
HELICOPTER_IMG = 'helicopter3.png'
OBSTACLE_IMG = 'obstacle4.png'
OBSTACLE_HEIGHT = 100
OBSTACLE_SPAWN_RATE = 1.0
CAVE_HEIGHT = 300

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
BG_COLOR = (30, 50, 25)


""" Initialize Game Area """
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
clock = pygame.time.Clock()

cave = Cave(screen, CAVE_HEIGHT)

heli = HelicopterSprite(HELICOPTER_IMG, (250, SCREEN_HEIGHT / 2))
heli_group = pygame.sprite.RenderPlain(heli)

obstacles = pygame.sprite.LayeredUpdates()
next_spawn = time.time()

""" Helper methods """
def spawn_obstacle(obstacles, y_min, y_max):
	obstacle = ObstacleSprite(OBSTACLE_IMG, y_min, y_max, SCREEN_WIDTH + SCREEN_WIDTH / 2)
	obstacles.add(obstacle)

""" Main Game Loop """
while True:
	delta_ms = clock.tick(60)

	# Process user interaction
	for event in pygame.event.get():
		if event.type == MOUSEBUTTONDOWN:
			heli.throttle = True
		elif event.type == MOUSEBUTTONUP:
			heli.throttle = False

		if not hasattr(event, 'key'): 
			continue
		elif event.key == K_SPACE:
			BG_COLOR = (
				random.randint(1, 255),
				random.randint(1, 255),
				random.randint(1, 255)
			)

	# Update game state and redraw screen
	screen.fill(BG_COLOR)

	if next_spawn <= time.time():
		midpoint = cave.sample_midpoint()
		spawn_obstacle(obstacles, midpoint[1] + OBSTACLE_HEIGHT / 2, midpoint[1] + CAVE_HEIGHT - OBSTACLE_HEIGHT / 2)
		next_spawn = time.time() + OBSTACLE_SPAWN_RATE

	heli_group.update(delta_ms)
	obstacles.update(delta_ms)
	cave.update()

	cave.check_collision(heli_group)

	for obstacle in obstacles.sprites():
		for heli in heli_group.sprites():
			if pygame.sprite.collide_rect(heli, obstacle):
				heli.image = pygame.image.load(EXPLOSION_IMG)

	obstacles.draw(screen)
	heli_group.draw(screen)

	# Remove reference to obstacle once it falls off screen
	if len(obstacles.sprites()) > 0:
		oldest_obstacle = obstacles.get_sprite(0)

		if oldest_obstacle.position[0] < 0:
			obstacles.remove(oldest_obstacle)

	pygame.display.flip()
