from __future__ import division
from players.player import Player
from card import Suit, Rank, Card, Deck
from rules import all_valid_cards
import datetime
from random import sample, choice, shuffle
from math import log, sqrt
from copy import deepcopy
import variables
import logging


class MonteCarloPlayer(Player):

    def __init__(self, **kwargs):
        self.verbose = variables.verbose_montecarlo
        microseconds = kwargs.get('time', variables.montecarlo_time)
        self.calculation_time = datetime.timedelta(microseconds=microseconds)
        self.max_moves = kwargs.get('max_moves', 100)
        self.wins = {}
        self.plays = {}
        self.C = kwargs.get('C', 1.4)
        self.max_depth = 0
        self.cards_count = {}
        self.hand = []

    def say(self, message, *formatargs):
        if self.verbose:
            logging.debug(message.format(*formatargs))

    def setGame(self, game):
        self.game = game

    def setAttributes(self, game, cards_count, hand):
        self.setGame(game)
        self.cards_count = cards_count
        self.hand = hand

    def play_card(self, valid_cards, trick, out_of_suits, remaining_players, are_hearts_broken, is_spade_queen_played, my_hand, cards_played):
        all_cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        cards = [card for card in all_cards if card not in self.game.cards_played and card not in self.hand]
        self.max_depth = 0
        player = self.game.current_player_index

        if len(valid_cards) == 1:
            return valid_cards[0]

        self.say('Trick: {}', trick)
        self.say('Valid cards: {}', valid_cards)

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation(cards, self.cards_count, valid_cards)
            games += 1
        self.say('Game count: {}', games)
        self.say('Simulation Time: {}', datetime.datetime.utcnow() - begin)
        
        moves_states = []
        cards_played = self.game.cards_played
        for p in valid_cards:
            legal_state = cards_played + (p,)
            moves_states.append((p, legal_state))

        percent_wins, move = max(
            (self.wins.get((player, S), 0) /
             self.plays.get((player, S), 1),
             p)
            for p, S in moves_states
        )
        self.say('played card: {}', move)

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

    def run_simulation(self, cards, cards_count, valid_cards):
        plays, wins = self.plays, self.wins
        current_game = deepcopy(self.game)
        self.redistribute(cards, cards_count, current_game)
        visited_states = set()
        current_game.current_trick_valid_cards = valid_cards

        expand = True
        for t in range(self.max_moves):
            player = current_game.current_player_index
            legal = current_game.current_trick_valid_cards

            moves_states = []
            cards_played = current_game.cards_played
            for p in legal:
                legal_state = cards_played + (p,)
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
                # self.say('Play {} in state {} for value {}', move, state, value)
            else:
                # Otherwise, just make an arbitrary decision.                
                move, state = choice(moves_states)
                # self.say('Random play {} in state {}', move, state)

            current_game.update_status(move)

            if expand and (player, state) not in plays:
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, state))
            winners = current_game.winners()
            if winners:
                break

        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player, state)] += 1
            if player in winners:
                wins[(player, state)] += 1

    def redistribute(self, cards, cards_count, game):
        shuffle(cards)
        start = 0
        for key, value in cards_count.items():
            t = start
            start += value
            game.player_hands[key] = sorted(cards[t: start])