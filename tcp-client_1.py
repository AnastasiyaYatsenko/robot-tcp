#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from time import sleep
from typing import NamedTuple
from struct import *
import threading
import sys


class Params(NamedTuple):
    lin: float
    ang: float
    hold: int


class Robot:
    def __init__(self):
        # self.hands = [Params(3, 3, 3), Params(4, 4, 4), Params(5, 5, 5)]
        self.hands = [Params(205.67936211491906, 287.49573328079583, 0),
                      Params(48.0, 4.0, 1),
                      Params(205.67936211491906, 80.50426671920418, 1)]
        self.isMoving = False

    def set_robot_params_hands(self, hand1, hand2, hand3):
        self.hands[0] = Params(hand1.lin, hand1.ang, hand1.hold)
        self.hands[1] = Params(hand2.lin, hand2.ang, hand2.hold)
        self.hands[2] = Params(hand3.lin, hand3.ang, hand3.hold)

    def set_robot_params(self, lin1, ang1, hold1, lin2, ang2, hold2, lin3, ang3, hold3):
        self.hands[0] = Params(lin1, ang1, hold1)
        self.hands[1] = Params(lin2, ang2, hold2)
        self.hands[2] = Params(lin3, ang3, hold3)


robot = Robot()

MAX_CONNECTIONS = 10
address_to_server = ('192.168.0.91', 8686)

# конектимось до сервера
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(address_to_server)


# надсилаємо на сервер інфу
# for i in range(10):
#     p = pack('@ffiffiffi',
#              robot.hands[0].lin, robot.hands[0].ang, robot.hands[0].hold,
#              robot.hands[1].lin, robot.hands[1].ang, robot.hands[1].hold,
#              robot.hands[2].lin, robot.hands[2].ang, robot.hands[2].hold)
#     client.sendall(p)
#     sleep(1)
#
# # отримуємо від сервера інфу
# data = client.recv(36)
# unp = unpack('@ffiffiffi', data)
# LS = list(unp)
# print(LS)
# print("---")


def send_params():
    p = pack('@ffiffiffi',
             robot.hands[0].lin, robot.hands[0].ang, robot.hands[0].hold,
             robot.hands[1].lin, robot.hands[1].ang, robot.hands[1].hold,
             robot.hands[2].lin, robot.hands[2].ang, robot.hands[2].hold)
    client.send(p)


def imitate_movement():
    sleep(1)
    send_params()


# Wait for incoming data from server
# .decode is used to turn the message in bytes to a string
def receive_data():
    while True:
        try:
            print("receive")
            data = client.recv(36)
            print("done")
            unp = unpack('@ffiffiffi', data)
            LS = list(unp)
            print(LS)
            robot.set_robot_params(LS[0], LS[1], LS[2],
                                   LS[3], LS[4], LS[5],
                                   LS[6], LS[7], LS[8])
            imitate_movement()
        except ConnectionResetError:
            print("Robot has been disconnected from the server")
            break


# Create new thread to wait for data
receiveThread = threading.Thread(target=receive_data)
receiveThread.start()

send_params()

# Send data to server
# str.encode is used to turn the string message into bytes so it can be sent across the network
# while True:
#     send_params()
#     sleep(1)
