import matplotlib.path as path
import numpy as np
import pdb
import pygame
from pygame.locals import *
import random
import time


EXPLOSION_IMG = 'explosion.png'
HELICOPTER_IMG = 'helicopter3.png'
OBSTACLE_IMG = 'obstacle4.png'
OBSTACLE_HEIGHT = 100
OBSTACLE_SPAWN_RATE = 3.0
CAVE_HEIGHT = 300

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
BG_COLOR = (30, 50, 25)

class HelicopterSprite(pygame.sprite.Sprite):
	MAX_VERTICAL_SPEED = 5.0
	MIN_VERTICAL_SPEED = -10.0

	ROTORS = -1.0
	GRAVITY = 2.5

	def __init__(self, image, position):
		super(HelicopterSprite, self).__init__()

		self.image = pygame.image.load(image)
		self.position = position
		self.speed = 0.0
		self.throttle = False

	def update(self, obstacles):
		if self.throttle:
			self.speed = min(self.speed + self.ROTORS, self.MAX_VERTICAL_SPEED)
		else:
			self.speed = max(self.speed + self.GRAVITY, self.MIN_VERTICAL_SPEED)

		self.position = (
			self.position[0],
			self.position[1] + self.speed
		)

		self.rect = self.image.get_rect()
		self.rect.center = self.position

class ObstacleSprite(pygame.sprite.Sprite):
	HORIZONTAL_SPEED = -5.0

	def __init__(self, image, min_height, max_height, x_pos):
		super(ObstacleSprite, self).__init__()

		self.image = pygame.image.load(image)
		self.position = (x_pos, random.randint(min_height, max_height))

	def update(self, delta_ms):
		self.position = (
			self.position[0] + self.HORIZONTAL_SPEED,
			self.position[1]
		)

		self.rect = self.image.get_rect()
		self.rect.center = self.position

class Cave():
	MIN_HEIGHT = 25
	WALL_COLOR = (100, 15, 100)
	HORIZONTAL_SPEED = -5.0

	def __init__(self, screen, cave_height):
		H, W = screen.get_height(), screen.get_width()
		self.screen = screen
		self.cave_height = cave_height

		self.top_endpoints = [
			(W, 0),
			(0, 0),
			(0, H / 2 - cave_height / 2),
		]

		self.bottom_endpoints = [
			(W, H),
			(0, H),
			(0, H / 2 + cave_height / 2),
		]

		self.midpoints = []
		self.sample_midpoint(x=(W / 2))
		self.sample_midpoint(x=W)
		self.redraw_walls()
	
	def sample_midpoint(self, x=None):
		if x is None:
			W = self.screen.get_width()
			x = W + W / 2

		height = random.randint(self.MIN_HEIGHT, self.screen.get_height() / 2 - self.MIN_HEIGHT)
		self.midpoints.append((x, height))

		return (x, height)

	def update(self):
		midpoints = []

		for midpoint in self.midpoints:
			if midpoint >= -self.HORIZONTAL_SPEED:
				midpoints.append((midpoint[0] + self.HORIZONTAL_SPEED, midpoint[1]))

		self.midpoints = midpoints
		self.redraw_walls()

	def redraw_walls(self):
		pygame.draw.polygon(screen, self.WALL_COLOR,
			self.midpoints + self.top_endpoints)
		self.top = path.Path(np.array(self.midpoints + self.top_endpoints))

		bottom_midpoints = [(mp[0], mp[1] + self.cave_height) for mp in self.midpoints]
		pygame.draw.polygon(screen, self.WALL_COLOR,
			bottom_midpoints + self.bottom_endpoints)
		self.bottom = path.Path(np.array(bottom_midpoints + self.bottom_endpoints))

	def check_collision(self, heli_group):
		for heli in heli_group.sprites():
			if self.collides(heli.rect):
				heli.image = pygame.image.load(EXPLOSION_IMG)

	def collides(self, rect):
		return (
			self.top.contains_point(rect.topleft) or
			self.top.contains_point(rect.topright) or
			self.bottom.contains_point(rect.bottomleft) or
			self.bottom.contains_point(rect.bottomright)
		)

	def spawn_obstacle(obstacles, y_min, y_max):
		pass


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
	delta_ms = clock.tick(10)

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
