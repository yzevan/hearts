import time
import json
from websocket import create_connection
import variables
from utils import init_logger
import logging
from agent import takeAction

ws = ""
player_name = variables.player_name

def doListen(player_name, player_number, token, connect_url):
    try:
        global ws
        ws = create_connection(connect_url)
        ws.send(json.dumps({
            "eventName": "join",
            "data": {
                "playerNumber":player_number,
                "playerName": player_name,
                "token": token                
                
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
    argv_count=len(sys.argv)
    if argv_count==5:
        player_name = sys.argv[1]
        player_number = sys.argv[2]
        token= sys.argv[3]
        connect_url = sys.argv[4]
    else:
        player_name = variables.player_name
        player_number = variables.player_number
        token = variables.token
        connect_url = variables.url
        
    init_logger()
    try:
        doListen(player_name, player_number, token, connect_url)
    except KeyboardInterrupt:
        logging.error("Exit by keyboard")