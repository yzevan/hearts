from players.player import Player
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid


class ExpertPlayer(Player):

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
        return (
            card.rank.value
            + (10 if card.suit == Suit.spades and card.rank >= Rank.queen else 0)
        )

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
                other_suits_in_hand = [self._cards_with_suit(Suit.clubs, hand_copy), self._cards_with_suit(Suit.diamonds, hand_copy), self._cards_with_suit(Suit.hearts, hand_copy)]
                suits_array = [x for x in other_suits_in_hand if len(x) != 0]
                min_suit_array = min(suits_array, key=len)
                card_to_pass = min_suit_array[-1]
            cards_to_pass.append(card_to_pass)
            hand_copy.remove(card_to_pass)
        self.say('Cards to pass: {}', cards_to_pass)
        return cards_to_pass
                    
    def play_card(self, hand, trick, trick_nr, are_hearts_broken):
        # Lead with a low card
        if not trick:
            hand.sort(key=lambda card:
                      100 if not are_hearts_broken and card.suit == Suit.hearts else
                      card.rank.value)
            return hand[0]

        hand.sort(key=self.undesirability, reverse=True)
        self.say('Hand: {}', hand)
        self.say('Trick so far: {}', trick)

        # Safe cards are cards which will not result in winning the trick
        leading_suit = trick[0].suit
        max_rank_in_leading_suit = max([card.rank for card in trick
                                        if card.suit == leading_suit])
        valid_cards = [card for card in hand
                       if is_card_valid(hand, trick, card, trick_nr, are_hearts_broken)]
        safe_cards = [card for card in valid_cards
                      if card.suit != leading_suit or card.rank <= max_rank_in_leading_suit]

        self.say('Valid cards: {}', valid_cards)
        self.say('Safe cards: {}', safe_cards)

        try:
            return safe_cards[0]
        except IndexError:
            queen_of_spades = Card(Suit.spades, Rank.queen)
            # Don't try to take a trick by laying the queen of spades
            if valid_cards[0] == queen_of_spades and len(valid_cards) > 1:
                return valid_cards[1]
            else:
                return valid_cards[0]

    def _cards_with_suit(self, suit, cards):
        return [card for card in cards if card.suit == suit]