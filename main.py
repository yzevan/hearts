import sys
from game import Game
from players.stupid_player import StupidPlayer
from players.simple_player import SimplePlayer
from players.advanced_player import AdvancedPlayer
from players.montecarlo_player import MonteCarloPlayer
import variables

# These four players are playing the game
players = [AdvancedPlayer(), MonteCarloPlayer(), SimplePlayer(), SimplePlayer()]
# players = [AdvancedPlayer(), SimplePlayer(), SimplePlayer(), SimplePlayer()]

# We are simulating n games accumulating a total score
nr_of_matches = variables.nr_of_matches
print('We are playing {} matches in total.'.format(nr_of_matches))
winning_count = [0, 0, 0, 0]
for match_nr in range(nr_of_matches):
    scores = (0, 0, 0, 0)
    game_nr = 0
    print('MATCH {}'.format(match_nr))
    while(max(scores) < 100):
        game_nr += 1
        print('GAME {}'.format(game_nr))
        game = Game(players, game_nr % 4)
        scores = tuple(sum(x) for x in zip(scores, game.play()))
    print(scores)
    min_index = scores.index(min(scores))
    winning_count[min_index] += 1
print(winning_count)
