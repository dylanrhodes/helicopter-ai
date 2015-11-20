from cave import Cave
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
WHITE = (255, 255, 255)
FRAME_RATE = 30


""" Initialize Game Area """
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
clock = pygame.time.Clock()

cave = Cave(screen, CAVE_HEIGHT)

heli = HelicopterSprite(HELICOPTER_IMG, (250, SCREEN_HEIGHT / 2))
heli_group = pygame.sprite.RenderPlain(heli)

obstacles = pygame.sprite.LayeredUpdates()
next_spawn = time.time()
score = 0

""" Helper methods """
def spawn_obstacle(obstacles, y_min, y_max):
	obstacle = ObstacleSprite(OBSTACLE_IMG, y_min, y_max, SCREEN_WIDTH + SCREEN_WIDTH / 2)
	obstacles.add(obstacle)

def pause():
	pass

def start_menu():
	while True:
		delta_ms = clock.tick(30)

		screen.fill(BG_COLOR)

		title_font = pygame.font.SysFont('arial', 30)
		title_surface = title_font.render("Helicopter", True, WHITE)
		title_rect = title_surface.get_rect()
		title_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
		screen.blit(title_surface, title_rect)

		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == MOUSEBUTTONDOWN:
				return
			if hasattr(event, 'key') and event.key == K_SPACE:
				return

def display_score():
	score_font = pygame.font.SysFont('arial', 20)
	score_surface = score_font.render("Score: {}".format(score), True, WHITE)
	score_rect = score_surface.get_rect()
	score_rect.topleft = (30, SCREEN_HEIGHT - 50)
	screen.blit(score_surface, score_rect)

""" Main Game Loop """
start_menu()

while True:
	delta_ms = clock.tick(30)

	# Process user interaction
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
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
		cave.spawn_obstacle(midpoint[1] + OBSTACLE_HEIGHT / 2, midpoint[1] + CAVE_HEIGHT - OBSTACLE_HEIGHT / 2)
		next_spawn = time.time() + OBSTACLE_SPAWN_RATE

	heli_group.update(delta_ms)
	cave.update()

	cave.check_collision(heli_group)
	heli_group.draw(screen)

	score += 1
	display_score()

	pygame.display.flip()
