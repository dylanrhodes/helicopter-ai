import pygame
from pygame.locals import *
import random
import time


EXPLOSION_IMG = 'explosion.png'
HELICOPTER_IMG = 'helicopter3.png'
OBSTACLE_IMG = 'obstacle4.png'
OBSTACLE_SPAWN_RATE = 1.5

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
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


""" Initialize Game Area """
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
clock = pygame.time.Clock()

heli = HelicopterSprite(HELICOPTER_IMG, (250, SCREEN_HEIGHT / 2))
heli_group = pygame.sprite.RenderPlain(heli)

obstacles = pygame.sprite.LayeredUpdates()
next_spawn = time.time()

""" Helper methods """
def spawn_obstacle(obstacles):
	obstacle = ObstacleSprite(OBSTACLE_IMG, 300, 500, SCREEN_WIDTH)
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
		spawn_obstacle(obstacles)
		next_spawn = time.time() + OBSTACLE_SPAWN_RATE

	heli_group.update(delta_ms)
	obstacles.update(delta_ms)
	
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
