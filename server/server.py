# CR: Are you handling exceptions correctly?
# CR: Add documention to functions
# !/bin/python3
'''
Author: Gal Davidi
'''

import os
import logging
import logging.config
import socket
import sys
import fileReader
import signal
import threading
from _thread import *
import hashlib
import time
from queue import Queue
import shell_commands



COMMANDS = fileReader.reader()
HOST = 'localhost'
PORT = 1803
BUFFER = 1024
END_MSG = b'exit'
CODING = "utf-8"
MAX_CLIENTS_NUM = 5
NUM_OF_THREADS = 2
JOB_NUM = [1, 2]
CONN_TEST = b' '
BIG_BUFFER = 65536
TRUE = 1
FALSE = 0
BACK_TO_STRESS = 'back'
USERNAME_CMD = b'whoami'
LOGGER_CONF_PATH = "../conf/logger.conf"

queue = Queue()
all_connections = []
all_address = []
all_clients = []

logging.config.fileConfig(LOGGER_CONF_PATH)
logger = logging.getLogger("server_logger")

def socket_setup():
    '''set up a listening socket'''
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (HOST, PORT)
    print('starting up on {} port {} \n'.format(*server_address))
    try:
        server_socket.bind(server_address)
        server_socket.listen(MAX_CLIENTS_NUM)
    except OSError as err:
        server_socket.close()
        print("got OSError: {}".format(err))
        sys.exit(1)


def connection_listner():
    '''
    listen for connaction and put each connaction in list
    :param sock:
    :return:
    '''
    for connection in all_connections:
        connection.close()

    del all_connections[:]
    del all_address[:]
    del all_clients[:]

    while True:
        try:
            connection, address = server_socket.accept()
            server_socket.setblocking(True)
            all_connections.append(connection)
            all_address.append(address)
            all_clients.append(get_client_username(connection))

            print('{} has connected using this address: {} \n'.format(all_clients[-1:], address), end='')
        except ConnectionError as err:
            print(err)
            server_socket.close()
            sys.exit(1)


def start_shell():
    '''
    a custom shell for all of the commands
    '''
    while True:
        server_cmd = input("stres$ ")
        if server_cmd == 'list':
            list_connections()
        elif 'select' in server_cmd:
            connection = get_client(server_cmd)
            if connection is not None:
                command_sender(connection)
        elif server_cmd == END_MSG.decode(CODING):
            for connection in all_connections:
                connection.close()
                server_socket.close()
                print("exiting")
                exit_thread()
                sys.exit(0)
        elif 'get' in server_cmd:
            connection = get_client(server_cmd)
            if connection is not None:
                shellCMD.(connection)

        else:
            print("Command does not exist")


def list_connections():
    '''return a list of all active connection'''
    results = ''

    for connection_index, connection in enumerate(all_connections):
        try:
            connection.send(CONN_TEST)
            connection.recv(BIG_BUFFER)
        except:
            del all_connections[connection_index]
            del all_address[connection_index]
            del all_clients[connection_index]
            continue
        results = f"{str(connection_index)}  {all_clients[connection_index]}  {str(all_address[connection_index][0])} \n"
    print(f"Clients \n {results}")


def get_client(select_command):
    '''return the connaction'''
    try:
        target = select_command.replace("select ", '')
        target = int(target)
        connection = all_connections[target]
        print(f'you are connected to {all_clients[target]}')
        print(f"{all_clients[target]}$", end="")
        return connection
    except:
        print("Invalid input: select from the list")
        return None


def get_client_username(connection):
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


def command_sender(connection):
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


def create_workers():
    '''create the threads for the program'''
    for _ in range(NUM_OF_THREADS):
        thread = threading.Thread(target=work)
        thread.daemon = True
        thread.start()


def create_jobs():
    for job in JOB_NUM:
        queue.put(job)

    queue.join()


def work():
    '''do the next job in the queue'''
    while True:
        job = queue.get()
        if job == 1:
            socket_setup()
            connection_listner()
        elif job == 2:
            start_shell()

        queue.task_done()


def dir_creator(client_name):
    '''generate dir based on the client name'''
    try:
        os.makedirs(f"./clients/{client_name}")
    except OSError as err:
        print(err)


def main():
    create_workers()
    create_jobs()


if __name__ == '__main__':
    main()
