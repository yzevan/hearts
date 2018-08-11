import time
import json
from websocket import create_connection
import variables
import utils
import logging

ws = ""
player_name = variables.player_name

def takeAction(action, player_name, data):
    pass

def doListen():
    try:
        global ws
        ws = create_connection(variables.url)
        ws.send(json.dumps({
            "eventName": "join",
            "data": {
                "playerName": player_name
            }
        }))
        while True:
            result = ws.recv()
            msg = json.loads(result)
            event_name = msg["eventName"]
            data = msg["data"]
            takeAction(event_name, player_name, data)
    except Exception:
        doListen()


if __name__ == '__main__':
    utils.init_logger()
    try:
        doListen()
    except KeyboardInterrupt:
        logging.error("Program exit by key board")