import sys
from game import Game
from players.stupid_player import StupidPlayer
from players.min_player import MinPlayer
from players.advanced_player import AdvancedPlayer
from players.montecarlo_player import MonteCarloPlayer
import variables

# These four players are playing the game
players = [AdvancedPlayer(), MonteCarloPlayer(), MinPlayer(), StupidPlayer()]
# players = [AdvancedPlayer(), MinPlayer(), MinPlayer(), StupidPlayer()]

# We are simulating n games accumulating a total score
nr_of_matches = variables.nr_of_matches
print('We are playing {} matches in total.'.format(nr_of_matches))
winning_count = [0, 0, 0, 0]
for match_nr in range(nr_of_matches):
    scores = (0, 0, 0, 0)
    print('MATCH {}'.format(match_nr))
    for game_nr in range(1, 5):
        print('GAME {}'.format(game_nr))
        game = Game(players, game_nr % 4)
        scores = tuple(sum(x) for x in zip(scores, game.play()))
    print(scores)
    max_index = scores.index(max(scores))
    max_score = max(scores)
    for i in range(4):
        if scores[i] == max_score:
            winning_count[i] += 1
print(winning_count)