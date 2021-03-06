from agents import *
from helicopter_game import HelicopterGame
import pdb
import pickle
import sys

NUM_TRAINING_GAMES = 1000

if __name__ == '__main__':
	if len(sys.argv) == 1:
		game = HelicopterGame()
	elif len(sys.argv) == 2:
		if sys.argv[1] == 'chainer':
			agent = ChainerAgent()
			agent.load('chain_agent_overnight_35000.pk')
		elif sys.argv[1] == 'conv':
			agent = ConvQAgent()
			agent.load('conv_agent.pk')
		else:
			agent = QAgent(20000, 2)
			agent.load('qagent_30k.txt')

		agent = RandomAgent()

		game = HelicopterGame(agent=agent)
		num_games = 0
		scores = []
		max_score = 0

		while num_games < NUM_TRAINING_GAMES:
			scores.append(game.run_game())

			if num_games % 1000 == 0:
				#agent.save('conv_agent_{}.pk'.format(num_games))
				print 'FINISHED {} GAMES'.format(num_games)

			game.init_game()

			num_games += 1

		print 'Agent scored: {}'.format(scores)
		print 'Mean score: {}'.format(np.mean(np.array(scores)))
		print 'Std: {}'.format(np.std(np.array(scores)))
		print 'CI: {}'.format(np.std(np.array(scores)) * 1.96 / np.sqrt(len(scores)))
		print 'Max score: {}'.format(np.max(np.array(scores)))
		#agent.save('conv_agent.pk')
		#pdb.set_trace()
		np.save(open('score_history.txt', 'wb'), np.array(scores))
