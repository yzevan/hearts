"""This module containts the abstract class Player and some implementations."""
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid, cards_with_suit, get_largest_rank_with_smallest_length


class Player:

    """
    Abstract class defining the interface of a Computer Player.
    """

    def __repr__(self):
        return str(self.index)

    def __eq__(self, other):
        return self.index == other.index

    def __hash__(self):
        return hash(repr(self))

    def setIndex(self, index):
        self.index = index

    def expose(self):
        return False

    def pass_cards(self, hand):
        """Must return a list of three cards from the given hand."""
        hand_copy = hand[:]
        cards_to_pass = []
        for _ in range(3):
            spades_in_hand = cards_with_suit(Suit.spades, hand_copy)
            clubs_in_hand = cards_with_suit(Suit.clubs, hand_copy)
            if len(spades_in_hand) < 6 and Card(Suit.spades, Rank.queen) in spades_in_hand:
                card_to_pass = Card(Suit.spades, Rank.queen)
            elif len(spades_in_hand) < 6 and Card(Suit.spades, Rank.ace) in spades_in_hand:
                card_to_pass = Card(Suit.spades, Rank.ace)
            elif len(spades_in_hand) < 6 and Card(Suit.spades, Rank.king) in spades_in_hand:
                card_to_pass = Card(Suit.spades, Rank.king)
            elif len(clubs_in_hand) < 6 and Card(Suit.clubs, Rank.ten) in clubs_in_hand:
                card_to_pass = Card(Suit.clubs, Rank.ten)
            else:
                card_to_pass = get_largest_rank_with_smallest_length(hand_copy, [Suit.clubs, Suit.diamonds, Suit.hearts])
            cards_to_pass.append(card_to_pass)
            hand_copy.remove(card_to_pass)
        return cards_to_pass

    def play_card(self, valid_cards, trick, out_of_suits, remaining_players, are_hearts_broken, is_spade_queen_played, cards_played, cards_count, hand):
        """
        Must return a card from the given hand.
        trick is a list of cards played so far.
        trick can thus have 0, 1, 2, or 3 elements.
        are_hearts_broken is a boolean indicating whether the hearts are broken yet.
        trick_nr is an integer indicating the current trick number, starting with 0.
        """
        return NotImplemented