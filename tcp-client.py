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
    hand1 = Params(0, 0, 0)
    hand2 = Params(1, 1, 1)
    hand3 = Params(2, 2, 2)

    num = 0

    def set_robot_params(self, hand1, hand2, hand3):
        self.hand1 = Params(hand1.lin, hand1.ang, hand1.hold)
        self.hand2 = Params(hand2.lin, hand2.ang, hand2.hold)
        self.hand3 = Params(hand3.lin, hand3.ang, hand3.hold)


robot = Robot()

MAX_CONNECTIONS = 10
address_to_server = ('192.168.0.91', 8686)

# clients = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for i in range(MAX_CONNECTIONS)]
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(address_to_server)

for i in range(MAX_CONNECTIONS):
    p = pack('@iffiffiffi', robot.num,
             robot.hand1.lin, robot.hand1.ang, robot.hand1.hold,
             robot.hand2.lin, robot.hand2.ang, robot.hand2.hold,
             robot.hand3.lin, robot.hand3.ang, robot.hand3.hold)
    client.send(p)
    sleep(0.1)

data = client.recv(1024)
print(str(data))
