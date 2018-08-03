from players.player import Player
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid


class AdvancedPlayer(Player):

    """
    This player has a notion of a card being undesirable.
    It will try to get rid of the most undesirable cards while trying not to win a trick.
    """

    def __init__(self, verbose=True):
        self.verbose = verbose

    def say(self, message, *formatargs):
        if self.verbose:
            print(message.format(*formatargs))

    def undesirability(self, card):
        return card.rank.value

    def pass_cards(self, hand):
        self.say('Hand before passing: {}', hand)
        hand_copy = hand.copy()
        cards_to_pass = []
        for _ in range(0, 3):
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
                suits_array = [x for x in other_suits_in_hand if x]
                min_suit_array = min(suits_array, key=len)
                card_to_pass = min_suit_array[-1]
            cards_to_pass.append(card_to_pass)
            hand_copy.remove(card_to_pass)
        self.say('Cards to pass: {}', cards_to_pass)
        return cards_to_pass
                    
    def play_card(self, hand, trick, trick_nr, are_hearts_broken, is_spade_queen_played):
        if trick_nr == 0:
            hand.sort()
        self.say('Hand: {}', hand)
        valid_cards = [card for card in hand
                       if is_card_valid(hand, trick, card, trick_nr, are_hearts_broken)]
        self.say('Valid cards: {}', valid_cards)
        if trick_nr == 0:
            decision = self.play_card_for_first_trick(valid_cards)
        elif trick:
            leading_suit = trick[0].suit
            decision = self.play_card_for_leading_suit(leading_suit, valid_cards, trick, is_spade_queen_played)
        else:
            valid_cards_copy = valid_cards.copy()
            valid_cards_copy.sort(key=self.undesirability)
            decision = valid_cards_copy[0]
        self.say('played card {} to the trick {}.', decision, trick)
        return decision

    def cards_with_suit(self, suit, cards):
        return [card for card in cards if card.suit == suit]

    def play_card_for_first_trick(self, cards):
        if Card(Suit.clubs, Rank.two) in cards:
            return Card(Suit.clubs, Rank.two)
        elif self.cards_with_suit(Suit.clubs, cards):
            return self.cards_with_suit(Suit.clubs, cards)[-1]
        elif Card(Suit.spades, Rank.ace) in cards:
            return Card(Suit.spades, Rank.ace)
        elif Card(Suit.spades, Rank.king) in cards:
            return Card(Suit.spades, Rank.king)
        elif self.cards_with_suit(Suit.diamonds, cards):
            return self.cards_with_suit(Suit.diamonds, cards)[-1]
        elif self.cards_with_suit(Suit.spades, cards):
            return self.cards_with_suit(Suit.spades, cards)[-1]
        else:
            return cards[-1]

    def play_card_for_leading_suit(self, suit, cards, trick, is_spade_queen_played):
        cards_with_leading_suit = self.cards_with_suit(suit, cards)
        if cards_with_leading_suit:
            if len(trick) == 3:
                if self.cards_with_suit(Suit.hearts, trick) or Card(Suit.spades, Rank.queen) in trick:
                    decision = self.best_available(suit, cards_with_leading_suit, trick)
                else:
                    decision = cards_with_leading_suit[-1]
                if decision == Card(Suit.spades, Rank.queen) and len(cards_with_leading_suit) > 1:
                    decision = cards_with_leading_suit[-2]
            else:
                decision = self.best_available(suit, cards_with_leading_suit, trick)
        else:
            if Card(Suit.spades, Rank.queen) in cards:
                decision = Card(Suit.spades, Rank.queen)
            elif Card(Suit.spades, Rank.ace) in cards and not is_spade_queen_played:
                decision = Card(Suit.spades, Rank.ace)
            elif Card(Suit.spades, Rank.king) in cards and not is_spade_queen_played:
                decision = Card(Suit.spades, Rank.king)
            else:
                cards_copy = cards.copy()
                cards_copy.sort(key=self.undesirability)
                decision = cards_copy[-1]
        return decision

    def best_available(self, suit, cards, trick):
        cards_with_suit_in_trick = self.cards_with_suit(suit, trick)
        max_rank_in_leading_suit = max([card.rank for card in cards_with_suit_in_trick])
        safe_cards = [card for card in cards if card.rank < max_rank_in_leading_suit]
        if safe_cards:
            decision = safe_cards[-1]
        else:
            if len(trick) == 3:
                decision = cards[-1]
            else:
                decision = cards[0]
        return decision