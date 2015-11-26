from chainer import cuda, FunctionSet, optimizers, Variable
import chainer.functions as F
import copy
import cupy as cp
from history import *
import numpy as np
import pdb
import pickle
import random


class Agent(object):
	def __init__(self):
		pass

	def act(self, state):
		return True

	def accept_reward(self, state, action, reward, new_state, is_terminal):
		pass

	def save(self, file_name):
		pass

class RandomAgent(Agent):
	def __init__(self):
		super(RandomAgent, self).__init__()

	def act(self, state):
		return random.random() > 0.375

class QAgent(Agent):
	# TODO: make policy annealed epsilon-greedy

	def __init__(self, state_space, action_space, alpha=0.05, gamma=0.99):
		super(QAgent, self).__init__()
		self.alpha = alpha
		self.gamma = gamma

		self.utility = np.zeros((state_space, action_space), dtype=np.float32)

	def act(self, state):
		if self.utility[state, 1] == self.utility[state, 0]:
			return random.random() > 0.375

		return self.utility[state, 1] > self.utility[state, 0]

	def accept_reward(self, state, action, reward, new_state, is_terminal):
		if train:
			current_utility = self.utility[state, action]
			self.utility[state, action] = current_utility + self.alpha * (reward + (
				np.max(self.utility[new_state, :])) - current_utility)

	def save(self, file_name):
		np.save(open(file_name, 'wb'), self.utility)

class ChainerAgent(Agent):
	def __init__(self, epsilon=1.0):
		super(ChainerAgent, self).__init__()
		cuda.init()
		self.epsilon = epsilon
		self.gamma = 0.99
		self.iterations = 0
		self.model = FunctionSet(
			l1 = F.Linear(9, 256),
			l2 = F.Linear(256, 256),
			l3 = F.Linear(256, 256),
			l4 = F.Linear(256, 2),
		).to_gpu()

		self.optimizer = optimizers.RMSprop(lr=1e-5)
		self.optimizer.setup(self.model)
		self.update_target()

		self.history = ChainHistory()

	def forward(self, state, action, reward, new_state, is_terminal):
		q = self.get_q(Variable(state))
		q_target = self.get_target_q(Variable(new_state))

		max_target_q = cp.max(q_target.data, axis=1)

		target = cp.copy(q.data)

		for i in xrange(target.shape[0]):
			curr_action = int(action[i])
			if is_terminal[i]:
				target[i, curr_action] = reward[i]
			else:
				target[i, curr_action] = reward[i] + self.gamma * max_target_q[i]
		
		loss = F.mean_squared_error(Variable(target), q)
		return loss, 0.0 #cp.mean(q.data[:, action[i]])

	def get_q(self, state):
		h1 = F.relu(self.model.l1(state))
		h2 = F.relu(self.model.l2(h1))
		h3 = F.relu(self.model.l3(h2))
		return self.model.l4(h3)

	def get_target_q(self, state):
		h1 = F.relu(self.target_model.l1(state))
		h2 = F.relu(self.target_model.l2(h1))
		h3 = F.relu(self.target_model.l3(h2))
		return self.target_model.l4(h3)

	def accept_reward(self, state, action, reward, new_state, is_terminal):
		self.history.add((state, action, reward, new_state, is_terminal))

		self.iterations += 1
		if self.iterations % 10000 == 0:
			print '*** UPDATING TARGET NETWORK ***'
			self.update_target()
		
		state, action, reward, new_state, is_terminal = self.history.get(num=32)

		state = cuda.to_gpu(state)
		action = cuda.to_gpu(action)
		new_state = cuda.to_gpu(new_state)
		reward = cuda.to_gpu(reward)

		loss, q = self.forward(state, action, reward, new_state, is_terminal)
		self.optimizer.zero_grads()
		loss.backward()
		self.optimizer.update()

	def act(self, state):
		if self.epsilon > 0.05:
			self.epsilon -= (0.95 / 150000)

		if random.random() < 0.0001:
			print 'Epsilon greedy strategy current epsilon: {}'.format(self.epsilon)

		if random.random() < self.epsilon:
			return random.random() > 0.375

		q = self.get_q(Variable(cuda.to_gpu(state)))

		if random.random() < 0.01:
			if q.data[0,1] > q.data[0,0]:
				print 'On: {}'.format(q.data)
			else:
				print 'Off: {}'.format(q.data)

		return q.data[0,1] > q.data[0,0]

	def save(self, file_name):
		with open(file_name, 'wb') as out_file:
			pickle.dump(self.model, out_file)

	def load(self, file_name):
		self.epsilon = 0.0

		with open(file_name, 'rb') as in_file:
			model = pickle.load(in_file)
			self.model.copy_parameters_from(model.parameters)

	def update_target(self):
		self.target_model = copy.deepcopy(self.model)
		self.target_model = self.target_model.to_gpu()


class ConvQAgent(Agent):
	pass
