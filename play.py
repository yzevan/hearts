import time
import json
from websocket import create_connection
import variables
from utils import init_logger
import logging
from agent import takeAction

ws = ""
player_name = variables.player_name

def doListen():
    try:
        global ws
        ws = create_connection(variables.url)
        ws.send(json.dumps({
            "eventName": "join",
            "data": {
                "playerNumber":11,
                "playerName": player_name,
                "token":"1234567"                
                
            }
        }))
        while True:
            result = ws.recv()
            msg = json.loads(result)
            takeAction(ws, msg)
    except Exception as e:
        logging.error(e)
        doListen()


if __name__ == '__main__':
    init_logger()
    try:
        doListen()
    except KeyboardInterrupt:
        logging.error("Exit by keyboard")