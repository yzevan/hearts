import json
from utils import set_data
import logging
from copy import deepcopy
import variables
from players.advanced_player import AdvancedPlayer
from players.montecarlo_player import MonteCarloPlayer
from rules import str_to_card
from card import Suit, Rank, Card
from game import Game
import datetime

PLAYER_STATUS = {
    "playerNumber": 0,
    "playerName": "",
    "gameScore": 0,
    "dealScore": 0,
    "scoreCards": [],
    "cards": [],
    "cardsCount": 13,
    "pickedCards": [],
    "receivedCards": [],
    "receivedFrom": "",
    "exposedCards": [],
    "shootingTheMoon": False,
    "roundCard": "",
    "candidateCards": [],
    "rank": 0,
    "deals": []
}

GAME_STATUS = {
    "dealNumber": 0,
    "roundNumber": 0,
    "gameNumber": 0,
    "players": {},
    "receiver": "",
    "roundPlayers": [],
    "turnPlayer": "",
    "turnCard": "",
    "roundPlayer": "",
    "cards_played": (),
    "are_hearts_broken": False,
    "is_spade_queen_played": False,
    "trick": [],
    "out_of_suits": {},
    "cards_taken": ([], [], [], []),
    "score_cards": {}
}

MY_NAME = ''
PLAYER = None
NAME_TO_NUMBER = {}

    
def takeAction(ws, msg): 
    event_name = msg["eventName"]
    data = msg["data"]
    logging.debug("--- {0} ---".format(event_name))
    logging.debug(data)
    if event_name == "new_game":
        set_new_game(data)
    elif event_name == "new_deal":
        set_new_deal(data)
    elif event_name == "pass_cards":
        do_pass_cards(ws, data)
    elif event_name == "receive_opponent_cards":
        set_received_opponent_cards(data)
    elif event_name == "pass_cards_end":
        set_cards_after_passing(data)
    elif event_name == "expose_cards":
        do_expose_card(ws, data)
    elif event_name == "expose_cards_end":
        set_cards_after_exposing(data)
    elif event_name == "new_round":
        set_new_round(data)
    elif event_name == "turn_end":
        set_turn_end(data)
    elif event_name == "your_turn":
        do_play_card(ws, data)
    elif event_name == "round_end":
        set_round_end(data)
    elif event_name == "deal_end":
        set_deal_end(data)
    elif event_name == "game_end":
        set_game_end(data)
    logging.debug(GAME_STATUS)

def set_new_game(data):
    fields_game = ["gameNumber"]
    set_data_for_game(data, fields_game = fields_game)
    for player in data["players"]:
        playerName = player["playerName"]
        GAME_STATUS["players"][playerName] = deepcopy(PLAYER_STATUS)

def set_new_deal(data):
    global PLAYER    
    PLAYER = AdvancedPlayer(MY_NAME)
        
    fields_game = ["dealNumber"]
    fields_all = ["playerNumber", "playerName", "gameScore", "dealScore", "cardsCount", "receivedFrom", "exposedCards", "shootingTheMoon", "roundCard"]
    fields_self = ["scoreCards", "cards", "pickedCards", "receivedCards", "candidateCards"]
    i = 0
    for player in data["players"]:
        playerName = player["playerName"]
        GAME_STATUS["out_of_suits"][playerName] = {Suit.clubs: False, Suit.diamonds: False, Suit.spades: False, Suit.hearts: False}
        NAME_TO_NUMBER[playerName] = i
        i += 1
    set_data_for_game(data, fields_game = fields_game, fields_all = fields_all, fields_self = fields_self)
    GAME_STATUS["cards_played"] = ()
    GAME_STATUS["are_hearts_broken"] = False
    GAME_STATUS["is_spade_queen_played"] = False
    GAME_STATUS["cards_taken"] = ([], [], [], [])
    GAME_STATUS["score_cards"] = {}

def do_pass_cards(ws, data):
    fields_game = ["receiver"]
    set_data_for_game(data, fields_game = fields_game)
    event_name = "pass_my_cards"
    logging.debug("--- {0} ---".format(event_name))
    cards = GAME_STATUS["players"][MY_NAME]["cards"]
    hand = [str_to_card(card) for card in cards]
    cards_to_pass = PLAYER.pass_cards(hand)
    result = [str(card) for card in cards_to_pass]
    ws.send(json.dumps({
        "eventName": event_name,
        "data": {
            "dealNumber": GAME_STATUS["dealNumber"],
            "cards": result
        }
    }))
    logging.debug(result)

def set_received_opponent_cards(data):
    fields_self = ["cards", "pickedCards", "receivedCards"]
    set_data_for_game(data, fields_self = fields_self)
    
def set_cards_after_passing(data):
    fields_all = ["receivedFrom"]
    set_data_for_game(data, fields_all = fields_all)

def do_expose_card(ws, data):
    event_name = "expose_my_cards"
    logging.debug("--- {0} ---".format(event_name))
    exposed = PLAYER.expose()
    result = ["AH"] if exposed else []
    ws.send(json.dumps({
        "eventName": event_name,
        "data": {
            "dealNumber": GAME_STATUS["dealNumber"],
            "cards": result
        }
    }))
    logging.debug(result)

def set_cards_after_exposing(data):
    fields_all = ["exposedCards"]
    set_data_for_game(data, fields_all = fields_all)

def set_new_round(data):
    fields_game = ["roundNumber", "roundPlayers"]
    fields_all = ["cardsCount", "roundCard"]
    fields_self = ["scoreCards", "cards", "candidateCards"]
    set_data_for_game(data, fields_game = fields_game, fields_all = fields_all, fields_self = fields_self)
    GAME_STATUS["trick"] = []

def set_turn_end(data):
    fields_game = ["turnPlayer", "turnCard"]
    fields_all = ["cardsCount", "roundCard"]
    set_data_for_game(data, fields_game = fields_game, fields_all = fields_all)
    turnCard = str_to_card(data["turnCard"])
    logging.debug("Turn card: {0}".format(data["turnCard"]))
    GAME_STATUS["cards_played"] += (turnCard, )
    GAME_STATUS["trick"].append(turnCard)
    if not GAME_STATUS["are_hearts_broken"] and turnCard.suit == Suit.hearts:
        GAME_STATUS["are_hearts_broken"] = True
    if not GAME_STATUS["is_spade_queen_played"] and turnCard == Card(Suit.spades, Rank.queen):
        GAME_STATUS["is_spade_queen_played"] = True
    leading_suit = GAME_STATUS["trick"][0].suit
    #If the player didn't play the leading suit, set out_of_suits to True for this player
    if not GAME_STATUS["out_of_suits"][GAME_STATUS["turnPlayer"]][leading_suit] and str_to_card(GAME_STATUS["turnCard"]).suit != leading_suit:
        GAME_STATUS["out_of_suits"][GAME_STATUS["turnPlayer"]][leading_suit] = True
        
    #check if palyers are out of suit after the turn card is palyed
    found = False    
    my_hand = [str_to_card(card) for card in GAME_STATUS["players"][MY_NAME]["cards"]]
    for rank in Rank:
        card = Card(turnCard.suit, rank)
        if card not in GAME_STATUS["cards_played"] and card not in my_hand:
            found = True
            break
    if not found:  #if there's no card which is played or in my hand, that means all other players are out of the suit
        logging.debug("NOTE: All players are out of the suit. Turn Card:{0}".format(turnCard))
        for player_name in GAME_STATUS["out_of_suits"].keys():
            if player_name != MY_NAME:
                GAME_STATUS["out_of_suits"][player_name][turnCard.suit] = True


def do_play_card(ws, data):
    global PLAYER
    begin = datetime.datetime.utcnow()
    fields_self = ["cards", "candidateCards"]
    set_data_for_game(data, fields_self = fields_self)
    candidateCards = [str_to_card(card) for card in data["self"]["candidateCards"]]
    candidateCards.sort()
    event_name = "pick_card"
    logging.info("--- {0} ---".format(event_name))
    logging.info("Candidate cards: {0}".format(candidateCards))
    logging.info("Trick: {0}".format(GAME_STATUS["trick"]))
    logging.info("Cards played: {0}".format(sorted(GAME_STATUS["cards_played"])))
    logging.info("Score cards: {0}".format(GAME_STATUS["score_cards"]))
    remaining_players = GAME_STATUS["roundPlayers"][((GAME_STATUS["roundPlayers"].index(MY_NAME) + 1) % 4):]
    if variables.montecarlo:
        game = Game()
        player_hands = [[], [], [], []]
        current_player_index = NAME_TO_NUMBER[MY_NAME]
        my_hand = [str_to_card(card) for card in GAME_STATUS["players"][MY_NAME]["cards"]]
        player_hands[current_player_index] = my_hand
        round_players = [NAME_TO_NUMBER[player] for player in GAME_STATUS["roundPlayers"]]
        game.set_attributes(GAME_STATUS["trick"], player_hands, GAME_STATUS["cards_played"], GAME_STATUS["are_hearts_broken"], GAME_STATUS["is_spade_queen_played"], current_player_index, NAME_TO_NUMBER[GAME_STATUS["roundPlayers"][0]], GAME_STATUS["cards_taken"], round_players, GAME_STATUS["roundNumber"] - 1)
        cards_count = {}
        for key, value in GAME_STATUS["players"].items():
            if key != MY_NAME:
                cards_count[NAME_TO_NUMBER[key]] = value["cardsCount"]
        PLAYER = MonteCarloPlayer()
        PLAYER.setAttributes(game, cards_count, my_hand)
    else:
        #PLAYER = AdvancedPlayer(MY_NAME)
        my_hand = [str_to_card(card) for card in GAME_STATUS["players"][MY_NAME]["cards"]]
        cards_played = GAME_STATUS["cards_played"]
        #PLAYER.setAttributes(my_hand, cards_played)        
    decision = PLAYER.play_card(candidateCards, GAME_STATUS["trick"], GAME_STATUS["out_of_suits"], remaining_players, GAME_STATUS["are_hearts_broken"], GAME_STATUS["is_spade_queen_played"], my_hand, cards_played, GAME_STATUS["score_cards"])
    result = str(decision)
    ws.send(json.dumps({
        "eventName": event_name,
        "data": {
            "dealNumber": GAME_STATUS["dealNumber"],
            "roundNumber": GAME_STATUS["roundNumber"],
            "turnCard": result
        }
    }))
    logging.info("Pick: {0}".format(result))
    logging.info('Decision Time: {0}'.format(datetime.datetime.utcnow() - begin))

def set_round_end(data):
    fields_game = ["roundPlayer"]
    fields_all = ["dealScore"]
    set_data_for_game(data, fields_game = fields_game, fields_all = fields_all)
    GAME_STATUS["cards_taken"][NAME_TO_NUMBER[GAME_STATUS["roundPlayer"]]].extend(GAME_STATUS["trick"])
    logging.info('Trick:{0}'.format(GAME_STATUS["trick"]))
    #update score_cards table
    trick_score_cards = [ card for card in GAME_STATUS["trick"] if card == Card(Suit.spades, Rank.queen) or card.suit == Suit.hearts]
    if trick_score_cards:
        if GAME_STATUS["roundPlayer"] not in GAME_STATUS["score_cards"]:
            GAME_STATUS["score_cards"][GAME_STATUS["roundPlayer"]] = trick_score_cards
        else:
            GAME_STATUS["score_cards"][GAME_STATUS["roundPlayer"]].extend(trick_score_cards)
        if GAME_STATUS["roundPlayer"] == MY_NAME:
            logging.info('I take the trick. Score cards:{}'.format(trick_score_cards))
    
            
def set_deal_end(data):
    fields_all = ["gameScore", "scoreCards", "cards", "shootingTheMoon"]
    set_data_for_game(data, fields_all = fields_all)
    logging.info('--- deal end ---')

def set_game_end(data):
    fields_all = ["rank", "deals"]
    set_data_for_game(data, fields_all = fields_all)

def set_data_for_game(data, fields_game = [], fields_all = [], fields_self = []):
    if fields_game:
        set_data(data, GAME_STATUS, fields_game)
    if fields_all:
        for player in data["players"]:
            playerName = player["playerName"]
            player_local = GAME_STATUS["players"][playerName]
            set_data(player, player_local, fields_all)
    if fields_self:
        player_self = data["self"]
        player_self_local = GAME_STATUS["players"][MY_NAME]
        set_data(player_self, player_self_local, fields_self)