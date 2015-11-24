from chainer import FunctionSet, optimizers, Variable
import chainer.functions as F
import copy
from history import *
import numpy as np
import pdb
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

class DeepQAgent(Agent):
	def __init__(self, input_vector, alpha=0.05, gamma=0.99, epsilon=1.0):
		super(DeepQAgent, self).__init__()
		self.alpha = alpha
		self.gamma = gamma
		self.epsilon = epsilon
		self.nnet = DenseNetwork(input_vector)

	def act(self, state):
		if random.random() < self.epsilon:
			return random.random() > 0.375

		return True

class ChainerAgent(Agent):
	def __init__(self, epsilon=1.0):
		super(ChainerAgent, self).__init__()
		self.epsilon = epsilon
		self.gamma = 0.99
		self.iterations = 0
		self.model = FunctionSet(
			l1 = F.Linear(9, 50),
			l2 = F.Linear(50, 50),
			l3 = F.Linear(50, 2),
		)

		self.optimizer = optimizers.RMSprop(lr=1e-5)
		self.optimizer.setup(self.model)
		self.update_target()

		self.history = ChainHistory()

	def forward(self, state, action, reward, new_state, is_terminal):
		#TODO: add support for minibatch learning
 		#TODO: zero-clipping or normalization?  Check Mnih

		q = self.get_q(Variable(state))
		q_target = self.get_target_q(Variable(new_state))

		max_target_q = np.max(q_target.data, axis=1)

		target = np.copy(q.data)

		for i in xrange(target.shape[0]):
			if is_terminal[i]:
				target[i, action[i]] = reward[i]
			else:
				target[i, action[i]] = reward[i] + self.gamma * max_target_q[i]
		
		loss = F.mean_squared_error(Variable(target), q)
		return loss, np.mean(q.data[:, action[i]])

	def get_q(self, state):
		h1 = F.relu(self.model.l1(state))
		h2 = F.relu(self.model.l2(h1))
		return self.model.l3(h2)

	def get_target_q(self, state):
		h1 = F.relu(self.target_model.l1(state))
		h2 = F.relu(self.target_model.l2(h1))
		return self.target_model.l3(h2)

	def accept_reward(self, state, action, reward, new_state, is_terminal):
		self.history.add((state, action, reward, new_state, is_terminal))

		self.iterations += 1
		#if self.iterations % 10000 == 0:
		#	self.update_target()
		
		state, action, reward, new_state, is_terminal = self.history.get(num=32)
		loss, q = self.forward(state, action, reward, new_state, is_terminal)
		self.optimizer.zero_grads()
		loss.backward()
		self.optimizer.update()

	def act(self, state):
		self.epsilon -= (1.0 / 50000)

		if random.random() < 0.0001:
			print 'Epsilon greedy strategy current epsilon: {}'.format(self.epsilon)

		if random.random() < self.epsilon:
			return random.random() > 0.375

		q = self.get_q(Variable(state))

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
		with open(file_name, 'rb') as in_file:
			model = pickle.loads(in_file)
			self.model.copy_parameters_from(model)

	def update_target(self):
		self.target_model = copy.deepcopy(self.model)


class ConvQAgent(Agent):
	pass
