import sys
from game import Game
from players.random_player import RandomPlayer
from players.min_player import MinPlayer
from players.advanced_player import AdvancedPlayer
from players.montecarlo_player import MonteCarloPlayer
import variables
from utils import init_logger
import logging


def play():
    # These four players are playing the game
    if variables.montecarlo:
        players = [AdvancedPlayer(), MonteCarloPlayer(), MinPlayer(), RandomPlayer()]
    else:
        players = [AdvancedPlayer(), MinPlayer(), MinPlayer(), RandomPlayer()]

    # We are simulating n games accumulating a total score
    nr_of_matches = variables.nr_of_matches
    logging.debug('We are playing {} matches in total.'.format(nr_of_matches))
    winning_count = [0, 0, 0, 0]
    for match_nr in range(nr_of_matches):
        scores = (0, 0, 0, 0)
        logging.debug("--- MATCH {} ---".format(match_nr))
        for game_nr in range(1, 5):
            logging.debug("--- GAME {} ---".format(game_nr))
            game = Game(players, game_nr % 4)
            scores = tuple(sum(x) for x in zip(scores, game.play()))
        logging.debug("--- Scores: {} ---".format(scores))
        max_score = max(scores)
        for i in range(4):
            if scores[i] == max_score:
                winning_count[i] += 1
    logging.debug("--- Winning count: {} ---".format(winning_count))

if __name__ == '__main__':
    init_logger()
    play()