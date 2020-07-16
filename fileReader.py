#!/bin/python3
'''
Author: Gal Davidi
'''

import sys
import os

FILE_PATH = 'commands'


def reader(path=FILE_PATH):
    commands = []
    with open(FILE_PATH) as file:
        line = file.readline()
        while line:
            line = file.readline()
            commands.append(line)

        return commands


if __name__ == '__main__':
    reader()
