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



# def handle(sock, client_ip, client_port):
#     # обробник, що працює у процесі-нащадку
#     logger.info('Start to process request from %s:%d' % (client_ip, client_port))
#
#     robot_num = ceil.match_IPs(client_ip)
#     if robot_num == -1:
#         robot_num = len(ceil.robots)
#         ceil.add_robot(client_ip)
#     ceil.robots[robot_num].set_socket(sock)
#     while True:
#         print("in handle loop")
#         # receiving the data
#         in_buffer = b''
#         try:
#             in_buffer = sock.recv(1024, socket.MSG_DONTWAIT)
#             print("after recv")
#         # Якщо сокет було закрито на іншій стороні
#         except ConnectionResetError:
#             print("ConnectionResetError")
#             break
#         # condition for closing the socket
#         # if the recv() returns 0, it means the client has disconnected
#         if not in_buffer:
#             print("in_buffer empty")
#             break
#         logger.info('In buffer = ' + repr(in_buffer))
#         # process new data
#         try:
#             unpacked_struct = unpack('@ffiffiffi', in_buffer)
#             LS = list(unpacked_struct)
#             ceil.robots[robot_num].set_robot_params(LS[0], LS[1], LS[2],
#                                                     LS[3], LS[4], LS[5],
#                                                     LS[6], LS[7], LS[8])
#             # print(unpacked_struct)
#             # print(robot_ip)
#             ceil.robots[robot_num].print()
#             # move_robot_simu(robot_num)
#             print("---")
#             ceil.robots[robot_num].isMoving = False
#
#         except Exception as e:
#             result = repr(e)
#
#         # for testing
#         # p = pack('@ffiffiffi',
#         #          0.0, 0.0, 0,
#         #          1.0, 1.0, 1,
#         #          2.0, 2.0, 2,)
#         # ceil.robots[robot_num].out_buffer = p
#         logger.info('Out buffer = ' + repr(ceil.robots[robot_num].out_buffer))
#
#         # if we have parameters to send in buffer, send
#         if ceil.robots[robot_num].out_buffer:
#             # out_buffer = result
#             logger.info('Out buffer = ' + repr(ceil.robots[robot_num].out_buffer))
#             # sending
#             sock.sendall(ceil.robots[robot_num].out_buffer)
#             time.sleep(1)
#     sock.close()
#     logger.info('Done.')


def handle_read(sock, client_ip, client_port):
    # обробник, що працює у процесі-нащадку
    logger.info('Start to process request from %s:%d' % (client_ip, client_port))

    robot_num = ceil.match_IPs(client_ip)
    if robot_num == -1:
        robot_num = len(ceil.robots)
        ceil.add_robot(client_ip)
    ceil.robots[robot_num].set_socket(sock)
    thread_tx = threading.Thread(
        target=handle_write,
        args=(sock, client_ip, client_port)
    )
    thread_tx.daemon = True
    thread_tx.start()
    while True:
        # print("in handle read loop")
        # receiving the data
        in_buffer = b''
        try:
            in_buffer = sock.recv(1024)
            # print("after recv")
        # Якщо сокет було закрито на іншій стороні
        except ConnectionResetError:
            print("ConnectionResetError")
            break
        # condition for closing the socket
        # if the recv() returns 0, it means the client has disconnected
        if not in_buffer:
            print("in_buffer empty")
            break
        # logger.info('In buffer = ' + repr(in_buffer))
        # process new data
        try:
            unpacked_struct = unpack('@ffiffiffi', in_buffer)
            LS = list(unpacked_struct)
            ceil.robots[robot_num].set_robot_params(LS[0], LS[1], LS[2],
                                                    LS[3], LS[4], LS[5],
                                                    LS[6], LS[7], LS[8])
            # print(unpacked_struct)
            # print(robot_ip)
            # ceil.robots[robot_num].print()
            # move_robot_simu(robot_num)
            # print("---")
            ceil.robots[robot_num].isMoving = False

        except Exception as e:
            result = repr(e)

    sock.close()
    logger.info('Done.')


def handle_write(sock, client_ip, client_port):
    # обробник, що працює у процесі-нащадку
    logger.info('Start to process request from %s:%d' % (client_ip, client_port))

    robot_num = ceil.match_IPs(client_ip)
    while True:
        # for testing
        # p = pack('@ffiffiffi',
        #          0.0, 0.0, 0,
        #          1.0, 1.0, 1,
        #          2.0, 2.0, 2)
        # ceil.robots[robot_num].out_buffer = p
        # logger.info('in out buffer handle')

        # if we have parameters to send in buffer, send
        if ceil.robots[robot_num].out_buffer:
            # logger.info('Out buffer = ' + repr(ceil.robots[robot_num].out_buffer))
            # sending
            # print(robot_num)
            to_send = ceil.robots[robot_num].out_buffer
            ceil.robots[robot_num].out_buffer = b''
            sock.sendall(to_send)
            # print(f"We've send all bytes")


def imitate_command():
    while len(ceil.robots) == 0:
        time.sleep(0.1)
    time.sleep(1)
    print("in imitate")
    ceil.move_robot(0, 1700.0, 0)
    ceil.move_robot(0, 300.0, 0)
    ceil.turn_robot(0)
    # ceil.robots[0].print()


def serve_forever():
    # створюємо сокет для прослуховування
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # re-use port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(BIND_ADDRESS)
    sock.listen(BACKLOG)
    # слухаємо і при отриманні нового вхідного з'єднання,
    # створюємо тред, який буде його обробляти
    logger.info('Listning no %s:%d...' % BIND_ADDRESS)

    # pg.init()
    # command_panel()

    t1 = threading.Thread(target=imitate_command)
    t1.start()

    # cp = ControlPanel()
    t_cp = threading.Thread(target=command_panel)
    t_cp.start()

    while True:
        # print("in serve forever loop")
        try:
            connection, (client_ip, client_port) = sock.accept()
        except IOError as e:
            if e.errno == errno.EINTR:
                continue
            raise
        # запускаємо тред
        thread_rx = threading.Thread(
            target=handle_read,
            args=(connection, client_ip, client_port)
        )
        thread_rx.daemon = True
        thread_rx.start()

        # thread_tx = threading.Thread(
        #     target=handle_write,
        #     args=(connection, client_ip, clinet_port)
        # )
        # thread_tx.daemon = True
        # thread_tx.start()
        # time.sleep(5)
        # ceil.move_robot(0,0,0)


def draw_ceil(screen):
    rect_side = 590
    # rect_side = 1000
    outer_border = 60  # 20 + 60
    outer_border_add = 20 + outer_border
    side = 2 * size["netBorder"] + (ceil.max_x - 1) * size["netStep"]
    rect_border = int(size["netBorder"]*rect_side / side)
    rect_step = int(size["netStep"] * rect_side / side)

    # side_x = 2*size["netBorder"]+(self.max_x-1)*size["netStep"]
    # side_y = 2 * size["netBorder"] + (self.max_y - 1) * size["netStep"]
    pg.draw.rect(screen, (255, 255, 255), (20, 20, rect_side+2*outer_border, rect_side+2*outer_border))
    pg.draw.rect(screen, (0, 0, 0), (outer_border_add, outer_border_add, rect_side, rect_side), 1)

    for y in range(ceil.max_y):
        for x in range(ceil.max_x):
            pg.draw.circle(screen, (0, 0, 0), (rect_border+x*rect_step+outer_border_add,
                                               rect_border+y*rect_step+outer_border_add), 5, 1)

        for i in range(len(ceil.robots)):
            # print("in r loop")
            points = ceil.robots[i].get_real_coordinates()
            hand_points = ceil.robots[i].get_real_coordinates_hand()
            # print(points)
            # self.rect_border + x * self.rect_step + 30
            hand_red_x, hand_red_y = (rect_border + hand_points[0][0] * rect_side / side + 40,
                                      rect_border + hand_points[0][1] * rect_side / side + 40)
            hand_green_x, hand_green_y = (rect_border + hand_points[1][0] * rect_side / side + 40,
                                          rect_border + hand_points[1][1] * rect_side / side + 40)
            hand_blue_x, hand_blue_y = (rect_border + hand_points[2][0] * rect_side / side + 40,
                                        rect_border + hand_points[2][1] * rect_side / side + 40)

            red_x, red_y = (points[0][0] * rect_side / side + outer_border_add,
                            points[0][1] * rect_side / side + outer_border_add)
            green_x, green_y = (points[1][0] * rect_side / side + outer_border_add,
                                points[1][1] * rect_side / side + outer_border_add)
            blue_x, blue_y = (points[2][0] * rect_side / side + outer_border_add,
                              points[2][1] * rect_side / side + outer_border_add)
            center_x, center_y = (points[3][0] * rect_side / side + outer_border_add,
                                  points[3][1] * rect_side / side + outer_border_add)

            # print(f"{red_x} {red_y}")
            # print(f"{green_x} {green_y}")
            # print(f"{blue_x} {blue_y}")
            # print(f"{center_x} {center_y}")
            # print("-----")

            pg.draw.line(screen, (255, 0, 0), (hand_red_x, hand_red_y), (center_x, center_y), 3)
            pg.draw.line(screen, (0, 255, 0), (hand_green_x, hand_green_y), (center_x, center_y), 3)
            pg.draw.line(screen, (0, 0, 255), (hand_blue_x, hand_blue_y), (center_x, center_y), 3)

            pg.draw.circle(screen, (255, 0, 0), (red_x, red_y), 10, 1)
            pg.draw.circle(screen, (0, 255, 0), (green_x, green_y), 10, 1)
            pg.draw.circle(screen, (0, 0, 255), (blue_x, blue_y), 10, 1)
            pg.draw.circle(screen, (255, 255, 255), (center_x, center_y), 5, 1)


def command_panel():
    # print('gogo')

    # screen = pg.display.set_mode([1200, 700])
    pg.init()
    screen = pg.display.set_mode([1200, 750])
    robot_input = pygame_textinput.TextInputVisualizer()
    x_input = pygame_textinput.TextInputVisualizer()
    y_input = pygame_textinput.TextInputVisualizer()
    screen.fill((48, 48, 48))

    # pg.draw.rect(self.screen, (255, 255, 255), (20, 20, 620, 620))

    running = True
        # while self.get_working():
        #     for event in pg.event.get():
        #         if event.type == pg.QUIT:
        #             pass
    while True:  # main game loop
        # print("in run")
        events = pg.event.get()
        draw_ceil(screen)
        # time.sleep(0.1)
            # Feed it with events every frame
            # robot_input.update(events)
            # x_input.update(events)
            # y_input.update(events)
            # Blit its surface onto the screen
            # self.screen.blit(robot_input.surface, (10, 10))
            # self.screen.blit(x_input.surface, (100, 10))
            # self.screen.blit(y_input.surface, (200, 10))

        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        pg.display.update()
