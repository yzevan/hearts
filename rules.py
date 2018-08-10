"""
This module contains a few functions comprising the rules of the game.
"""

from card import Suit, Rank, Card

def is_card_valid(hand, trick, card, trick_nr, are_hearts_broken):
    """
    Return True if the given card is valid to play in given context, False otherwise.
    """
    # No points allowed in first trick
    if trick_nr == 0 and not trick:
        return card == Card(Suit.clubs, Rank.two)

    if trick_nr == 0 and all([card.suit == Suit.hearts for card in hand]):
        return True

    if trick_nr == 0 and card_point(card, False) < 0:
        return False

    # No hearts can be led until hearts are broken
    if not trick:
        return are_hearts_broken or (
            not are_hearts_broken and (card.suit != Suit.hearts
                                       or all([card.suit == Suit.hearts for card in hand]))
        )

    # Suit must be followed unless player has none of that suit
    leading_suit = trick[0].suit
    return card.suit == leading_suit or all([card.suit != leading_suit for card in hand])

def card_point(card, exposed):
    """
    Return the number of points given card is worth.
    """
    if card == Card(Suit.spades, Rank.queen):
        return -13
    if card.suit == Suit.hearts:
        return (-2 if exposed else -1)
    return 0

def is_last_trick(trick):
    return len(trick) == 3

def count_points(cards_taken, exposed):
    """
    Count the number of points in cards, where cards is a list of Cards.
    """
    points = [0, 0, 0, 0]
    shooting_the_moon = False
    for i, cards in enumerate(cards_taken):
        points[i] = sum(card_point(card, exposed) for card in cards)
        if ((not shooting_the_moon) and all([(card.suit == Suit.hearts or card == Card(Suit.spades, Rank.queen)) for card in cards])):
            shooting_the_moon = True
            shooting_the_moon_player = i
    if shooting_the_moon:
        winning_point = points[shooting_the_moon_player]
        points[i] = (0 if i == shooting_the_moon_player else winning_point)
    # print(points)
    return points