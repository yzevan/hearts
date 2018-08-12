import utils
import logging

def takeAction(ws, msg, player_name):
    event_name = msg["eventName"]
    data = msg["data"]
    logging.debug("--- {0} ---".format(event_name))
    logging.debug(data)