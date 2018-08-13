from players.player import Player
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid, is_last_trick, cards_with_suit, secondary_choice_needed, contains_unwanted_cards
import variables
import logging


class AdvancedPlayer(Player):

    """
    This player has a notion of a card being undesirable.
    It will try to get rid of the most undesirable cards while trying not to win a trick.
    """

    def __init__(self):
        self.verbose = variables.verbose_advanced

    def say(self, message, *formatargs):
        if self.verbose:
            logging.debug(message.format(*formatargs))

    def undesirability(self, card):
        return card.rank.value
                    
    def play_card(self, valid_cards, trick, are_hearts_broken, is_spade_queen_played):
        self.say('Trick: {}', trick)
        self.say('Valid cards: {}', valid_cards)
        if trick:
            leading_suit = trick[0].suit
            decision = self.play_card_for_leading_suit(leading_suit, valid_cards, trick, is_spade_queen_played)
        else:
            valid_cards_copy = valid_cards[:]
            valid_cards_copy.sort(key=self.undesirability)
            decision = valid_cards_copy[0]
        self.say('played card: {}', decision)
        return decision

    def play_card_for_leading_suit(self, suit, cards, trick, is_spade_queen_played):
        cards_with_leading_suit = cards_with_suit(suit, cards)
        if cards_with_leading_suit:
            decision = self.best_available(suit, cards_with_leading_suit, trick)
        else:
            if Card(Suit.spades, Rank.queen) in cards:
                decision = Card(Suit.spades, Rank.queen)
            elif Card(Suit.clubs, Rank.ten) in cards:
                decision = Card(Suit.clubs, Rank.ten)
            elif Card(Suit.spades, Rank.ace) in cards and not is_spade_queen_played:
                decision = Card(Suit.spades, Rank.ace)
            elif Card(Suit.spades, Rank.king) in cards and not is_spade_queen_played:
                decision = Card(Suit.spades, Rank.king)
            else:
                cards_copy = cards[:]
                cards_copy.sort(key=self.undesirability)
                decision = cards_copy[-1]
        return decision

    def best_available(self, suit, cards, trick):
        if is_last_trick(trick) and not contains_unwanted_cards(trick):
            if not secondary_choice_needed(cards[-1], cards) or any(card.rank > cards[-1].rank for card in cards):
                decision = cards[-1]
            else:
                decision = cards[-2]
        else:
            cards_with_suit_in_trick = cards_with_suit(suit, trick)
            max_rank_in_leading_suit = max([card.rank for card in cards_with_suit_in_trick])
            safe_cards = [card for card in cards if card.rank < max_rank_in_leading_suit]
            if safe_cards:
                decision = safe_cards[-1]
            else:
                if is_last_trick(trick):
                    decision = cards[-1] if not secondary_choice_needed(cards[-1], cards) else cards[-2]
                else:
                    decision = cards[0] if not secondary_choice_needed(cards[0], cards) else cards[1]
        return decision