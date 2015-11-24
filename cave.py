import numpy as np
from math import floor
import matplotlib.path as path
import pygame
import random
from sprites import ObstacleSprite


EXPLOSION_IMG = 'explosion.png'
OBSTACLE_IMG = 'obstacle4.png'

class Cave():
	MIN_HEIGHT = 25
	WALL_COLOR = (100, 15, 100)
	HORIZONTAL_SPEED = -5.0

	def __init__(self, screen, cave_height):
		W, H = screen.get_width(), screen.get_height()
		self.screen = screen
		self.cave_height = cave_height

		self.top_endpoints = [
			(W, 0),
			(0, 0),
			#(0, H / 2 - cave_height / 2),
		]

		self.bottom_endpoints = [
			(W, H),
			(0, H),
			#(0, H / 2 + cave_height / 2),
		]

		self.midpoints = [(0, H / 2 - cave_height / 2)]
		self.update_walls()
		self.obstacles = pygame.sprite.LayeredUpdates()

	def get_ceiling_at(self, x_pos):
		prev_point, next_point = None, None
		prev_x, next_x = -np.Inf, np.Inf

		for point in (self.top_endpoints + self.midpoints):
			if point[0] < x_pos and point[0] > prev_x:
				prev_point = point
			elif point[0] > x_pos and point[0] < next_x:
				next_point = point

		scale = float(x_pos - prev_point[0]) / (next_point[0] - prev_point[0])
		return int(prev_point[1] + scale * (next_point[1] - prev_point[1]))

	def next_obstacle_coords(self, x_pos):
		next_obstacle, next_midpoint = None, None

		for obstacle in self.obstacles.sprites():
			obstacle_x = obstacle.rect.center[0]

			if ((next_obstacle is None or obstacle_x < next_obstacle.rect.center[0]) and
				x_pos < obstacle_x):
				next_obstacle = obstacle

		for midpoint in self.midpoints:
			if ((next_midpoint is None or midpoint[0] < next_midpoint[0]) and
				x_pos < midpoint[0]):
				next_midpoint = midpoint

		if next_obstacle is None or next_midpoint is None:
			W, H = self.screen.get_width(), self.screen.get_height()
			fake_obs_pos = (W + W / 2, H / 2)
			fake_mid_pos = (W + W / 2, H / 2 - self.cave_height / 2)

			return fake_obs_pos, fake_mid_pos

		return next_obstacle.rect.center, next_midpoint
	
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
			if midpoint[0] >= -1200:
				midpoints.append((midpoint[0] + self.HORIZONTAL_SPEED, midpoint[1]))

		self.midpoints = midpoints
		self.update_walls()

		self.obstacles.update(100)
		self.obstacles.draw(self.screen)

		# Remove reference to obstacle once it falls off screen
		if len(self.obstacles.sprites()) > 0:
			oldest_obstacle = self.obstacles.get_sprite(0)

			if oldest_obstacle.position[0] < 0:
				self.obstacles.remove(oldest_obstacle)

	def update_walls(self):
		pygame.draw.polygon(self.screen, self.WALL_COLOR,
			self.midpoints + self.top_endpoints)
		self.top = path.Path(np.array(self.midpoints + self.top_endpoints))

		bottom_midpoints = [(mp[0], mp[1] + self.cave_height) for mp in self.midpoints]
		pygame.draw.polygon(self.screen, self.WALL_COLOR,
			bottom_midpoints + self.bottom_endpoints)
		self.bottom = path.Path(np.array(bottom_midpoints + self.bottom_endpoints))

	def check_collision(self, heli_group):
		for heli in heli_group.sprites():
			if self.collides(heli.rect):
				heli.image = pygame.image.load(EXPLOSION_IMG)
				return True

			for obstacle in self.obstacles.sprites():
				if pygame.sprite.collide_rect(heli, obstacle):
					heli.image = pygame.image.load(EXPLOSION_IMG)
					return True

		return False

	def collides(self, rect):
		return (
			self.top.contains_point(rect.topleft) or
			self.top.contains_point(rect.topright) or
			self.bottom.contains_point(rect.bottomleft) or
			self.bottom.contains_point(rect.bottomright)
		)

	def spawn_obstacle(self, y_min, y_max):
		W = self.screen.get_width()
		obstacle = ObstacleSprite(OBSTACLE_IMG, y_min, y_max, W + W / 2)
		self.obstacles.add(obstacle)
