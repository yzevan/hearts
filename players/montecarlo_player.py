from players.player import Player
from card import Suit, Rank, Card, Deck
from rules import is_card_valid
import datetime
from random import choice
from __future__ import division
from math import log, sqrt

class MonteCarloPlayer(Player):

    def __init__(self, game, verbose=True, **kwargs):
        self.verbose = verbose
        self.game = game
        self.states = []
        seconds = kwargs.get('time', 30)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.max_moves = kwargs.get('max_moves', 100)
        self.wins = {}
        self.plays = {}
        self.C = kwargs.get('C', 1.4)
        self.max_depth = 0

    def update(self, state):
        self.states.append(state)

    def get_play(self):
        self.max_depth = 0
        state = self.states[-1]
        player = self.game.getCurrentPlayer()
        legal = self.game.getCurrentTrickValidCards()

        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation()
            games += 1

    def run_simulation(self):
        pass