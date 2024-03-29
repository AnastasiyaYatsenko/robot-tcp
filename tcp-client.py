#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from time import sleep
from typing import NamedTuple
from struct import *


class Params(NamedTuple):
    lin: float
    ang: float
    hold: int


class Robot:
    def __init__(self):
        self.hands = [Params(3, 3, 3), Params(4, 4, 4), Params(5, 5, 5)]
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
for i in range(10):
    p = pack('@ffiffiffi',
             robot.hands[0].lin, robot.hands[0].ang, robot.hands[0].hold,
             robot.hands[1].lin, robot.hands[1].ang, robot.hands[1].hold,
             robot.hands[2].lin, robot.hands[2].ang, robot.hands[2].hold)
    client.send(p)
    sleep(1)

# отримуємо від сервера інфу
data = client.recv(36)
unp = unpack('@ffiffiffi', data)
LS = list(unp)
print(LS)
print("---")
