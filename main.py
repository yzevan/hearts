import sys
print('Terminal encoding: {}'.format(sys.stdout.encoding))

from game import Game
from player import StupidPlayer, SimplePlayer, ExpertPlayer

# These four players are playing the game
players = [ExpertPlayer(), SimplePlayer(), SimplePlayer(), SimplePlayer()]

# We are simulating n games accumulating a total score
nr_of_matches = 20
print('We are playing {} matches in total.'.format(nr_of_matches))
for match_nr in range(nr_of_matches):
    scores = (0, 0, 0, 0)
    game_nr = 0
    print('MATCH {}'.format(match_nr))
    while(max(scores) < 100):
        game_nr += 1
        print('GAME {}'.format(game_nr))
        game = Game(players, game_nr % 4, verbose=True)
        scores = tuple(sum(x) for x in zip(scores, game.play()))
    print(scores)
