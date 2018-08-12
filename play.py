import time
import json
from websocket import create_connection
import variables
import utils
import logging
import agent

ws = ""
player_name = variables.player_name

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
            agent.takeAction(ws, msg, player_name)
    except Exception:
        doListen()


if __name__ == '__main__':
    utils.init_logger()
    try:
        doListen()
    except KeyboardInterrupt:
        logging.error("Exit by keyboard")