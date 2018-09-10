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
    #if variables.montecarlo:
        #players = [AdvancedPlayer(), MonteCarloPlayer(), MinPlayer(), RandomPlayer()]
    #else:
        ##players = [AdvancedPlayer(), MinPlayer(), MinPlayer(), RandomPlayer()]
        ##players = [AdvancedPlayer(), AdvancedPlayer(), AdvancedPlayer(), AdvancedPlayer()]
        #players = [AdvancedPlayer(), MinPlayer(), MinPlayer(), MinPlayer()]

    # We are simulating n games accumulating a total score
    nr_of_matches = variables.nr_of_matches
    logging.debug('We are playing {} matches in total.'.format(nr_of_matches))
    winning_count = [0, 0, 0, 0]
    shoot_the_moon_list = (0, 0, 0, 0)
    shoot_try_num = 0
    for match_nr in range(nr_of_matches):
        scores = (0, 0, 0, 0)
        
        logging.debug("--- MATCH {} ---".format(match_nr))
        for game_nr in range(1, 5):
            logging.debug("--- GAME {} ---".format(game_nr))
            my_player = AdvancedPlayer(0)
            players = [my_player, MinPlayer(), MinPlayer(), MinPlayer()]
            game = Game(players, game_nr % 4)
            scores = tuple(sum(x) for x in zip(scores, game.play()))
            shoot_the_moon_list = tuple(sum(x) for x in zip(shoot_the_moon_list, game.shoot_the_moon_list))
            if my_player.try_to_shoot != 0:
                shoot_try_num += 1
           
        logging.debug("--- Scores: {} ---".format(scores))
        max_score = max(scores)
        for i in range(4):
            if scores[i] == max_score:
                winning_count[i] += 1
    logging.debug("--- Winning count: {} ---".format(winning_count))
    logging.debug("--- shoot the moon count: {} ---".format(shoot_the_moon_list))
    logging.debug("--- shoot the moon try count: {} ---".format(shoot_try_num))
    

if __name__ == '__main__':
    init_logger()
    play()