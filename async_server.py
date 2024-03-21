#!/usr/bin/python3


import errno
import threading
import socket
import logging
import time
from struct import unpack

from arm_geometry_test import *
from robot import *
from ceil import *

logger = logging.getLogger('main')


BIND_ADDRESS = ('192.168.0.91', 8686)
BACKLOG = 5

ceil = Ceil()


def handle(sock, client_ip, client_port):
    # обработчик, работающий в процессе-потомке
    logger.info('Start to process request from %s:%d' % (client_ip, client_port))
    robot_num = ceil.match_IPs(client_ip)
    if robot_num == -1:
        robot_num = len(ceil.robots)
        ceil.add_robot(client_ip)
    ceil.robots[robot_num].set_socket(sock)
    while True:
        # receiving the data
        in_buffer = b''
        try:
            in_buffer = sock.recv(1024)
        # Якщо сокет було закрито на іншій стороні
        except ConnectionResetError:
            break
        # condition for closing the socket
        # if the recv() returns 0, it means the client has disconnected
        if not in_buffer:
            break
        logger.info('In buffer = ' + repr(in_buffer))
        # process new data
        try:
            unpacked_struct = unpack('@ffiffiffi', in_buffer)
            LS = list(unpacked_struct)
            ceil.robots[robot_num].set_robot_params(LS[0], LS[1], LS[2],
                                                    LS[3], LS[4], LS[5],
                                                    LS[6], LS[7], LS[8])
            # print(unpacked_struct)
            # print(robot_ip)
            ceil.robots[robot_num].print()
            # move_robot_simu(robot_num)
            print("---")

        except Exception as e:
            result = repr(e)

        p = pack('@ffiffiffi',
                 0.0, 0.0, 0,
                 1.0, 1.0, 1,
                 2.0, 2.0, 2,)
        ceil.robots[robot_num].out_buffer = p

        if ceil.robots[robot_num].out_buffer:
            # out_buffer = result
            logger.info('Out buffer = ' + repr(ceil.robots[robot_num].out_buffer))
            # отправляем
            sock.sendall(ceil.robots[robot_num].out_buffer)
            time.sleep(1)
    sock.close()
    logger.info('Done.')


def serve_forever():
    # создаём слушающий сокет
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # re-use port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(BIND_ADDRESS)
    sock.listen(BACKLOG)
    # слушаем и при получении нового входящего соединения,
    # порождаем нить, которая будет его обрабатывать
    logger.info('Listning no %s:%d...' % BIND_ADDRESS)
    while True:
        try:
            connection, (client_ip, clinet_port) = sock.accept()
        except IOError as e:
            if e.errno == errno.EINTR:
                continue
            raise
        # запускаем нить
        thread = threading.Thread(
            target=handle,
            args=(connection, client_ip, clinet_port)
        )
        thread.daemon = True
        thread.start()


# def main():
#     # настраиваем логгинг
#     logger.setLevel(logging.DEBUG)
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.DEBUG)
#     formatter = logging.Formatter(
#         '%(asctime)s [%(levelname)s] [%(thread)s] %(message)s',
#         '%H:%M:%S'
#     )
#     ch.setFormatter(formatter)
#     logger.addHandler(ch)
#     logger.info('Run')
#     # запускаем сервер
#     serve_forever()
#
#
# main()