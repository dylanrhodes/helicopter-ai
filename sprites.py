import pygame
import random

class HelicopterSprite(pygame.sprite.Sprite):
	MAX_VERTICAL_SPEED = 5.0
	MIN_VERTICAL_SPEED = -10.0

	ROTORS = -0.5
	GRAVITY = 1.0

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
	def __init__(self, image, min_height, max_height, x_pos, speed=-5.0):
		super(ObstacleSprite, self).__init__()

		self.image = pygame.image.load(image)
		self.position = (x_pos, random.randint(min_height, max_height))
		self.speed = speed

	def update(self, delta_ms):
		self.position = (
			self.position[0] + self.speed,
			self.position[1]
		)

		self.rect = self.image.get_rect()
		self.rect.center = self.position
