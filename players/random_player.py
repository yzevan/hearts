from players.player import Player
from random import sample, choice
from card import Suit, Rank, Card, Deck
from rules import is_card_valid


class RandomPlayer(Player):

    """
    Most simple player you can think of.
    It just plays random valid cards.
    """

    def pass_cards(self, hand):
        return sample(hand, 3)

    def play_card(self, valid_cards, trick, out_of_suits, remaining_players, are_hearts_broken, is_spade_queen_played,  my_hand, cards_played, score_cards):
        return choice(valid_cards)