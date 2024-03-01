import select
import socket
from struct import unpack, pack
from time import sleep
from typing import NamedTuple

from arm_geometry_test import *

SERVER_ADDRESS = ('192.168.0.91', 8686)

MAX_CONNECTIONS = 10  # 20

# Звідки й куди записувати інформацію
INPUTS = list()
OUTPUTS = list()

ceil_step = 200.0
max_x = 10
max_y = 10
ceil_arr = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


class Params(NamedTuple):
    lin: float
    ang: float
    hold: int

    x: int
    y: int


class Robot:
    def __init__(self):
        self.hands = [Params(0, 0, 0, 0, 0), Params(1, 1, 1, 0, 0), Params(2, 2, 2, 0, 0)]
    # hand1 = Params(0, 0, 0, 0, 0)
    # hand2 = Params(1, 1, 1, 0, 0)
    # hand3 = Params(2, 2, 2, 0, 0)

    # num = 0

    def set_robot_params_hands(self, hand1, hand2, hand3):
        self.hands[0] = Params(hand1.lin, hand1.ang, hand1.hold, hand1.x, hand1.y)
        self.hands[1] = Params(hand2.lin, hand2.ang, hand2.hold, hand1.x, hand1.y)
        self.hands[2] = Params(hand3.lin, hand3.ang, hand3.hold, hand1.x, hand1.y)

    def set_robot_params(self, lin1, ang1, hold1, lin2, ang2, hold2, lin3, ang3, hold3):
        self.hands[0] = Params(lin1, ang1, hold1, self.hands[0].x, self.hands[0].y)
        self.hands[1] = Params(lin2, ang2, hold2, self.hands[1].x, self.hands[1].y)
        self.hands[2] = Params(lin3, ang3, hold3, self.hands[2].x, self.hands[2].y)

    def set_coordinates(self, x1, y1, x2, y2, x3, y3):
        self.hands[0] = Params(self.hands[0].lin, self.hands[0].ang, self.hands[0].hold, x1, y1)
        self.hands[1] = Params(self.hands[1].lin, self.hands[1].ang, self.hands[1].hold, x2, y2)
        self.hands[2] = Params(self.hands[2].lin, self.hands[2].ang, self.hands[2].hold, x3, y3)
        self.place_ceil_coordinates()

    def set_hand_x(self, i, x):
        self.hands[i] = Params(self.hands[i].lin, self.hands[i].ang, self.hands[i].hold, x, self.hands[i].y)

    def set_hand_y(self, i, y):
        self.hands[i] = Params(self.hands[i].lin, self.hands[i].ang, self.hands[i].hold, self.hands[i].x, y)

    def place_ceil_coordinates(self):
        self.move_hand(0, self.hands[0].x, self.hands[0].y)
        self.move_hand(1, self.hands[1].x, self.hands[1].y)
        self.move_hand(2, self.hands[2].x, self.hands[2].y)

    def move_hand(self, hand_num, x, y):
        if ceil_arr[y][x] == 0:
            self.hand_unhold_point(hand_num)
            self.hand_hold_point(hand_num, x, y)

    def hand_unhold_point(self, hand_num):
        old_x = self.hands[hand_num].x
        old_y = self.hands[hand_num].y
        ceil_arr[old_y][old_x] = 0

    def hand_hold_point(self, hand_num, x, y):
        if ceil_arr[y][x] == 0:
            ceil_arr[y][x] = 1
            self.set_hand_x(hand_num, x)
            self.set_hand_y(hand_num, y)
        else:
            print("Point occupied!")

    def get_occupied_area(self):
        center_x, center_y = calculate_center(self.hands[0].x, self.hands[0].y,
                                              self.hands[1].x, self.hands[1].y,
                                              self.hands[2].x, self.hands[2].y,
                                              self.hands[0].lin, self.hands[1].lin, self.hands[2].lin)
        return [self.hands[0].x, self.hands[0].y,
                self.hands[1].x, self.hands[1].y,
                self.hands[2].x, self.hands[2].y,
                center_x, center_y]

    def print(self):
        print("Hand 1: " + str(self.hands[0]))
        print("Hand 2: " + str(self.hands[1]))
        print("Hand 3: " + str(self.hands[2]))


robots_num = 2
robots = [Robot() for i in range(robots_num)]


# def robot_move_hand(rob_num, hand_num, x, y):
#     if ceil_arr[y][x] == 0:
#         robot_hand_unhold_point(rob_num, hand_num)
#         robot_hand_hold_point(rob_num, hand_num, x, y)
#
#
# def robot_hand_unhold_point(rob_num, hand_num):
#     old_x = robots[rob_num].hands[hand_num].x
#     old_y = robots[rob_num].hands[hand_num].y
#     ceil_arr[old_y][old_x] = 0
#
#
# def robot_hand_hold_point(rob_num, hand_num, x, y):
#     if ceil_arr[y][x] == 0:
#         ceil_arr[y][x] = 1
#         robots[rob_num].set_hand_x(hand_num, x)
#         robots[rob_num].set_hand_y(hand_num, y)
#     else:
#         print("Point occupied!")


def show_ceil():
    print("- - - - - - - - - -")
    for i in range(max_y):
        for j in range(max_x):
            print(ceil_arr[i][j], end=' ')
        print()
    print("- - - - - - - - - -")



def robot_simulation():
    robots[0].set_coordinates(0, 0, 1, 0, 2, 0)
    robots[1].set_coordinates(9, 9, 8, 9, 7, 9)
    # robots[0].move_hand(0, robots[0].hands[0].x, robots[0].hands[0].y)
    # robots[0].move_hand(1, robots[0].hands[1].x, robots[0].hands[1].y)
    # robots[0].move_hand(2, robots[0].hands[2].x, robots[0].hands[2].y)
    move_dir = 0  # (0,0) to (10,0), top
             # 1    (10,0) to (10,10), right
             # 2    (10,10) to (0,10), bottom
             # 3    (0,10) to (0,0), left

    while True:
        for i in range(3):
            show_ceil()
            sleep(0.5)
            if move_dir == 0:
                if robots[0].hands[i].x + 3 < 10:
                    robots[0].move_hand(i, robots[0].hands[i].x + 3, robots[0].hands[i].y)
                else:
                    if robots[0].hands[i].x + 3 == 10:
                        robots[0].move_hand(i, 9, robots[0].hands[i].y + 1)
                    elif robots[0].hands[i].x + 3 == 11:
                        robots[0].move_hand(i, 9, robots[0].hands[i].y + 2)
                        move_dir = 1

                if robots[1].hands[i].x - 3 >= 0:
                    robots[1].move_hand(i, robots[1].hands[i].x - 3, robots[1].hands[i].y)
                else:
                    if robots[1].hands[i].x - 3 == -1:
                        robots[1].move_hand(i, 0, robots[1].hands[i].y - 1)
                    elif robots[1].hands[i].x - 3 == -2:
                        robots[1].move_hand(i, 0, robots[1].hands[i].y - 2)
            elif move_dir == 1:
                if robots[0].hands[i].y + 3 < 10:
                    robots[0].move_hand(i, robots[0].hands[i].x, robots[0].hands[i].y + 3)
                else:
                    if robots[0].hands[i].y + 3 == 10:
                        robots[0].move_hand(i, robots[0].hands[i].x - 1, 9)
                    elif robots[0].hands[i].y + 3 == 11:
                        robots[0].move_hand(i, robots[0].hands[i].x - 2, 9)
                        move_dir = 2

                if robots[1].hands[i].y - 3 >= 0:
                    robots[1].move_hand(i, robots[1].hands[i].x, robots[1].hands[i].y - 3)
                else:
                    if robots[1].hands[i].y - 3 == -1:
                        robots[1].move_hand(i, robots[1].hands[i].x + 1, 0)
                    elif robots[1].hands[i].y - 3 == -2:
                        robots[1].move_hand(i, robots[1].hands[i].x + 2, 0)
                        # move_dir = 0
            elif move_dir == 2:
                if robots[0].hands[i].x - 3 >= 0:
                    robots[0].move_hand(i, robots[0].hands[i].x - 3, robots[0].hands[i].y)
                else:
                    if robots[0].hands[i].x - 3 == -1:
                        robots[0].move_hand(i, 0, robots[0].hands[i].y - 1)
                    elif robots[0].hands[i].x - 3 == -2:
                        robots[0].move_hand(i, 0, robots[0].hands[i].y - 2)
                        move_dir = 3

                if robots[1].hands[i].x + 3 < 10:
                    robots[1].move_hand(i, robots[1].hands[i].x + 3, robots[1].hands[i].y)
                else:
                    if robots[1].hands[i].x + 3 == 10:
                        robots[1].move_hand(i, 9, robots[1].hands[i].y + 1)
                    elif robots[1].hands[i].x + 3 == 11:
                        robots[1].move_hand(i, 9, robots[1].hands[i].y + 2)
                        # move_dir = 1
            elif move_dir == 3:
                if robots[0].hands[i].y - 3 >= 0:
                    robots[0].move_hand(i, robots[0].hands[i].x, robots[0].hands[i].y - 3)
                else:
                    if robots[0].hands[i].y - 3 == -1:
                        robots[0].move_hand(i, robots[0].hands[i].x + 1, 0)
                    elif robots[0].hands[i].y - 3 == -2:
                        robots[0].move_hand(i, robots[0].hands[i].x + 2, 0)
                        move_dir = 0

                if robots[1].hands[i].y + 3 < 10:
                    robots[1].move_hand(i, robots[1].hands[i].x, robots[1].hands[i].y + 3)
                else:
                    if robots[1].hands[i].y + 3 == 10:
                        robots[1].move_hand(i, robots[1].hands[i].x - 1, 9)
                    elif robots[1].hands[i].y + 3 == 11:
                        robots[1].move_hand(i, robots[1].hands[i].x - 2, 9)
                        # move_dir = 2
        # show_ceil()
        # sleep(2)


def get_non_blocking_server_socket():

    # Створюємо сокет, що працює без блокування основного потоку
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)

    server.bind(SERVER_ADDRESS)

    # Встановлення максимальної кількості підключень
    server.listen(MAX_CONNECTIONS)

    return server


def handle_readables(readables, server):
    """
    Обробка появи подій на входах
    """
    for resource in readables:

        # Якщо подія від серверного сокету, то ми отримуємо нове підключення
        if resource is server:
            connection, client_address = resource.accept()
            connection.setblocking(0)
            INPUTS.append(connection)
            print("new connection from {address}".format(address=client_address))

        # Якщо подія не від серверного сокету, але спрацювало переривання на наповнення вхідного буферу
        else:
            data = []
            try:
                data = resource.recv(1024)

            # Якщо сокет було закрито на іншій стороні
            except ConnectionResetError:
                pass

            if data:

                # Отримання даних
                unpacked_struct = unpack('@iffiffiffi', data)
                LS = list(unpacked_struct)
                robots[LS[0]].set_robot_params(LS[1], LS[2], LS[3],
                                               LS[4], LS[5], LS[6],
                                               LS[7], LS[8], LS[9])
                # print(unpacked_struct)
                robots[LS[0]].print()
                print("---")
                # print("getting data: {data}".format(data=str(data)))

                # Говоримо про те, що ми будемо ще й писати у даний сокет
                if resource not in OUTPUTS:
                    OUTPUTS.append(resource)

            # Якщо даних нема, але подія спрацювала, то ОС нам відправляє прапорець про повне прочитання ресурсу та його закритті
            else:

                # Очищуємо дані про ресурс і закриваємо дескриптор
                clear_resource(resource)


def clear_resource(resource):
    """
    Метод очищення ресурсів використання сокету
    """
    if resource in OUTPUTS:
        OUTPUTS.remove(resource)
    if resource in INPUTS:
        INPUTS.remove(resource)
    resource.close()

    print('closing connection ' + str(resource))


def handle_writables(writables):

    # Дана подія виникає, коли в буфері на запис звільнюється місце
    for resource in writables:
        try:
            arm_state = get_arm_state_by_pos(7, size, 'b')
            # print(arm_state)
            p = pack('@ffi', arm_state['s'], arm_state['a'], arm_state['h'])
            resource.send(p)
            # resource.send(bytes('Hello from server!', encoding='UTF-8'))
        except OSError:
            clear_resource(resource)


def send_point():
    try:
        p = pack('@ff', 1.5, 3.2)
        OUTPUTS[0].send(p)
    except OSError:
        clear_resource(OUTPUTS[0])
