"""This module containts the abstract class Player and some implementations."""
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid


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

    def pass_cards(self, hand):
        """Must return a list of three cards from the given hand."""
        hand_copy = hand[:]
        cards_to_pass = []
        for _ in range(3):
            spades_in_hand = [card for card in hand_copy if card.suit == Suit.spades]
            if len(spades_in_hand) < 6 and Card(Suit.spades, Rank.queen) in spades_in_hand:
                card_to_pass = Card(Suit.spades, Rank.queen)
            elif len(spades_in_hand) < 6 and Card(Suit.spades, Rank.ace) in spades_in_hand:
                card_to_pass = Card(Suit.spades, Rank.ace)
            elif len(spades_in_hand) < 6 and Card(Suit.spades, Rank.king) in spades_in_hand:
                card_to_pass = Card(Suit.spades, Rank.king)
            else:
                other_suits_in_hand = [self.cards_with_suit(Suit.clubs, hand_copy), 
                                       self.cards_with_suit(Suit.diamonds, hand_copy),
                                       self.cards_with_suit(Suit.hearts, hand_copy)]
                other_suits_in_hand.sort(key=len, reverse=True)
                other_suits_in_hand_flatten = [card for cards in other_suits_in_hand for card in cards]
                other_suits_in_hand_flatten.sort(key=lambda card: card.rank.value)
                card_to_pass = other_suits_in_hand_flatten[-1]
            cards_to_pass.append(card_to_pass)
            hand_copy.remove(card_to_pass)
        return cards_to_pass
    
    def cards_with_suit(self, suit, cards):
        return [card for card in cards if card.suit == suit]

    def play_card(self, hand, trick, trick_nr, are_hearts_broken, is_spade_queen_played):
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