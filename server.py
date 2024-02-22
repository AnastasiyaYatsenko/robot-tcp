import select
import socket
from struct import unpack, pack
from typing import NamedTuple

from arm_geometry_test import *

SERVER_ADDRESS = ('192.168.0.91', 8686)

MAX_CONNECTIONS = 10  # 20

# Звідки й куди записувати інформацію
INPUTS = list()
OUTPUTS = list()


class Params(NamedTuple):
    lin: float
    ang: float
    hold: int


class Robot:
    hand1 = Params(0, 0, 0)
    hand2 = Params(1, 1, 1)
    hand3 = Params(2, 2, 2)

    # num = 0

    def set_robot_params_hands(self, hand1, hand2, hand3):
        self.hand1 = Params(hand1.lin, hand1.ang, hand1.hold)
        self.hand2 = Params(hand2.lin, hand2.ang, hand2.hold)
        self.hand3 = Params(hand3.lin, hand3.ang, hand3.hold)

    def set_robot_params(self, lin1, ang1, hold1, lin2, ang2, hold2, lin3, ang3, hold3):
        self.hand1 = Params(lin1, ang1, hold1)
        self.hand2 = Params(lin2, ang2, hold2)
        self.hand3 = Params(lin3, ang3, hold3)

    def print(self):
        print("Hand 1: " + str(self.hand1))
        print("Hand 2: " + str(self.hand2))
        print("Hand 3: " + str(self.hand3))


# robots_num = 2
robots = [Robot()]  # for i in range(robots_num)]


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
                                               LS[7], LS[8], LS[9],)
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
