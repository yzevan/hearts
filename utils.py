import logging
import os
import sys


debug_maping ={
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