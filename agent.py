import json
from utils import set_data, str_to_card
import logging
from copy import deepcopy
import variables
from players.advanced_player import AdvancedPlayer
from players.montecarlo_player import MonteCarloPlayer


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
    "candidateCards": []
}

GAME_STATUS = {
    "dealNumber": 0,
    "roundNumber": 0,
    "gameNumber": 0,
    "players": {},
    "receiver": ""
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
    elif event_name == "pass_cards_end":
        set_cards_after_passing(data)
    elif event_name == "expose_cards":
        do_expose_cards(ws, data)
    elif event_name == "expose_cards_end":
        set_cards_after_exposing(data)
    logging.debug(GAME_STATUS)

def set_new_game(data):
    GAME_STATUS["gameNumber"] = data["gameNumber"]
    for player in data["players"]:
        playerName = player["playerName"]
        GAME_STATUS["players"][playerName] = deepcopy(PLAYER_STATUS)

def set_new_deal(data):
    GAME_STATUS["dealNumber"] = data["dealNumber"]
    fields_all = ["playerNumber", "playerName", "gameScore", "dealScore", "cardsCount", "receivedFrom", "exposedCards", "shootingTheMoon", "roundCard"]
    fields_self = ["scoreCards", "cards", "pickedCards", "receivedCards", "candidateCards"]
    set_data_for_players(data, fields_all, fields_self)

def do_pass_cards(ws, data):
    GAME_STATUS["receiver"] = data["receiver"]
    event_name = "pass_my_cards"
    logging.debug("--- {0} ---".format(event_name))
    cards = GAME_STATUS["players"][MY_NAME]["cards"]
    hand = [str_to_card(card) for card in cards]
    cards_to_pass = PLAYER.pass_cards(hand)
    result = [str(card) for card in cards_to_pass]
    ws.send(json.dumps({
        "eventName": event_name,
        "data": {
            "cards": result
        }
    }))
    logging.debug(result)
    
def set_cards_after_passing(data):
    fields_all = ["receivedFrom"]
    fields_self = ["cards", "pickedCards", "receivedCards"]
    set_data_for_players(data, fields_all, fields_self)

def do_expose_cards(ws, data):
    event_name = "expose_my_cards"
    logging.debug("--- {0} ---".format(event_name))
    exposed = PLAYER.expose()
    result = ["AH"] if exposed else []
    ws.send(json.dumps({
        "eventName": event_name,
        "data": {
            "cards": result
        }
    }))
    logging.debug(result)

def set_cards_after_exposing(data):
    fields_all = ["exposedCards"]
    set_data_for_players(data, fields_all = fields_all)

def set_data_for_players(data, fields_all = [], fields_self = []):
    if fields_all:
        for player in data["players"]:
            playerName = player["playerName"]
            player_local = GAME_STATUS["players"][playerName]
            set_data(player, player_local, fields_all)
    if fields_self:
        player_self = data["self"]
        player_self_local = GAME_STATUS["players"][MY_NAME]
        set_data(player_self, player_self_local, fields_self)