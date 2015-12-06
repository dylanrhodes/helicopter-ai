import numpy as np
import random


MAX_SIZE = 10000

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

class ChainHistory(object):
	def __init__(self, state_len=9):
		self.history = (
			np.zeros((MAX_SIZE, state_len), dtype=np.float32),
			np.zeros((MAX_SIZE, 1), dtype=np.uint8),
			np.zeros((MAX_SIZE, 1), dtype=np.float32),
			np.zeros((MAX_SIZE, state_len), dtype=np.float32),
			np.zeros((MAX_SIZE, 1), dtype=np.bool),
		)
		self.length = 0

	def add(self, sample):
		if self.length != MAX_SIZE:
			index = self.length
			self.length += 1
		else:
			index = random.randint(1, MAX_SIZE) - 1

		for i in xrange(len(self.history)):
			self.history[i][index, :] = sample[i]

	def get(self, num=1):
		indices = np.random.randint(self.length, size=num)
		return (
			self.history[0][indices, :],
			self.history[1][indices, :],
			self.history[2][indices, :],
			self.history[3][indices, :],
			self.history[4][indices, :],
		)

class ConvHistory(object):
	def __init__(self, state_size):
		self.history = (
			np.zeros(tuple([MAX_SIZE] + list(state_size)), dtype=np.float32),
			np.zeros((MAX_SIZE, 1), dtype=np.uint8),
			np.zeros((MAX_SIZE, 1), dtype=np.float32),
			np.zeros(tuple([MAX_SIZE] + list(state_size)), dtype=np.float32),
			np.zeros((MAX_SIZE, 1), dtype=np.bool),
		)
		self.length = 0

	def add(self, sample):
		if self.length != MAX_SIZE:
			index = self.length
			self.length += 1
		else:
			index = random.randint(1, MAX_SIZE) - 1

		for i in xrange(len(self.history)):
			if i == 0 or i == 3:
				self.history[i][index, :, :, :] = sample[i]
			else:
				self.history[i][index, :] = sample[i]

	def get(self, num=1):
		indices = np.random.randint(self.length, size=num)
		return (
			self.history[0][indices, :, :, :],
			self.history[1][indices, :],
			self.history[2][indices, :], 
			self.history[3][indices, :, :, :],
			self.history[4][indices, :],
		)
