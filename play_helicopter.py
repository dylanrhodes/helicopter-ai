from agents import *
from helicopter_game import HelicopterGame
import sys

NUM_TRAINING_GAMES = 50

if __name__ == '__main__':
	if len(sys.argv) == 1:
		game = HelicopterGame()
	else:
		agent = RandomAgent()
		game = HelicopterGame(agent=agent)
		num_games = 0
		scores = []

		while num_games < NUM_TRAINING_GAMES:
			scores.append(game.run_game())
			game.init_game()
			num_games += 1

		print 'Agent scored: {}'.format(scores)
		print 'Mean score: {}'.format(np.mean(np.array(scores)))
		print 'Max score: {}'.format(np.max(np.array(scores)))
		agent.save('agent.txt')
