from players.player import Player
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid


class MinPlayer(Player):

    """
    This player has a notion of a card being undesirable.
    It will try to get rid of the most undesirable cards while trying not to win a trick.
    """

    def play_card(self, valid_cards, trick, out_of_suits, remaining_players, are_hearts_broken, is_spade_queen_played, cards_played, cards_count, hand):
        return valid_cards[0]