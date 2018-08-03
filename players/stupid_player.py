from players.player import Player
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid


class StupidPlayer(Player):

    """
    Most simple player you can think of.
    It just plays random valid cards.
    """

    def pass_cards(self, hand):
        return hand[:3]

    def play_card(self, hand, trick, trick_nr, are_hearts_broken, is_spade_queen_played):
        # Play first card that is valid
        for card in hand:
            if is_card_valid(hand, trick, card, trick_nr, are_hearts_broken):
                return card
        raise AssertionError(
            'Apparently there is no valid card that can be played. This should not happen.'
        )