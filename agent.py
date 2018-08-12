import json
from utils import set_data, str_to_card
import logging
from copy import deepcopy
import variables
from players.advanced_player import AdvancedPlayer
from players.montecarlo_player import MonteCarloPlayer
from rules import are_hearts_broken, is_spade_queen_played

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
    "cards_played": (),
    "are_hearts_broken": False,
    "is_spade_queen_played": False,
    "trick": [],
    "roundPlayer": ""
}

MY_NAME = variables.player_name
PLAYER = AdvancedPlayer()

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
    fields_game = ["dealNumber"]
    fields_all = ["playerNumber", "playerName", "gameScore", "dealScore", "cardsCount", "receivedFrom", "exposedCards", "shootingTheMoon", "roundCard"]
    fields_self = ["scoreCards", "cards", "pickedCards", "receivedCards", "candidateCards"]
    set_data_for_game(data, fields_game = fields_game, fields_all = fields_all, fields_self = fields_self)

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
    GAME_STATUS["are_hearts_broken"] = GAME_STATUS["are_hearts_broken"] or are_hearts_broken(GAME_STATUS["cards_played"])
    GAME_STATUS["is_spade_queen_played"] = GAME_STATUS["is_spade_queen_played"] or is_spade_queen_played(GAME_STATUS["cards_played"])

def do_play_card(ws, data):
    fields_self = ["cards", "candidateCards"]
    set_data_for_game(data, fields_self = fields_self)
    candidateCards = [str_to_card(card) for card in data["self"]["candidateCards"]]
    candidateCards.sort()
    event_name = "pick_card"
    logging.debug("--- {0} ---".format(event_name))
    logging.debug("Candidate cards: {0}".format(candidateCards))
    logging.debug("Trick: {0}".format(GAME_STATUS["trick"]))
    decision = PLAYER.play_card(candidateCards, GAME_STATUS["trick"], GAME_STATUS["are_hearts_broken"], GAME_STATUS["is_spade_queen_played"])
    result = str(decision)
    ws.send(json.dumps({
        "eventName": event_name,
        "data": {
            "dealNumber": GAME_STATUS["dealNumber"],
            "roundNumber": GAME_STATUS["roundNumber"],
            "turnCard": result
        }
    }))
    logging.debug("Pick: {0}".format(result))

def set_round_end(data):
    fields_game = ["roundPlayer"]
    fields_all = ["dealScore"]
    set_data_for_game(data, fields_game = fields_game, fields_all = fields_all)

def set_deal_end(data):
    fields_all = ["gameScore", "scoreCards", "cards", "shootingTheMoon"]
    set_data_for_game(data, fields_all = fields_all)

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