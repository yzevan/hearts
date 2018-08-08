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

    def say(self, message, *formatargs):
        if self.verbose:
            print(message.format(*formatargs))

    def update(self, state):
        self.states.append(state)

    def pass_cards(self, hand):
        self.say('Hand before passing: {}', hand)
        cards_to_pass = super(MonteCarloPlayer, self).pass_cards(hand)
        self.say('Cards to pass: {}', cards_to_pass)
        return cards_to_pass

    def play_card(self):
        self.max_depth = 0
        state = self.states[-1]
        player = self.game.current_player
        legal = self.game.current_trick_valid_cards

        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation()
            games += 1
        self.say('Game count: {}', games)
        self.say('Time: {}', datetime.datetime.utcnow() - begin)
        
        moves_states = []
        for p in legal:
            legal_state = self.game.cards_played + p
            moves_states.append((p, legal_state))

        percent_wins, move = max(
            (self.wins.get((player, S), 0) /
             self.plays.get((player, S), 1),
             p)
            for p, S in moves_states
        )

        # Display the stats for each possible play.
        for x in sorted(
            ((100 * self.wins.get((player, S), 0) /
              self.plays.get((player, S), 1),
              self.wins.get((player, S), 0),
              self.plays.get((player, S), 0), p)
             for p, S in moves_states),
            reverse=True
        ):
            self.say("{3}: {0:.2f}% ({1} / {2})".format(*x))

        self.say('Maximum depth searched: {}', self.max_depth)
        return move

    def run_simulation(self):
        plays, wins = self.plays, self.wins

        visited_states = set()
        states_copy = self.states[:]
        state = states_copy[-1]
        
        expand = True
        for t in xrange(self.max_moves):
            player = self.game.current_player
            legal = self.game.current_trick_valid_cards

            moves_states = []
            for p in legal:
                legal_state = self.game.cards_played + p
                moves_states.append((p, legal_state))
                
            if all(plays.get((player, S)) for p, S in moves_states):
                # If we have stats on all of the legal moves here, use them.
                log_total = log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) +
                     self.C * sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else:
                # Otherwise, just make an arbitrary decision.
                move, state = choice(moves_states)