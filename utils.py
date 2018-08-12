import logging
import os
import sys
from card import Suit, Rank, Card

debug_maping = {
    'error':logging.ERROR,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'debug':logging.DEBUG,
}

def init_logger():
    logger = logging.getLogger()
    formatter_str = '%(asctime)s [%(process)d:%(threadName)s] %(levelname)-8s[%(filename)s:%(lineno)d] %(message)s'
    formatter = logging.Formatter(formatter_str, '%Y-%m-%d %H:%M:%S')
    
    logger.setLevel(debug_maping.get("debug"))
    handler = logging.FileHandler(os.path.join(sys.path[0],'debug.log'))
    handler.setFormatter(formatter)

    for item in logger.handlers:
        item.close()
        logger.removeHandler(item)
    logger.addHandler(handler)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(debug_maping.get("debug"))
    logger.addHandler(ch)

def set_data(server, client, fields):
    for field in fields:
        client[field] = server[field]

def str_to_card(s):
    str_to_suit = {
        "C": Suit.clubs,
        "D": Suit.diamonds,
        "S": Suit.spades,
        "H": Suit.hearts
    }
    str_to_rank = {
        "2": Rank.two,
        "3": Rank.three,
        "4": Rank.four,
        "5": Rank.five,
        "6": Rank.six,
        "7": Rank.seven,
        "8": Rank.eight,
        "9": Rank.nine,
        "T": Rank.ten,
        "J": Rank.jack,
        "Q": Rank.queen,
        "K": Rank.king,
        "A": Rank.ace
    }
    return Card(str_to_suit[s[1]], str_to_rank[s[0]])