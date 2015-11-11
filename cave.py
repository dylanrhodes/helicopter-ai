import numpy as np
import matplotlib.path as path
import pygame
import random


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
		self.update_walls()
	
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
		self.update_walls()

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

	def collides(self, rect):
		return (
			self.top.contains_point(rect.topleft) or
			self.top.contains_point(rect.topright) or
			self.bottom.contains_point(rect.bottomleft) or
			self.bottom.contains_point(rect.bottomright)
		)

	def spawn_obstacle(obstacles, y_min, y_max):
		pass
