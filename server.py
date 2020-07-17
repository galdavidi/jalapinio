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
import logger

COMMANDS = fileReader.reader()
HOST = 'localhost'
PORT = 1803
BUFFER = 1024
END_MSG = b'exit'
CODING = "utf-8"
MAX_CLIENTS_NUM = 5
NUM_OF_THREADS = 2
JOB_NUM = [1, 2]
CONN_TEST = b''
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
        logger.logger_build(f"{err}", 'error')
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
            server_socket.setblocking(TRUE)
            all_connections.append(connection)
            all_address.append(address)
            client_name = get_client_username(connection)
            all_clients.append(client_name)
            logger.logger_build(f"new connection from {client_name}", 'info', client_name)
            print('{} has connected using this address: {} \n'.format(all_clients[-1:], address), end='')
        except ConnectionError as err:
            logger.logger_build(f"{err}", 'error')
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
            connection, client_name = get_client(server_cmd)
            if connection is not None:
                shell_commands.command_sender(connection, client_name)
        elif server_cmd == END_MSG.decode(CODING):
            for connection in all_connections:
                connection.close()
                server_socket.close()
                logger.logger_build(f"exit", 'info')
                sys.exit()
        elif 'get' in server_cmd:
            connection, client_name = get_client(server_cmd)
            if connection is not None:
                remote_path, local_path = path_exector(server_cmd)
                shell_commands.get_file(local_path, remote_path, connection)
        elif 'put' in server_cmd:
            connection, client_name = get_client(server_cmd)
            if connection is not None:
                remote_path, local_path = path_exector(server_cmd)
                shell_commands.put_file(remote_path, local_path, connection)
        else:
            print("Command does not exist")


def path_exector(command):
    '''get the pathes from the put and get command'''
    command = command.split()
    if len(command) == 4:
        return command[2], command[3]


def list_connections():
    '''return a list of all active connection'''
    results = ''

    connection: object
    for connection_index, connection in enumerate(all_connections):
        try:
            connection.send(CONN_TEST)
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
        target = select_command.split()
        target = int(target[1])
        connection = all_connections[target]
        print(f'you are connected to {all_clients[target]}')
        return connection, all_clients[target]
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


def main():
    create_workers()
    create_jobs()


if __name__ == '__main__':
    main()
