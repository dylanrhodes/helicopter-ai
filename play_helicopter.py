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
			#old_model = pickle.load(open('deep_model.pk', 'rb'))
			#agent.model.copy_parameters_from(old_model.parameters)
		else:
			agent = QAgent(20000, 2)

		game = HelicopterGame(agent=agent)
		num_games = 0
		scores = []
		max_score = 0

		while num_games < NUM_TRAINING_GAMES:
			scores.append(game.run_game())

			if scores[-1] > max_score:
				max_score = scores[-1]
				agent.update_target()
				print '******** UPDATED TARGET NETWORK ********'

			if num_games % 100 == 0:
				print 'FINISHED {} GAMES'.format(num_games)

			game.init_game()

			num_games += 1

		print 'Agent scored: {}'.format(scores)
		print 'Mean score: {}'.format(np.mean(np.array(scores)))
		print 'Max score: {}'.format(np.max(np.array(scores)))
		pdb.set_trace()
		agent.save('chain_agent.txt')
		np.save(open('score_history.txt', 'wb'), np.array(scores))
