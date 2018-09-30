"""
This module contains a few functions comprising the rules of the game.
"""

from card import Suit, Rank, Card
import logging

def is_card_valid(hand, trick, card, trick_nr, are_hearts_broken):
    """
    Return True if the given card is valid to play in given context, False otherwise.
    """
    # No points allowed in first trick
    if trick_nr == 0 and not trick:
        return card == Card(Suit.clubs, Rank.two)

    if trick_nr == 0 and all([card.suit == Suit.hearts for card in hand]):
        return True

    if trick_nr == 0 and card_point(card) < 0:
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

def card_point(card, exposed = False):
    """
    Return the number of points given card is worth.
    """
    if card == Card(Suit.spades, Rank.queen):
        return -13
    if card.suit == Suit.hearts:
        return -2 if exposed else -1
    return 0

def is_last_turn(trick):
    return len(trick) == 3

def count_points(cards_taken, exposed):
    """
    Count the number of points in cards, where cards is a list of Cards.
    """
    points = [0, 0, 0, 0]
    shoot_the_moon_list = [0, 0, 0, 0]
    shooting_the_moon = False
    club_ten_holder = 0
    for i, cards in enumerate(cards_taken):
        points[i] = sum(card_point(card, exposed) for card in cards)
        if (Card(Suit.clubs, Rank.ten) in cards):
            points[i] = points[i] * 2
            club_ten_holder = i
        if (not shooting_the_moon) and Card(Suit.spades, Rank.queen) in cards \
            and all([ Card(Suit.hearts, rank) in cards for rank in Rank]):
            shooting_the_moon = True
            shooting_the_moon_player = i
    if shooting_the_moon:
        winning_point = points[shooting_the_moon_player] * 2
        points[i] = (0 if i == shooting_the_moon_player else (winning_point * 2 if i == club_ten_holder else winning_point))
        shoot_the_moon_list[shooting_the_moon_player] = 1        
        logging.info('player {} shoot the moon successfully'.format(shooting_the_moon_player))
       
    return points, shoot_the_moon_list

def are_hearts_broken(cards):
    """
    Return True if the hearts are broken yet, otherwise return False.
    """
    return any(card.suit == Suit.hearts for card in cards)

def is_spade_queen_played(cards):
    """
    Return True if the spade queen is played yet, otherwise return False.
    """
    return Card(Suit.spades, Rank.queen) in cards

def cards_with_suit(suit, cards):
    return [card for card in cards if card.suit == suit]
    
def all_valid_cards(hand, trick, trick_nr, are_hearts_broken):
    return [card for card in hand
                    if is_card_valid(hand, trick, card, trick_nr, are_hearts_broken)]

def secondary_choice_needed(decision, cards):
    return decision in [Card(Suit.spades, Rank.queen), Card(Suit.clubs, Rank.ten)] and len(cards) > 1

def contains_unwanted_cards(cards):
    return (len(cards_with_suit(Suit.hearts, cards)) > 0) or (Card(Suit.spades, Rank.queen) in cards) or (Card(Suit.clubs, Rank.ten) in cards)
def contains_score_cards(cards):
    return (len(cards_with_suit(Suit.hearts, cards)) > 0) or (Card(Suit.spades, Rank.queen) in cards)


def get_largest_rank_with_smallest_length(cards, suits = "all"):
    if suits == "all":
        suits = [Suit.clubs, Suit.diamonds, Suit.spades, Suit.hearts]
    cards_for_suit = [cards_with_suit(suit, cards) for suit in suits]
    cards_for_suit.sort(key=len, reverse=True)
    cards_for_suit_flatten = [card for cards in cards_for_suit for card in cards]
    cards_for_suit_flatten.sort(key=lambda card: card.rank.value)
    return cards_for_suit_flatten[-1]

def get_smallest_rank_cards(cards, number):
    return sorted(cards, key=lambda card: card.rank.value)[0:number]

def str_to_card(s):
    str_to_suit = {
        "C": Suit.clubs,
        "D": Suit.diamonds,
        "S": Suit.spades,
        "H": Suit.hearts
    }
    str_to_rank = {
        "2": Rank.two,
        "3": Rank.three,
        "4": Rank.four,
        "5": Rank.five,
        "6": Rank.six,
        "7": Rank.seven,
        "8": Rank.eight,
        "9": Rank.nine,
        "T": Rank.ten,
        "J": Rank.jack,
        "Q": Rank.queen,
        "K": Rank.king,
        "A": Rank.ace
    }
    return Card(str_to_suit[s[1]], str_to_rank[s[0]])

def get_unplayed_cards_with_suit(played_cards, my_hand, suit):
    """
    Get unplayed cards of a suit
    """
    unplayed_cards = []
    for rank in Rank:
        card = Card(suit, rank)
        if card not in played_cards and card not in my_hand:
            unplayed_cards.append(card)
        
    return unplayed_cards

def is_others_off_suit(suit, out_of_suits, my_name):
    """
    suit:
    out_of_suits: a dict to store all players out of suit info,whose value is also a dict. e.g. out_of_suits['player']['suit'] = True/False
    my_name:
    """
    return all([out_of_suits[player][suit] for player in out_of_suits if player != my_name ])

def is_larger_than_others(my_card, my_hand, played_cards):
    suit = my_card.suit
    others_played_cards_of_suit = cards_with_suit(suit, played_cards)
    others_unplayed_cards_of_suit = [ Card(suit, rank) for rank in Rank if Card(suit, rank) not in my_hand and Card(suit, rank) not in played_cards]
    return all([ my_card > other for other in others_unplayed_cards_of_suit])

def is_smaller_than_others(card, my_hand, played_cards):
    suit = my_card.suit
    others_played_cards_of_suit = cards_with_suit(suit, played_cards)
    others_unplayed_cards_of_suit = [ Card(suit, rank) for rank in Rank if Card(suit, rank) not in my_hand and Card(suit, rank) not in played_cards]
    return all([ my_card < other for other in others_unplayed_cards_of_suit])

def get_min_rank_card(cards):
    """
    return min rank card of cards with different suits.
    If mutliple suits have the same rank, only return last one
    """
    min_rank = Rank.ace
    min_card = None
    
    for card in cards:
        if card.rank <= min_rank:
            min_rank = card.rank
            min_card = card
    return min_card

def get_suits_from_cards(cards):
    """
    return suit list from cards
    """
    suits = []
    for card in cards:
        if card.suit not in suits:
            suits.append(card.suit)
            
    return suits
    
            



if __name__ == "__main__":
    cards = [Card(Suit.spades, Rank.two), Card(Suit.hearts, Rank.three), Card(Suit.spades, Rank.ten)]
    print(get_suits_from_cards(cards))
    
        