from players.player import Player
from random import shuffle
from card import Suit, Rank, Card, Deck
#from rules import is_card_valid, is_last_turn, cards_with_suit, secondary_choice_needed, contains_unwanted_cards, get_largest_rank_with_smallest_length, get_unplayed_cards_with_suit, contains_score_cards, get_smallest_rank_cards, str_to_card
from rules import *

import variables
import logging
import sys
import math


class AdvancedPlayer(Player):

    """
    This player has a notion of a card being undesirable.
    It will try to get rid of the most undesirable cards while trying not to win a trick.
    """

    def __init__(self, name = ''):
        self.verbose = variables.verbose_advanced
        self.try_to_shoot = 0
        self.name = name
        self.suit_strength= {}
        #self.my_hand = []
        #self.cards_played = ()

    #def setAttributes(self, my_hand, cards_played):                
        #self.my_hand = my_hand
        #self.cards_played = cards_played
        
    def say(self, message, *formatargs):
        if self.verbose:
            logging.info(message.format(*formatargs))
        
        
    def pass_cards(self, my_hand):
        """Must return a list of three cards from the given hand."""
        self.say('Start to pass cards......')
        if not variables.enable_shoot_the_moon:
            return super(AdvancedPlayer, self).pass_cards(my_hand)
        
        hand_copy = my_hand[:]
        #select 3 weakest cards and caculate suit strength if they are got rid of
        pass_cards = []
        cards_played = []
        for _ in range(0,3):
            card = self.get_weakest_card(hand_copy, pass_cards, {})
            pass_cards.append(card)
            hand_copy.remove(card)
        self.say('check_shoot: prepare to select 3 cards:{}', pass_cards)
        
        self.check_shoot_the_moon(hand_copy, cards_played, [], {})
        #my_suits = {}
        #for card in hand_copy:
            #if card.suit not in my_suits:
                #my_suits[card.suit] = 0
                
        
        #for suit in my_suits.keys():
            #suit_cards = cards_with_suit(suit, hand_copy)
            #suit_cards.sort()
            #others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                #[], hand_copy, 
                #suit)
            #suit_strenth = self.calc_suit_strength(suit, suit_cards, 
                                              #others_unplayed_cards_of_suit, {} )
            #self.say('suit {}, suit strength: {}', suit, suit_strenth)
            #if not others_unplayed_cards_of_suit:
                #my_suits[suit] = 1
                #self.say('check_shoot: {} is offsuit', suit)
            #elif all(other.rank < my_card.rank for other in others_unplayed_cards_of_suit for my_card in suit_cards):
                #my_suits[suit] = 1
                #self.say('check_shoot: {} cards are the largest', suit)
            ##elif all(other.rank < suit_cards[-1].rank for other in others_unplayed_cards_of_suit):
            #elif suit_strenth > 0.5:
                #my_suits[suit] = 1
                #self.say('check_shoot: {} has a max card and high suit strength are the largest', suit)
            #elif all(other.rank < suit_cards[-1].rank for other in others_unplayed_cards_of_suit) \
                 #and len(suit_cards) > 5: 
                #my_suits[suit] = 1
                #self.say('check_shoot: {} has a max card and high suit card number', suit)
                     
        #if all suits are strong enough
        #if sum(my_suits[suit] for suit in my_suits) > 2:
            #self.try_to_shoot = 1
            #self.say('NOTE: Switch to shoot the moon. My hand:{}', my_hand)                        

        if self.try_to_shoot == 1:           
            self.say('Try to shoot the moon: pass small cards.')
        else:
            #pass_cards = super(AdvancedPlayer, self).pass_cards(my_hand)
            
            hand_copy = my_hand[:]
            pass_cards = []
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
                    card_to_pass = self.get_strongest_card(hand_copy, 
                        pass_cards, 
                        {})
                pass_cards.append(card_to_pass)
                hand_copy.remove(card_to_pass)
                
        self.say('passed cards:{}', pass_cards)
        return pass_cards
    
    def undesirability(self, card):
        return card.rank.value
                    

    
      
    
    def play_card(self, valid_cards, trick, out_of_suits, remaining_players, are_hearts_broken, is_spade_queen_played, my_hand, cards_played, score_cards):
        self.say('Trick: {}', trick)
        self.say('Valid cards: {}', valid_cards)
        self.say('my_hand: {}', sorted(my_hand))
        self.say('cards_played: {}', sorted(cards_played))
        self.say('score_cards: {}', score_cards)
        
        if len(valid_cards) == 1:
            return valid_cards[0]
        
        #update out_of_suits
        #check if palyers are out of suit after the turn card is played        
        for suit in Suit:
            found = False    
            for rank in Rank:
                card = Card(suit, rank)
                if card not in cards_played and card not in my_hand:
                    found = True
                    break
            if not found:  #if there's no card which is played or in my hand, that means all other players are out of the suit            
                for player_name in out_of_suits:
                    if player_name != self.name:
                        out_of_suits[player_name][suit] = True
                        
        self.check_shoot_the_moon(my_hand, cards_played, score_cards, out_of_suits)
                
        if variables.enable_shoot_the_moon and self.try_to_shoot == 1:
            self.say("NOTE: try to shoot the moon. My hand:{}", my_hand)
            if trick:
                leading_suit = trick[0].suit
                decision = self.shoot_follow_trick(leading_suit, valid_cards, trick, out_of_suits, remaining_players, is_spade_queen_played, my_hand, cards_played)
            else:
                decision = self.shoot_lead_trick(valid_cards, out_of_suits, remaining_players, is_spade_queen_played, my_hand, cards_played)
        else:
            if trick:
                leading_suit = trick[0].suit
                cards_with_leading_suit = cards_with_suit(leading_suit, valid_cards)
                if cards_with_leading_suit:
                    self.say('NOTE: play the trick suit')
                    decision = self.best_available(leading_suit, cards_with_leading_suit, trick, out_of_suits, remaining_players)
                else:  #off suit
                    decision = self.play_card_for_offsuit( valid_cards, my_hand, cards_played, is_spade_queen_played, out_of_suits)                    
                
            else:   #lead the trick
                self.say('NOTE: lead the trick')
                decision = self.lead_trick(valid_cards, 
                                                     out_of_suits, 
                                                     remaining_players, 
                                                     my_hand, 
                                                     cards_played)
        self.say('played card: {}', decision)
        return decision

    def lead_trick(self, valid_cards, out_of_suits, remaining_players, my_hand, cards_played):
        suits = get_suits_from_cards(valid_cards)                        

            
        risk = sys.maxsize
        decision = None
        for suit in suits:
            my_cards_of_suit = cards_with_suit(suit, valid_cards)
            if not my_cards_of_suit:
                continue
            #select min card of the suit and calculate the risk
            card = my_cards_of_suit[0] 
            others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                                cards_played, my_hand, 
                                suit)
            #if I have QS/TC, and they are the smallest, play it first    
            if len(others_unplayed_cards_of_suit)>0 and (Card(Suit.spades, Rank.queen) in my_cards_of_suit) and all( [other.rank > Rank.queen for other in others_unplayed_cards_of_suit]):
                return Card(Suit.spades, Rank.queen)            
            if len(others_unplayed_cards_of_suit)>0 and (Card(Suit.clubs, Rank.ten) in my_cards_of_suit) and all( [other.rank > Rank.ten for other in others_unplayed_cards_of_suit]):
                return Card(Suit.clubs, Rank.ten)   
            
            #if the only unplayed card is QS/TC, and my card is smaller than that, force it out
            if len(others_unplayed_cards_of_suit)==1 and others_unplayed_cards_of_suit[0] == Card(Suit.spades, Rank.queen) and card.rank < Rank.queen:
                return card
            if len(others_unplayed_cards_of_suit)==1 and others_unplayed_cards_of_suit[0] == Card(Suit.clubs, Rank.ten) and card.rank < Rank.ten:
                return card          
    

        if len(suits) > 1 and Suit.spades in suits and Card(Suit.spades, Rank.queen) in my_hand:
            suits.remove(Suit.spades)
                
        for suit in suits:
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
            elif card_risk == risk:
                if Card(Suit.spades, Rank.queen) in others_unplayed_cards_of_suit:
                    if all([c.rank < Rank.queen for c in my_cards_of_suit] ) or len([c for c in my_cards_of_suit if c.rank < Rank.queen]) >= len(others_unplayed_cards_of_suit):
                        risk = card_risk
                        decision = card
                elif Card(Suit.clubs, Rank.ten) in others_unplayed_cards_of_suit and card.rank < Rank.ten:
                    risk = card_risk
                    decision = card
                    
        return decision      

    
    def play_card_for_offsuit(self, cards, my_hand, cards_played, is_spade_queen_played, out_of_suits):
        self.say('NOTE: play off suit')
        if Card(Suit.spades, Rank.queen) in cards:
            return Card(Suit.spades, Rank.queen)
        if Card(Suit.clubs, Rank.ten) in cards:
            return Card(Suit.clubs, Rank.ten)
        if Card(Suit.spades, Rank.ace) in cards and not is_spade_queen_played:
            return Card(Suit.spades, Rank.ace)
        if Card(Suit.spades, Rank.king) in cards and not is_spade_queen_played:
            return Card(Suit.spades, Rank.king)
        
        suits = get_suits_from_cards(cards)
        if len(suits) == 1:
            return cards_with_suit(suits[0], cards)[-1]           
        
        #remove the suits that others don't have
        suits = [ suit for suit in suits if not is_others_off_suit(suit, out_of_suits, self.name)]
        if not suits:   #all my valid cards are offsuit, play any one
            return cards[0]                                                        
        
        # candidate cards are max cards of each suits
        candidate_cards = [ cards_with_suit(suit, cards)[-1] for suit in suits ]
        suit_safe_cards = {}
        suit_strength = {}
        suit_cards_cnt = {}
        card_strength = {}
        smaller_than_mine = {}
        larger_than_mine = {}
        for card in candidate_cards:
            my_cards_of_suit = cards_with_suit(card.suit, cards)
            others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(cards_played, my_hand, card.suit)
            safe_card_num = len([ card for card in my_cards_of_suit if card < min(others_unplayed_cards_of_suit)])
            suit_safe_cards[card] = safe_card_num
            
            suit_strength[card] = self.calc_suit_strength(card.suit, my_cards_of_suit, others_unplayed_cards_of_suit, out_of_suits)
            num_of_mine = len(my_cards_of_suit)
            suit_cards_cnt[card] = num_of_mine
            
            num_of_smaller_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank < card.rank])
            smaller_than_mine[card] = num_of_smaller_than_mine
            
            num_of_larger_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank > card.rank])
            larger_than_mine[card] = num_of_larger_than_mine
            
            suit_risk = self.calc_suit_risk(my_cards_of_suit, others_unplayed_cards_of_suit)
            self.say('suit {}, suit risk: {}', card.suit, suit_risk)            
            card_risk = self.calc_risk_for_off_suit(card, num_of_mine, num_of_smaller_than_mine , num_of_larger_than_mine, suit_risk)
            self.say('card: {}, risk: {}', card, card_risk)
            card_strength[card] = card_risk
            
        #select the suit with least safe cards 
        min_safe_card_num = suit_safe_cards[min(suit_safe_cards, key=suit_safe_cards.get)]
        candidate_cards = [ card for card in candidate_cards if suit_safe_cards[card]==min_safe_card_num]
        if len(candidate_cards) == 1:
            return candidate_cards[0]
        
                
    
        #select the suit I have 1 card and it's not the smallest
        
        #select max card strength
        card_strength = {k:v for k,v in card_strength.items() if k in candidate_cards}
        max_card_strength = card_strength[max((card_strength), key=card_strength.get)]
        candidate_cards = [ card for card in candidate_cards if card_strength[card]==max_card_strength]
        if len(candidate_cards) == 1:
            return candidate_cards[0]
        
        
        self.say('candidate cards: {}', candidate_cards)
        #select the suit with max strength 
        suit_strength = {k:v for k,v in suit_strength.items() if k in candidate_cards}
        max_suit_strength = suit_strength[max(suit_strength, key=suit_strength.get)]
        candidate_cards = [ card for card in candidate_cards if suit_strength[card]==max_suit_strength]
        if len(candidate_cards) == 1:
            return candidate_cards[0]
        
        #play hearts card
        hearts_card = [ card for card in candidate_cards if card.suit == Suit.hearts]
        if hearts_card:
            return hearts_card[0]
        
        #play the suit with min cards
        suit_cards_cnt = {k:v for k,v in suit_cards_cnt.items() if k in candidate_cards}
        min_suit_cnt = suit_cards_cnt[min(suit_cards_cnt, key=suit_cards_cnt.get)]
        candidate_cards = [ card for card in candidate_cards if suit_cards_cnt[card]==min_suit_cnt]
        return candidate_cards[0]           
            
                
            
        
        #risk = -1
        #decision = None
        #for suit in suits:
            #my_cards_of_suit = cards_with_suit(suit, cards)
            #if not my_cards_of_suit:
                #continue
            ##select max card of the suit and calculate the risk
            #card = my_cards_of_suit[-1]
            #others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                            #cards_played, my_hand, 
                            #suit)
            #num_of_mine = len(my_cards_of_suit)
            #num_of_smaller_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank < card.rank])
            #num_of_larger_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank > card.rank])
            #suit_risk = self.calc_suit_risk(my_cards_of_suit, others_unplayed_cards_of_suit)
            #self.say('suit {}, suit risk: {}', card.suit, suit_risk)
            
            #card_risk = self.calc_risk_for_off_suit(card, num_of_mine, num_of_smaller_than_mine , num_of_larger_than_mine, suit_risk)
            #self.say('card: {}, risk: {}', card, card_risk)
            ##select a card with the lowest risk                    
            #if card_risk > risk:
                #risk = card_risk
                #decision = card    
        #return decision
    
    def calc_risk(self, suit, card, others_unplayed_cards_of_suit, out_of_suits, remaining_players):
        """
        """
      
        num_of_smaller_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank < card.rank])
        num_of_larger_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank > card.rank])        
        out_of_suit_player_num = 0
        for player in remaining_players:
            if out_of_suits[player][suit]:
                out_of_suit_player_num = out_of_suit_player_num + 1
        others_unplayed_num = len(others_unplayed_cards_of_suit)
        weight = 0.01
        self.say("num_of_smaller_than_mine:{}, out_of_suit_player_num:{}, others_unplayed_num:{}", num_of_smaller_than_mine, out_of_suit_player_num, others_unplayed_num)
        if out_of_suit_player_num == 3: #avoid playing card that's off suit for others
            risk = 100
        elif num_of_larger_than_mine == 0:  #avoid playing card that's largest in a suit
            risk = 99
        else:
            #risk = num_of_smaller_than_mine/(3-out_of_suit_player_num) + weight * others_unplayed_num/(3-out_of_suit_player_num)
            risk = num_of_smaller_than_mine/(3-out_of_suit_player_num)
        return risk    
    
    def calc_card_strength(self, suit, card, others_unplayed_cards_of_suit, out_of_suits, remaining_players):
        """
        """
      
        num_of_smaller_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank < card.rank])
        num_of_larger_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank > card.rank])        
        out_of_suit_player_num = 0
        for player in remaining_players:
            if out_of_suits[player][suit]:
                out_of_suit_player_num = out_of_suit_player_num + 1
        others_unplayed_num = len(others_unplayed_cards_of_suit)
        weight = 0.01
        self.say("num_of_smaller_than_mine:{}, out_of_suit_player_num:{}, others_unplayed_num:{}", num_of_smaller_than_mine, out_of_suit_player_num, others_unplayed_num)
        if out_of_suit_player_num == 3: #avoid playing card that's off suit for others
            risk = 100
        elif num_of_larger_than_mine == 0:  #avoid playing card that's largest in a suit
            risk = 99
        else:
            risk = num_of_smaller_than_mine/(3-out_of_suit_player_num) + weight * others_unplayed_num/(3-out_of_suit_player_num)
            #risk = num_of_smaller_than_mine/(3-out_of_suit_player_num)
        return risk       
    
    def calc_risk_for_off_suit(self, card, num_of_mine, num_of_smaller_than_mine , num_of_larger_than_mine, suit_risk):
        if suit_risk == -1: #others are off suit, avoid playing it
            risk = 0
        else:
            card_risk = num_of_smaller_than_mine/(num_of_smaller_than_mine+num_of_larger_than_mine)
            risk = card_risk  + suit_risk * 0.1
            if card.suit == Suit.hearts:
                risk = risk * 1.1
                if num_of_mine > 4:
                    risk = risk * 1.2
        #risk = card.rank.value
        
        #if num_of_larger_than_mine == 0:    #I'm the largest
            #if num_of_smaller_than_mine == 0: #others are off suit
                #risk = 0
            #else:
                #risk += 100
                #if card.suit == Suit.hearts:    #hearts have higher priority
                    #risk += 5                
        #else:           
            #if card.suit == Suit.hearts:
                #risk += 5
                
            ##only 1 card left and there're several cards less than mine        
            #if num_of_mine  == 1:
                #if num_of_smaller_than_mine >= 2:
                    #risk += 20
                #elif num_of_smaller_than_mine > 0:
                    #risk += 10                 
        return risk
        
        
    def calc_suit_risk(self, my_cards, others_unplayed_cards_of_suit):
        if not my_cards or not others_unplayed_cards_of_suit:
            return -1
        
        total_smaller = 0
        total_larger = 0
        for card in my_cards:
            num_of_smaller_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank < card.rank])
            num_of_larger_than_mine = len([ other for other in others_unplayed_cards_of_suit if other.rank > card.rank])
            total_smaller += num_of_smaller_than_mine
            total_larger += num_of_larger_than_mine        
        return total_smaller/(total_smaller+total_larger)


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
        else: #the last one and there's point in the trick  OR  not the last one, play safe card if possbile
            cards_with_suit_in_trick = cards_with_suit(suit, trick)
            max_rank_in_leading_suit = max([card.rank for card in cards_with_suit_in_trick])
            safe_cards = [card for card in cards if card.rank < max_rank_in_leading_suit]
            if safe_cards:
                decision = safe_cards[-1]
            else:
                # 1) last one AND there's point in trick AND no safe card, just play max non-point card
                # 2) not last one AND there's point in trick AND no safe card AND other remaining players are out of suit, play max non-point 
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
        
        
    def get_weakest_card(self, my_hand, cards_played, out_of_suits):
        my_suits = {}
        for card in my_hand:
            if card.suit not in my_suits:
                my_suits[card.suit] = 0
        for suit in my_suits:    
            my_cards = cards_with_suit(suit, my_hand)
            others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(cards_played, my_hand, suit)
            
            my_suits[suit] = self.calc_suit_strength(suit, my_cards, others_unplayed_cards_of_suit, 
                               out_of_suits)
            
        #select weakest
        suit = min(my_suits, key=my_suits.get)
        cards = cards_with_suit(suit, my_hand)
        cards.sort()
        return cards[0]         
    
        
    def get_strongest_card(self, my_hand, cards_played, out_of_suits):
        my_suits = {}
        for card in my_hand:
            if card.suit not in my_suits:
                my_suits[card.suit] = 0
        for suit in my_suits:    
            my_cards = cards_with_suit(suit, my_hand)
            others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(cards_played, my_hand, suit)
            
            my_suits[suit] = self.calc_suit_strength(suit, my_cards, others_unplayed_cards_of_suit, 
                               out_of_suits)
            
        #select strongest
        suit = max(my_suits, key=my_suits.get)
        cards = cards_with_suit(suit, my_hand)
        cards.sort()
        return cards[-1]       
        
    
        
    def check_shoot_the_moon(self, my_hand, cards_played, score_cards, out_of_suits):
        #check if shoot the moon is broken
        if self.try_to_shoot == 2:
            return
        
        if self.try_to_shoot != 2:
            #if any other player has a score card, it's broken
            if (len(score_cards) == 1 and self.name not in score_cards) or len(score_cards) > 1:
                self.try_to_shoot = 2
                self.say("NOTE: Shoot the moon is broken:{}", score_cards)
                return
        
        #calculate suit strength
        self.suit_strength = {}
        my_suits = { card.suit:0 for card in my_hand }
        for suit in my_suits:
            suit_cards = cards_with_suit(suit, my_hand)
            suit_cards.sort()
            others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                cards_played, my_hand, 
                suit)
            suit_strenth = self.calc_suit_strength(suit, suit_cards, 
                                              others_unplayed_cards_of_suit, out_of_suits)
            self.say('suit {}, suit strenth: {}', suit, suit_strenth)                
            self.suit_strength[suit] = suit_strenth            
        
        #check if my cards are strong engough to shoot the moon
        if self.try_to_shoot == 0:
            for suit in my_suits.keys():
                suit_cards = cards_with_suit(suit, my_hand)
                suit_cards.sort()
                others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                    cards_played, my_hand, 
                    suit)
                suit_strenth = self.suit_strength[suit]                 
                
                if not others_unplayed_cards_of_suit:
                    my_suits[suit] = 1
                    self.say('check_shoot: {} is offsuit', suit)                 

                if suit == Suit.hearts:
                    #if all(other.rank < suit_cards[-1].rank for other in others_unplayed_cards_of_suit) and suit_strenth >= 0.5 and len(suit_cards) > 5:
                    if suit_strenth >= 0.5 and len(suit_cards) > 5:
                        my_suits[suit] = 1
                        self.say('check_shoot: {} suit_strength> threshold', suit) 
                    if all(other.rank < suit_cards[-1].rank for other in others_unplayed_cards_of_suit) and suit_strenth > 0.8:
                        my_suits[suit] = 1
                        self.say('check_shoot: {} suit_strength> threshold', suit)                         
                elif suit == Suit.spades:
                    if suit_strenth > 0.7:
                        my_suits[suit] = 1
                        self.say('check_shoot: {} suit_strength> threshold', suit)                           
                else:
                    if all(other.rank < suit_cards[-1].rank for other in others_unplayed_cards_of_suit) and suit_strenth > 0.6:
                        my_suits[suit] = 1
                        self.say('check_shoot: {} suit_strength> threshold', suit)                       
                    
                    #if len(others_unplayed_cards_of_suit) == 1:
                        #my_suits[suit] = 1
                        #self.say('check_shoot: {} has the largest and only one card of others is unplayed', suit)
                    #elif len(suit_cards) > 6:
                        #my_suits[suit] = 1
                        #self.say('check_shoot: {} has the largest and suit_number is {}', suit, len(suit_cards))                    
                    #elif len(suit_cards) < len(others_unplayed_cards_of_suit) and suit_strenth > 0.5:
                        #self.say('check_shoot: {} has the largest and suit_number is {}', suit, len(suit_cards))             
                        #my_suits[suit] = 1
                    #elif len(suit_cards) > len(others_unplayed_cards_of_suit) and suit_strenth > 0.5:
                        #my_suits[suit] = 1
                        #self.say('check_shoot: {} has the largest and suit_number is {}', suit, len(suit_cards))
                    
            #if all suits are strong enough, or only 1 diamond/clubs suit is weak
            weak_suits = [suit for suit in my_suits if my_suits[suit] != 1]
            if not weak_suits or (len(weak_suits)==1 and weak_suits[0] in [Suit.diamonds, Suit.clubs] ):
            #if all( my_suits[suit] == 1 for suit in my_suits) or \               
                self.try_to_shoot = 1
                self.say('NOTE: Switch to shoot the moon. My hand:{}', my_hand)      
                
    def shoot_lead_trick(self, valid_cards, out_of_suits, remaining_players, is_spade_queen_played, my_hand, cards_played):
        '''
        lead the trick while try to shoot the moon
        '''
        self.say('NOTE: shoot - lead the trick')
        #get valid suits first
        valid_suits = {}
        for c in valid_cards:
            if c.suit not in valid_suits:
                valid_suits[c.suit] = True
                
        #if not big enough, start with smaller cards first
        #d = {k:v for k,v in self.suit_strength.items() if k in valid_suits}
        #if d:
            #min_suit = min(d, key=d.get)
            #if self.suit_strength[min_suit]< 0.7:
                #return cards_with_suit(min_suit, valid_cards)[0]

        safe_cards = []
        for card in my_hand:
            if is_others_off_suit(card.suit, out_of_suits, self.name):
                safe_cards.append(card)
            if is_larger_than_others(card, my_hand, cards_played):
                safe_cards.append(card)
                
        if len(my_hand) - len(safe_cards) > 4 : #my hand is not strong enough
            #start from second largest of weak suit
            d = {k:v for k,v in self.suit_strength.items() if k in valid_suits}
            if d:
                min_suit = min(d, key=d.get)
                cards = cards_with_suit(min_suit, valid_cards)
                if len(cards) > 1:
                    decision = cards_with_suit(min_suit, valid_cards)[-2]         
                else:
                    decision = cards_with_suit(min_suit, valid_cards)[-1]
        else:
            # start from lowest rank of safe cards to avoid exposing too early
            if len(safe_cards) > 0:
                if len(safe_cards) > 1 and Card(Suit.spades, Rank.queen) in safe_cards: #avoid exposing QS early
                    safe_cards.remove(Card(Suit.spades, Rank.queen))
                    
                #avoid playing hearts first
                hearts_safe_cards = cards_with_suit(Suit.hearts, safe_cards)
                if hearts_safe_cards and len(hearts_safe_cards) < len(safe_cards):
                    for c in hearts_safe_cards:
                        safe_cards.remove(c)
                decision = get_min_rank_card(safe_cards)
            else:
                risk = -1
                decision = None
                for suit in valid_suits.keys():
                    my_cards_of_suit = cards_with_suit(suit, valid_cards)
                    if not my_cards_of_suit:
                        continue
                    #select max card of the suit and calculate the risk
                    card = my_cards_of_suit[-1] 
                    others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                        cards_played, my_hand, 
                        suit)
                    card_risk = self.calc_risk(suit, card, others_unplayed_cards_of_suit, 
                                              out_of_suits, remaining_players)
                    #select a card with the lowest risk
                    self.say('shoot the moon. card: {}, risk: {}', card, card_risk)
                    if card_risk > risk:
                        risk = card_risk
                        decision = card              

        self.say('played card: {}', decision)
        return decision
    
    def shoot_follow_trick(self, suit, cards, trick, out_of_suits, remaining_players, is_spade_queen_played, my_hand, cards_played):
        '''
        follow the trick while try to shoot the moon
        '''
        cards_with_leading_suit = cards_with_suit(suit, cards)
        if cards_with_leading_suit:
            self.say('NOTE: shoot - play the trick suit')                  
            cards_with_suit_in_trick = cards_with_suit(suit, trick)
            max_rank_in_leading_suit = max([card.rank for card in cards_with_suit_in_trick])
            safe_cards = [card for card in cards if card.rank > max_rank_in_leading_suit]
            safe_cards.sort()
            
            if is_last_turn(trick):
                if contains_score_cards(trick):  #contain score cards, ignore ten of clubs                    
                    if safe_cards:                        
                        decision = safe_cards[0]
                    else:
                        self.say('Shoot the moon is broken')
                        self.try_to_shoot = 2
                        decision = self.best_available(suit, cards, trick, out_of_suits,
                                            remaining_players)
                else:   #no score card, just play my smallest card                    
                    decision = cards[0] if not secondary_choice_needed(cards[0], cards) else cards[1]
             
            else: 
                if safe_cards:  #not the last one, just play the max one or QS
                    if Card(Suit.spades, Rank.queen) in safe_cards:
                        decision = Card(Suit.spades, Rank.queen)
                    else:
                        decision = safe_cards[-1]
                else:  #No safe card
                    if contains_score_cards(trick): #broken, switch to default method
                        self.say('Shoot the moon is broken')
                        self.try_to_shoot = 2
                        decision = self.best_available(suit, cards, trick, out_of_suits,
                                            remaining_players)    
                    else:
                        decision = cards[-1]

        else:  #off suit
            self.say('NOTE: shoot - play off suit')
            if contains_score_cards(trick):
                self.say('Shoot the moon is broken')
                self.try_to_shoot = 2                
                decision = self.play_card_for_offsuit(cards, my_hand, cards_played, is_spade_queen_played, out_of_suits)
            else:                
                valid_suits = {}
                for c in cards:
                    if c.suit not in valid_suits:
                        valid_suits[c.suit] = True
            
                #play the smallest card of the weakest suit.  Avoid playing point card(QS/Heart)
                strength = sys.maxsize
                card = None
                for suit in valid_suits.keys():
                    my_cards_of_suit = cards_with_suit(suit, cards)
                    if not my_cards_of_suit:
                        continue
                    
                    others_unplayed_cards_of_suit = get_unplayed_cards_with_suit(
                                    cards_played, my_hand, 
                                    suit)                   
                    suit_strength = self.calc_suit_strength(suit,my_cards_of_suit, others_unplayed_cards_of_suit, out_of_suits)
                    self.say('suit {}, suit strength: {}', suit, suit_strength)
                    #select a card with the lowest risk                    
                    if suit_strength < strength:
                        strength = suit_strength
                        card = my_cards_of_suit[0]
                
                #avoid QS/hearts
                if card == Card(Suit.spades, Rank.queen) or card.suit == Suit.hearts:
                    self.say('Shoot the moon is broken')
                    self.try_to_shoot = 2                
                    decision = self.play_card_for_offsuit(cards, my_hand, cards_played, is_spade_queen_played, out_of_suits)                    
                else:
                    decision = card            

        return decision            
    
    

    
    
    def calc_suit_strength(self, suit, my_cards, others_unplayed_cards_of_suit, out_of_suits):
        """
        Calculate the strength of my suit by comparing top N cards of mines and other players
        N is average card number of all other players
        """
        if len(my_cards) == 0:
            return 1
        if len(others_unplayed_cards_of_suit) == 0:
            return 1
        
        out_of_suit_player_num = 0
        for player in out_of_suits:
            if player != self.name and out_of_suits[player][suit]:
                out_of_suit_player_num = out_of_suit_player_num + 1
        avg_card_num = math.ceil(len(others_unplayed_cards_of_suit)/(3-out_of_suit_player_num))
        others_unplayed_cards_of_suit.sort()
        start_index = 0
        if len(others_unplayed_cards_of_suit) > avg_card_num:
            start_index = len(others_unplayed_cards_of_suit) - avg_card_num
        others_top_n = others_unplayed_cards_of_suit[start_index:]
        
        my_cards.sort()
        start_index = 0
        if len(my_cards) > avg_card_num:
            start_index = len(my_cards) -avg_card_num
        my_top_n = my_cards[start_index:]
        self.say("my top N:{}, others top N:{}", my_top_n, others_top_n)
        
        total_smaller = 0
        total_larger = 0
        for card in my_top_n:
            num_of_smaller_than_mine = len([ other for other in others_top_n if other.rank < card.rank])
            num_of_larger_than_mine = len([ other for other in others_top_n if other.rank > card.rank])
            total_smaller += num_of_smaller_than_mine
            total_larger += num_of_larger_than_mine        
        return total_smaller/(total_smaller+total_larger)    
    
    
if __name__ == "__main__":
    player = AdvancedPlayer()
    my_hand = [str_to_card('2D'), str_to_card('AD'),
               str_to_card('5H'), str_to_card('4H'), str_to_card('AH'),
               str_to_card('5S'), str_to_card('KS'),
               str_to_card('3C'), str_to_card('AC'),
               ]
    cards_played = []
    out_of_suits = {}
    print(player.get_strongest_card(my_hand, cards_played, out_of_suits))
    
    print(min(my_hand))
    