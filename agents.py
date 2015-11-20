import numpy as np
import random


class Agent(object):
	def __init__(self):
		pass

	def act(self, state):
		return True

	def accept_reward(self, state, action, reward, new_state, train=True):
		pass

	def save(self, file_name):
		pass

class RandomAgent(Agent):
	def __init__(self):
		super(RandomAgent, self).__init__()

	def act(self, state):
		return random.random() > 0.375
