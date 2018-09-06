from players.player import Player
from random import shuffle
from card import Suit, Rank, Card, Deck
from rules import is_card_valid, is_last_turn, cards_with_suit, secondary_choice_needed, contains_unwanted_cards, get_largest_rank_with_smallest_length, get_unplayed_cards_with_suit
import variables
import logging
import sys


class AdvancedPlayer(Player):

    """
    This player has a notion of a card being undesirable.
    It will try to get rid of the most undesirable cards while trying not to win a trick.
    """

    def __init__(self):
        self.verbose = variables.verbose_advanced
        #self.my_hand = []
        #self.cards_played = ()

    #def setAttributes(self, my_hand, cards_played):                
        #self.my_hand = my_hand
        #self.cards_played = cards_played
        
    def say(self, message, *formatargs):
        if self.verbose:
            logging.debug(message.format(*formatargs))

    def undesirability(self, card):
        return card.rank.value
                    
    def calc_risk(self, suit, card, others_unplayed_cards_of_suit, out_of_suits, remaining_players):
        """
        """
        num_of_smaller_than_mine = 0
        for c in others_unplayed_cards_of_suit:
            if c < card:
                num_of_smaller_than_mine = num_of_smaller_than_mine + 1        
        
        out_of_suit_player_num = 0
        for player in remaining_players:
            if out_of_suits[player][suit]:
                out_of_suit_player_num = out_of_suit_player_num + 1
        others_unplayed_num = len(others_unplayed_cards_of_suit)
        weight = 0.01
        self.say("num_of_smaller_than_mine:{}, out_of_suit_player_num:{}, others_unplayed_num:{}", num_of_smaller_than_mine, out_of_suit_player_num, others_unplayed_num)
        if out_of_suit_player_num == 3:
            risk = 100
        else:
            risk = num_of_smaller_than_mine/(3-out_of_suit_player_num) + weight * others_unplayed_num/(3-out_of_suit_player_num)
        return risk
    
    def play_card(self, valid_cards, trick, out_of_suits, remaining_players, are_hearts_broken, is_spade_queen_played, my_hand, cards_played):
        self.say('Trick: {}', trick)
        self.say('Valid cards: {}', valid_cards)
        if len(valid_cards) == 1:
            return valid_cards[0]
        
        if trick:
            leading_suit = trick[0].suit
            decision = self.play_card_for_leading_suit(leading_suit, valid_cards, trick, out_of_suits, remaining_players, is_spade_queen_played, my_hand, cards_played)
        else:   #lead the trick
            #pick safe card first()
            if variables.advanced_formula: 
                #get valid suits first
                valid_suits = {}
                for c in valid_cards:
                    if c.suit not in valid_suits:
                        valid_suits[c.suit] = True
                
                risk = sys.maxsize
                decision = None
                for suit in valid_suits.keys():
                    my_cards_of_suit = cards_with_suit(suit, valid_cards)
                    if not my_cards_of_suit:
                        continue
                    #select min card of the suit and calculate the risk
                    card = my_cards_of_suit[0] 
                    others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                        cards_played, my_hand, 
                        suit)
                    card_risk = self.calc_risk(suit, card, others_unplayed_cards_of_suit, 
                                              out_of_suits, remaining_players)
                    #select a card with the lowest risk
                    self.say('card: {}, risk: {}', card, card_risk)
                    if card_risk < risk:
                        risk = card_risk
                        decision = card              

            else:            
                valid_cards_copy = valid_cards[:]
                valid_cards_copy.sort(key=self.undesirability)
                i = 0
                #TODO: use the min card that's not off-suit for all players
                while i < len(valid_cards_copy) and all([out_of_suits[player][valid_cards_copy[i].suit] for player in remaining_players]):
                    i += 1
                decision = valid_cards_copy[i] if i < len(valid_cards_copy) else valid_cards_copy[0]
        self.say('played card: {}', decision)
        return decision

    def play_card_for_leading_suit(self, suit, cards, trick, out_of_suits, remaining_players, is_spade_queen_played, my_hand, cards_played):
        cards_with_leading_suit = cards_with_suit(suit, cards)
        if cards_with_leading_suit:
            decision = self.best_available(suit, cards_with_leading_suit, trick, out_of_suits, remaining_players)
        else:  #off suit
            if Card(Suit.spades, Rank.queen) in cards:
                decision = Card(Suit.spades, Rank.queen)
            elif Card(Suit.clubs, Rank.ten) in cards:
                decision = Card(Suit.clubs, Rank.ten)
            elif Card(Suit.spades, Rank.ace) in cards and not is_spade_queen_played:
                decision = Card(Suit.spades, Rank.ace)
            elif Card(Suit.spades, Rank.king) in cards and not is_spade_queen_played:
                decision = Card(Suit.spades, Rank.king)
            else:
                valid_suits = {}
                for c in cards:
                    if c.suit not in valid_suits:
                        valid_suits[c.suit] = True
            
                risk = -1
                decision = None
                for suit in valid_suits.keys():
                    my_cards_of_suit = cards_with_suit(suit, cards)
                    if not my_cards_of_suit:
                        continue
                    #select max card of the suit and calculate the risk
                    card = my_cards_of_suit[-1]
                    others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                                    cards_played, my_hand, 
                                    suit)
                    card_risk = self.calc_risk_for_off_suit(suit, card, my_cards_of_suit, others_unplayed_cards_of_suit)
                    self.say('card: {}, risk: {}', card, card_risk)
                    #select a card with the lowest risk                    
                    if card_risk > risk:
                        risk = card_risk
                        decision = card                              
                    

        return decision
    
    def calc_risk_for_off_suit(self, suit, card, my_cards_of_suit, others_unplayed_cards_of_suit):
        risk = card.rank.value
        if card.suit == Suit.hearts:
            risk += 7
            
        #only 1 card left and there're several cards less than mine
        num_of_smaller_than_mine = 0
        for c in others_unplayed_cards_of_suit:
            if c < card:
                num_of_smaller_than_mine = num_of_smaller_than_mine + 1                
        if len(my_cards_of_suit)  == 1:
            if num_of_smaller_than_mine >=3:
                risk += 20
            elif num_of_smaller_than_mine > 0:
                risk += 10            

                
        return risk
        
        


    def best_available(self, suit, cards, trick, out_of_suits, remaining_players):
        #Play Q of spades and 10 of clubs if possbile        
        if suit == Suit.spades and Card(Suit.spades, Rank.queen) in cards and any( card.suit == suit and card.rank > Rank.queen for card in trick ):
            return Card(Suit.spades, Rank.queen)        
        if suit == Suit.clubs and Card(Suit.clubs, Rank.ten) in cards and any( card.suit == suit and card.rank > Rank.ten for card in trick):
            return Card(Suit.clubs, Rank.ten)
           
        if is_last_turn(trick) and not contains_unwanted_cards(trick):  #doesn't contain point cards, play max non-point card
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
                if is_last_turn(trick) or \
                   (contains_unwanted_cards(trick) and all([out_of_suits[player][suit] for player in remaining_players])):
                #(not contains_unwanted_cards(trick) and not any(out_of_suits[player][suit] for player in remaining_players)) or \                
                    decision = cards[-1] if not secondary_choice_needed(cards[-1], cards) else cards[-2] 
                else:
                    decision = cards[0] if not secondary_choice_needed(cards[0], cards) else cards[1]
        return decision
    
    #def best_available(self, suit, cards, trick, out_of_suits, remaining_players):
        #if is_last_turn(trick) and not contains_unwanted_cards(trick):
            #if not secondary_choice_needed(cards[-1], cards) or any(card.rank > cards[-1].rank for card in cards):
                #decision = cards[-1]
            #else:
                #decision = cards[-2]
        #else:
            #cards_with_suit_in_trick = cards_with_suit(suit, trick)
            #max_rank_in_leading_suit = max([card.rank for card in cards_with_suit_in_trick])
            #safe_cards = [card for card in cards if card.rank < max_rank_in_leading_suit]
            #if safe_cards:
                #decision = safe_cards[-1]
            #else:
                #if is_last_turn(trick) or (not contains_unwanted_cards and not any(out_of_suits[player][suit] for player in remaining_players)) or (contains_unwanted_cards and all([out_of_suits[player][suit] for player in remaining_players])):
                    #decision = cards[-1] if not secondary_choice_needed(cards[-1], cards) else cards[-2] 
                #else:
                    #decision = cards[0] if not secondary_choice_needed(cards[0], cards) else cards[1]
        #return decision