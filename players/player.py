"""This module containts the abstract class Player and some implementations."""
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid


class Player:

    """
    Abstract class defining the interface of a Computer Player.
    """

    def pass_cards(self, hand):
        """Must return a list of three cards from the given hand."""
        return NotImplemented

    def play_card(self, hand, trick, trick_nr, are_hearts_broken):
        """
        Must return a card from the given hand.
        trick is a list of cards played so far.
        trick can thus have 0, 1, 2, or 3 elements.
        are_hearts_broken is a boolean indicating whether the hearts are broken yet.
        trick_nr is an integer indicating the current trick number, starting with 0.
        """
        return NotImplemented

    def all_valid_cards(self, hand, trick, trick_nr, are_hearts_broken):
        return [card for card in hand
                       if is_card_valid(hand, trick, card, trick_nr, are_hearts_broken)]