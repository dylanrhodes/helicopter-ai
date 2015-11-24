import numpy as np
import random


MAX_SIZE = 50000

class History(object):
	def __init__(self, ):
		self.history = []
		self.length = 0

	def add(self, sample):
		if self.length != MAX_SIZE:
			self.history.append(sample)
			self.length += 1
		else:
			index = random.randint(1, MAX_SIZE) - 1
			self.history[index] = sample

	def get(self,):
		return self.history[random.randint(1, self.length) - 1]
