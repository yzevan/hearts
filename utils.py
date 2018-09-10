import logging
import os
import sys
import variables

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
    if not os.path.exists(variables.log_folder):
        os.mkdir(variables.log_folder)
    log_filename = os.path.join(variables.log_folder, "debug.log")
    handler = logging.FileHandler(log_filename)
    handler.setFormatter(formatter)
    
    log_filename_info = os.path.join(variables.log_folder, "info.log")
    handler_info = logging.FileHandler(log_filename_info)
    handler_info.setFormatter(formatter)
    handler_info.setLevel(debug_maping["info"])

    for item in logger.handlers:
        item.close()
        logger.removeHandler(item)
    logger.addHandler(handler)
    logger.addHandler(handler_info)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(debug_maping.get("debug"))
    logger.addHandler(ch)

def set_data(server, client, fields):
    for field in fields:
        client[field] = server[field]