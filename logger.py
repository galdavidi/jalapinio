# !/bin/python3
'''
Author: Gal Davidi
'''

FORMAT = "%(asctime)s - %(message)s"
DATE_FMT = "%d/%m/%Y %I:%M:%S"
LOG_LEVEL = 'INFO'
import logging
import os


def logger_build(msg, l_level, client_name='server'):
    dir_creator(client_name)
    if client_name != 'server':
        logging.basicConfig(filename=f"./clients/{client_name}/log", format=FORMAT, datefmt=DATE_FMT, level=LOG_LEVEL)
    else:
        logging.basicConfig(filename=f"./app_log/{client_name}/log", format=FORMAT, datefmt=DATE_FMT, level=LOG_LEVEL)
    if l_level == 'info':
        logging.info(msg)
    elif l_level == 'error':
        logging.error(msg)


def dir_creator(client_name):
    '''generate dir based on the client name'''
    try:
        if client_name != "server":
            os.makedirs(f"./clients/{client_name}")
    except OSError as err:
        if err == FileExistsError:
            print(err)
