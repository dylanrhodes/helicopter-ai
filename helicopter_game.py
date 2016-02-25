from agents import *
from cave import Cave
import pygame
from pygame.locals import *
import random
from sprites import *
from skimage.transform import resize


EXPLOSION_IMG = 'explosion.png'
HELICOPTER_IMG = 'helicopter3.png'
OBSTACLE_IMG = 'obstacle4.png'
OBSTACLE_HEIGHT = 100
OBSTACLE_SPAWN_RATE = 60
CAVE_HEIGHT = 300

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
BG_COLOR = (30, 50, 25)
WHITE = (255, 255, 255)
FRAME_RATE = 30

class HelicopterGame(object):
	""" Wrapper class used for initializing Helicopter games and controlling state """

	def __init__(self, agent=None):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
		self.clock = pygame.time.Clock()
		self.agent = agent

		self.init_game()

		if agent is None:
			self.has_started = False
			self.run_game()
		else:
			self.has_started = True

	def process_event(self, event):
		""" Process user interaction """
		if event.type == pygame.QUIT:
			pygame.quit()
		elif event.type == MOUSEBUTTONDOWN:
			self.heli.throttle = True
		elif event.type == MOUSEBUTTONUP:
			self.heli.throttle = False

		if not hasattr(event, 'key'): 
			return
		elif event.key == K_SPACE:
			if self.has_crashed:
				self.init_game()
			self.has_started = True
		elif event.key == K_UP:
			BG_COLOR = (
				random.randint(1, 255),
				random.randint(1, 255),
				random.randint(1, 255)
			)

	def init_game(self):
		self.cave = Cave(self.screen, CAVE_HEIGHT)

		self.heli = HelicopterSprite(HELICOPTER_IMG, (250, SCREEN_HEIGHT / 2))
		self.heli_group = pygame.sprite.RenderPlain(self.heli)

		self.score = 0
		self.frame_counter = 0
		self.has_crashed = False

	def update_state(self):
		""" Update game state and redraw screen """
		if self.frame_counter % OBSTACLE_SPAWN_RATE == 0:
			midpoint = self.cave.sample_midpoint()
			self.cave.spawn_obstacle(midpoint[1] + OBSTACLE_HEIGHT / 2, midpoint[1] + CAVE_HEIGHT - OBSTACLE_HEIGHT / 2)

		self.heli_group.update(self.frame_counter)
		self.cave.update()

		if self.cave.check_collision(self.heli_group):
			self.has_crashed = True

		self.heli_group.draw(self.screen)

		self.score += 1
		self.frame_counter += 1
		self.display_score()

	def display_score(self):
		score_font = pygame.font.SysFont('arial', 20)
		score_surface = score_font.render("Score: {}".format(self.score), True, WHITE)
		score_rect = score_surface.get_rect()

		if self.has_crashed:
			score_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
		else:
			score_rect.topleft = (30, SCREEN_HEIGHT - 50)
		self.screen.blit(score_surface, score_rect)

	def display_start_menu(self):
		title_font = pygame.font.SysFont('arial', 30)
		title_surface = title_font.render("Helicopter", True, WHITE)
		title_rect = title_surface.get_rect()
		title_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
		self.screen.blit(title_surface, title_rect)

	def display_game_over(self):
		msg_font = pygame.font.SysFont('arial', 30)
		msg_surface = msg_font.render("Game Over!", True, WHITE)
		msg_rect = msg_surface.get_rect()
		msg_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
		self.screen.blit(msg_surface, msg_rect)

		self.display_score()

	def get_state_vector(self):
		velocity = self.heli.speed
		heli_x, heli_y = self.heli.position

		cave_y = self.cave.get_ceiling_at(heli_y)
		obs_pos, ceil_pos = self.cave.next_obstacle_coords(heli_x)
		obs_pos2, ceil_pos2 = self.cave.next_obstacle_coords(obs_pos[0])

		W = float(self.screen.get_width())
		H = float(self.screen.get_height())

		state_vector = np.zeros((9, 1), dtype=np.float32)

		state_vector[0] = (heli_y - cave_y) * 1.0 / CAVE_HEIGHT
		state_vector[1] = cave_y / H * 2
		state_vector[2] = velocity / 10.0
		state_vector[3] = obs_pos[0] / (W * 1.5)
		state_vector[4] = obs_pos[1] / H
		state_vector[5] = ceil_pos[1] / H * 2
		state_vector[6] = obs_pos2[0] / (W * 1.5)
		state_vector[7] = obs_pos2[1] / H
		state_vector[8] = ceil_pos2[1] / H * 2

		return state_vector.T

	def get_current_screen(self, H=84, W=84):
		rgb = pygame.surfarray.array3d(self.screen)
		rgb = resize(rgb, (W, H))
		rgb = rgb.astype(np.float32)
		return rgb[:, :, 0] * 0.2126 + rgb[:, :, 1] * 0.7152 + rgb[:, :, 2] * 0.0722

	def get_current_state(self):
		velocity = self.heli.speed
		heli_x, heli_y = self.heli.position

		cave_y = self.cave.get_ceiling_at(heli_y)
		obs_pos, ceil_pos = self.cave.next_obstacle_coords(heli_x)

		H = self.screen.get_height()

		velocity_i = 0 if velocity > 0 else 1
		heli_y_k = int(10.0 * (heli_y - cave_y) / float(CAVE_HEIGHT))
		cave_y_k = int(10.0 * float(cave_y) / H)
		next_cave_y_k = int(10.0 * float(ceil_pos[1]) / H)
		next_obs_y_k = int(10.0 * (obs_pos[1] - ceil_pos[1]) / float(CAVE_HEIGHT))

		state_index = 0
		state_index += heli_y_k
		state_index += 10 * cave_y_k
		state_index += 100 * next_cave_y_k
		state_index += 1000 * next_obs_y_k

		if velocity > 0:
			state_index * 2

		return state_index

	def get_current_reward(self):
		if self.has_crashed:
			return -1
		else:
			return min(self.score / 100.0, 1.0)

	def run_game(self):
		if self.agent is not None:
			self.agent.start_new_game()

		prev_screen = None

		while True:
			delta_ms = self.clock.tick(FRAME_RATE)

			if self.agent is None:
				for event in pygame.event.get():
					self.process_event(event)
			else:
				if type(self.agent) is ChainerAgent:
					state = self.get_state_vector()
				elif type(self.agent) is ConvQAgent:
					if prev_screen is None:
						state = self.get_current_screen(W=84, H=84)
					else:
						state = prev_screen
				else:
					state = self.get_current_state()

				agent_action = self.agent.act(state)
				if agent_action is not None:
					self.heli.throttle = agent_action

			self.screen.fill(BG_COLOR)

			if not self.has_started:
				self.display_start_menu()
			elif self.has_crashed:
				self.display_game_over()
			else:
				self.update_state()

			if self.agent is not None:
				action = int(self.heli.throttle)
				reward = self.get_current_reward()

				if type(self.agent) is ChainerAgent:
					new_state = self.get_state_vector()
				elif type(self.agent) is ConvQAgent:
					new_state = self.get_current_screen(W=84, H=84)
					prev_screen = new_state
				else:
					new_state = self.get_current_state()

				#self.agent.accept_reward(state, action, reward, new_state, self.has_crashed)

				if self.has_crashed:
					return self.score

			pygame.display.flip()
