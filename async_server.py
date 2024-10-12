#!/usr/bin/python3


import errno
import random
import threading
# import socket
import logging
# import time
from struct import unpack

import pygame as pg
import sys
# from pygame import font

# from arm_geometry_test import *
from pygame_elements import InputBox, RadioButton
# from robot import *
from ceil import *

logger = logging.getLogger('main')


# BIND_ADDRESS = ('192.168.0.91', 8686)
BIND_ADDRESS = ('localhost', 8686)
BACKLOG = 5

ceil = Ceil()
ceil_type = 0 # 0 - hex, 1 - square
# path = []
counter = 0
ot = [-1, -1]
running = True

def handle_read(sock, client_ip, client_port):
    # обробник, що працює у процесі-нащадку
    logger.info('Start to process request from %s:%d' % (client_ip, client_port))

    robot_num = ceil.match_IPs(client_ip)
    if robot_num == -1:
        robot_num = len(ceil.robots)
        ceil.add_robot(client_ip)
    ceil.robots[robot_num].set_socket(sock)
    ceil.robots[robot_num].isAlive = True
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
            # if ceil.robots[robot_num].params_updated == False and ceil.robots[robot_num].isMoving == True:
            ceil.robots[robot_num].params_updated = True
            # elif ceil.robots[robot_num].params_updated == True and ceil.robots[robot_num].isMoving == True:
            #     ceil.robots[robot_num].isMoving = False
            ceil.robots[robot_num].set_robot_params(LS[0], LS[1], LS[2],
                                                    LS[3], LS[4], LS[5],
                                                    LS[6], LS[7], LS[8])
            print(f"obtained: {unpacked_struct}")
            # print("---")
            # print(f"Robot no. {robot_num}")
            # ceil.robots[robot_num].print()
            # move_robot_simu(robot_num)
            # print("---")
            ceil.robots[robot_num].isMoving = False
            # print(f"isMoving: {ceil.robots[robot_num].isMoving}")

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
            logger.info('Out buffer = ' + repr(ceil.robots[robot_num].out_buffer))
            unp = unpack('ffiffiffi', ceil.robots[robot_num].out_buffer)
            # sending
            print(unp)
            to_send = ceil.robots[robot_num].out_buffer
            ceil.robots[robot_num].out_buffer = b''
            ceil.robots[robot_num].socket.sendall(to_send)
            # print(f"We've send all bytes")


# def imitate_command():
#     while len(ceil.robots) == 0:
#         time.sleep(0.1)
#     time.sleep(1)
#     print("in imitate")
#     ceil.start_move(0, 500.0, 700.0)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def serve_forever():
    # створюємо сокет для прослуховування
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # re-use port
    global sock
    global BIND_ADDRESS

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    current_ip = s.getsockname()[0]
    s.close()
    # print(f"Hostname: {hostname}")
    print(f"Current machine IP Address: {current_ip}")

    inp = input('0 - Leave localhost IP\n1 - Set current machine IP as server IP\n2 - Enter IP manually\nOption: ')
    try:
        inp = int(inp)
    except:
        inp = 0

    print(f"Option {inp} is chosen")
    if inp == 0:
        print("local")
    elif inp == 1:
        print("current")
        BIND_ADDRESS = (current_ip, 8686)
    elif inp == 2:
        manual_ip = input('IP address: ')
        # print(manual_ip)
        if validate_ip(manual_ip):
            BIND_ADDRESS = (manual_ip, 8686)
        else:
            print("IP address is not valid, the default will be chosen")
            # print("not ok :(")
            # print("default local")
    else:
        print("default local")

    # BIND_ADDRESS = (ip_address, 8686)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(BIND_ADDRESS)
    sock.listen(BACKLOG)
    # слухаємо і при отриманні нового вхідного з'єднання,
    # створюємо тред, який буде його обробляти
    logger.info('Listning no %s:%d...' % BIND_ADDRESS)

    # pg.init()
    # command_panel()

    # t1 = threading.Thread(target=imitate_command)
    # t1.start()

    # cp = ControlPanel()
    t_cp = threading.Thread(target=command_panel)
    t_cp.daemon = True
    t_cp.start()


    global running
    while running:
        try:
            connection, (client_ip, client_port) = sock.accept()
        except IOError as e:
            if e.errno == errno.EINTR:
                continue
            elif e.errno == errno.EINVAL:
                sys.exit(1)
            raise
        # запускаємо тред
        thread_rx = threading.Thread(
            target=handle_read,
            args=(connection, client_ip, client_port)
        )
        thread_rx.daemon = True
        thread_rx.start()

def draw_ceil(screen):
    global ceil_type
    rect_side = 590
    # rect_side = 1000
    outer_border = 60  # 20 + 60
    outer_border_add = 20 + outer_border
    if ceil_type == 0:
        side = (ceil.max_x - 1) * size["d2"] / 2 + 2 * size["netBorder"]
    elif ceil_type == 1:
        side = 2 * size["netBorder"] + (ceil.max_x - 1) * size["netStep"]
    # side = (ceil.max_x - 1)*size["d2"] / 2 + 2*size["netBorder"]
    rect_border = int(size["netBorder"]*rect_side / side)
    # rect_step = int(rect_side / ceil.max_x)
    rect_step = int(size["d2"]/2 * rect_side / side)

    # D1 = (size["d2"] / 3) * 2
    # side = size["d2"] / 2 + size["netBorder"]
    # ceil_y = D1 + (1 - (x % 2)) * (size["D2"] / 4) + size["netBorder"]

    # side_x = 2*size["netBorder"]+(self.max_x-1)*size["netStep"]
    # side_y = 2 * size["netBorder"] + (self.max_y - 1) * size["netStep"]
    pg.draw.rect(screen, (255, 255, 255), (20, 20, rect_side+2*outer_border, rect_side+2*outer_border))
    pg.draw.rect(screen, (0, 0, 0), (outer_border_add, outer_border_add, rect_side, rect_side), 1)

    # Create a font object
    font = pg.font.Font(None, 30)
    top_text = font.render("top", True, (0, 0, 0))
    top_text_rect = top_text.get_rect(center=(20 + (rect_side+2*outer_border) / 2, 10 + outer_border_add / 2))
    bottom_text = font.render("bottom", True, (0, 0, 0))
    bottom_text_rect = bottom_text.get_rect(center=(20 + (rect_side + 2 * outer_border) / 2,
                                                    rect_side + 1.5 * outer_border_add - 10))

    left_text = font.render("left", True, (0, 0, 0))
    left_r_text = pg.transform.rotate(left_text, 90)
    left_text_rect = left_text.get_rect(center=(10 + outer_border_add / 2, 20 + (rect_side + 2 * outer_border) / 2))
    right_text = font.render("right", True, (0, 0, 0))
    right_r_text = pg.transform.rotate(right_text, -90)
    right_text_rect = right_text.get_rect(center=(rect_side + 1.5 * outer_border_add - 10,
                                                  20 + (rect_side + 2 * outer_border) / 2))

    screen.blit(top_text, top_text_rect)
    screen.blit(bottom_text, bottom_text_rect)
    screen.blit(left_r_text, left_text_rect)
    screen.blit(right_r_text, right_text_rect)

    for y in range(ceil.max_y):
        for x in range(ceil.max_x):
            fin_x, fin_y = -1, -1
            r = to_range(size["holeRad"], 0, size["ceilLenX"], 0, rect_side)
            if ceil_type == 0:
                fin_x, fin_y = get_ceil_coords_hex(x, y, rect_side, outer_border, outer_border_add)
            elif ceil_type == 1:
                fin_x, fin_y = get_ceil_coords_square(x, y, rect_side, outer_border, outer_border_add)

            pg.draw.circle(screen, (0, 0, 0), (fin_x, fin_y), r, 1)
        # print("\n")

        for i in range(len(ceil.robots)):
            if not ceil.robots[i].isAlive:
                print("Robot is inactive")
                continue
            # print("in r loop")
            if ceil.robots[i].ot[0] != -1:
                # x = ceil.robots[i].ot[0] * rect_side / side + outer_border_add + rect_border
                # y = ceil.robots[i].ot[1] * rect_side / side + outer_border_add + rect_border


                x, y = get_visual_coords(ceil.robots[i].ot[0],
                                         ceil.robots[i].ot[1],
                                         rect_side, outer_border, outer_border_add)

                # xs = ceil.robots[i].os[0] * rect_side / side + outer_border_add
                # ys = ceil.robots[i].os[1] * rect_side / side + outer_border_add

                # pg.draw.line(screen, (255, 0, 0), (xs, ys), (x, y), 3)
                pg.draw.circle(screen, (255, 0, 0), (x, y), 5, 0)
                # pg.draw.circle(screen, (255, 0, 0), (xs, ys), 5, 0)

            if len(ceil.robots[i].opt_points) != 0:
                # print(f"trying to print opt points: {ceil.robots[i].opt_points}")
                for j in range(len(ceil.robots[i].opt_points)):
                    # hand_0_x, hand_0_y = get_ceil_coords(ceil.robots[i].opt_points[j][0],
                    #                                      ceil.robots[i].opt_points[j][1],
                    #                                      rect_side, outer_border)
                    hand_0_x, hand_0_y = get_visual_coords(ceil.robots[i].opt_points[j][0],
                                                           ceil.robots[i].opt_points[j][1],
                                                           rect_side, outer_border, outer_border_add)
                    # print(f"Opt point: {hand_0_x}, {hand_0_y}")
                    # hand_0_x, hand_0_y = (ceil.robots[i].opt_points[j][0] * rect_side / side + outer_border_add,
                    #                       ceil.robots[i].opt_points[j][1] * rect_side / side + outer_border_add)
                    pg.draw.circle(screen, (0, 255, 0),
                                   (hand_0_x, hand_0_y), 7, 2)

                if not ceil.robots[i].isMovingPath:
                    global counter

                    if len(ceil.robots[i].path) != 0:
                        for j in range(len(ceil.robots[i].path)):
                            for l in range(len(ceil.robots[i].path[j])):
                                # hand_0_x, hand_0_y = (
                                # ceil.robots[i].path[j][l][0] * rect_side / side + outer_border_add,
                                # ceil.robots[i].path[j][l][1] * rect_side / side + outer_border_add)

                                hand_0_x, hand_0_y = get_visual_coords(ceil.robots[i].path[j][l][0],
                                                                       ceil.robots[i].path[j][l][1],
                                                                       rect_side, outer_border, outer_border_add)

                                pg.draw.circle(screen, (255, 0, 0), (hand_0_x, hand_0_y), 10, 2)

                    if len(ceil.robots[i].centers) != 0:
                        for j in range(1, len(ceil.robots[i].centers)):
                            # x_old = ceil.robots[i].centers[j-1][0]  * rect_side / side + outer_border_add + rect_border
                            # y_old = ceil.robots[i].centers[j-1][1]  * rect_side / side + outer_border_add + rect_border
                            x_old, y_old = get_visual_coords(ceil.robots[i].centers[j-1][0],
                                                             ceil.robots[i].centers[j-1][1],
                                                             rect_side, outer_border, outer_border_add)

                            # x_new = ceil.robots[i].centers[j][0]  * rect_side / side + outer_border_add + rect_border
                            # y_new = ceil.robots[i].centers[j][1]  * rect_side / side + outer_border_add + rect_border

                            x_new, y_new = get_visual_coords(ceil.robots[i].centers[j][0],
                                                             ceil.robots[i].centers[j][1],
                                                             rect_side, outer_border, outer_border_add)
                            pg.draw.line(screen, (0, 0, 255), (x_old, y_old), (x_new, y_new), 2)

            points = ceil.robots[i].get_real_coordinates_robot()
            hand_points = ceil.robots[i].get_real_coordinates_hand()

            # hand_red_x, hand_red_y = (hand_points[0][0] * rect_side / side + outer_border_add + rect_border,
            #                           hand_points[0][1] * rect_side / side + outer_border_add + rect_border)
            hand_red_x, hand_red_y = get_visual_coords(hand_points[0][0],
                                                       hand_points[0][1],
                                                       rect_side, outer_border, outer_border_add)
            # hand_red_x, hand_red_y = get_ceil_coords(hand_points[0][0], hand_points[0][1],
            #                                          rect_border, rect_step, outer_border_add)
            # hand_green_x, hand_green_y = (hand_points[1][0] * rect_side / side + outer_border_add + rect_border,
            #                               hand_points[1][1] * rect_side / side + outer_border_add + rect_border)
            hand_green_x, hand_green_y = get_visual_coords(hand_points[1][0],
                                                           hand_points[1][1],
                                                           rect_side, outer_border, outer_border_add)
            # hand_blue_x, hand_blue_y = (hand_points[2][0] * rect_side / side + outer_border_add + rect_border,
            #                             hand_points[2][1] * rect_side / side + outer_border_add + rect_border)
            hand_blue_x, hand_blue_y = get_visual_coords(hand_points[2][0],
                                                         hand_points[2][1],
                                                         rect_side, outer_border, outer_border_add)

            # red_x, red_y = (points[0][0] * rect_side / side + outer_border_add + rect_border,
            #                 points[0][1] * rect_side / side + outer_border_add + rect_border)
            red_x, red_y = get_visual_coords(points[0][0],
                                             points[0][1],
                                             rect_side, outer_border, outer_border_add)
            # green_x, green_y = (points[1][0] * rect_side / side + outer_border_add + rect_border,
            #                     points[1][1] * rect_side / side + outer_border_add + rect_border)
            green_x, green_y = get_visual_coords(points[1][0],
                                                 points[1][1],
                                                 rect_side, outer_border, outer_border_add)
            # blue_x, blue_y = (points[2][0] * rect_side / side + outer_border_add + rect_border,
            #                   points[2][1] * rect_side / side + outer_border_add + rect_border)
            blue_x, blue_y = get_visual_coords(points[2][0],
                                               points[2][1],
                                               rect_side, outer_border, outer_border_add)
            # center_x, center_y = (points[3][0] * rect_side / side + outer_border_add + rect_border,
            #                       points[3][1] * rect_side / side + outer_border_add + rect_border)
            center_x, center_y = get_visual_coords(points[3][0],
                                                   points[3][1],
                                                   rect_side, outer_border, outer_border_add)

            pg.draw.line(screen, (255, 0, 0), (hand_red_x, hand_red_y), (center_x, center_y), 3)
            pg.draw.line(screen, (0, 255, 0), (hand_green_x, hand_green_y), (center_x, center_y), 3)
            pg.draw.line(screen, (0, 0, 255), (hand_blue_x, hand_blue_y), (center_x, center_y), 3)

            if ceil.robots[i].hands[0].hold == 1:
                pg.draw.circle(screen, (255, 0, 0), (red_x, red_y), 5, 0)
            else:
                pg.draw.circle(screen, (255, 0, 0), (red_x, red_y), 10, 1)

            if ceil.robots[i].hands[1].hold == 1:
                pg.draw.circle(screen, (0, 255, 0), (green_x, green_y), 5, 0)
            else:
                pg.draw.circle(screen, (0, 255, 0), (green_x, green_y), 10, 1)

            if ceil.robots[i].hands[2].hold == 1:
                pg.draw.circle(screen, (0, 0, 255), (blue_x, blue_y), 5, 0)
            else:
                pg.draw.circle(screen, (0, 0, 255), (blue_x, blue_y), 10, 1)

            pg.draw.circle(screen, (255, 255, 255), (center_x, center_y), 5, 1)

        # if ceil.robots[i].ot[0] != -1:
        #     x = ceil.robots[i].ot[0] * rect_side / side + outer_border_add
        #     y = ceil.robots[i].ot[1] * rect_side / side + outer_border_add
        #     pg.draw.circle(screen, (255, 0, 0), (x, y), 5, 0)

def on_click_hex():
    global ceil_type
    print("hex")
    ceil_type = 0
    ceil.max_x = 11
    ceil.max_y = 9

def on_click_square():
    global ceil_type
    print("square")
    ceil_type = 1
    ceil.max_x = 10
    ceil.max_y = 10

def command_panel():
    global ceil_type
    pg.init()
    screen = pg.display.set_mode([1210, 750])

    # Inputs
    robot_input = InputBox(810, 70, 200, 32)
    x_input = InputBox(810, 120, 200, 32)
    y_input = InputBox(810, 170, 200, 32)

    r2_input = InputBox(900, 360)
    x1_input = InputBox(790, 440, 100)
    y1_input = InputBox(790, 490, 100)

    x2_input = InputBox(940, 440, 100)
    y2_input = InputBox(940, 490, 100)

    x3_input = InputBox(1090, 440, 100)
    y3_input = InputBox(1090, 490, 100)

    # Input surfaces
    robot_surface = pg.Surface((robot_input.inputBox.width, robot_input.inputBox.height))
    x_surface = pg.Surface((x_input.inputBox.width, x_input.inputBox.height))
    y_surface = pg.Surface((y_input.inputBox.width, y_input.inputBox.height))

    r2_surface = pg.Surface((r2_input.inputBox.width, r2_input.inputBox.height))
    x1_surface = pg.Surface((x1_input.inputBox.width, x1_input.inputBox.height))
    y1_surface = pg.Surface((y1_input.inputBox.width, y1_input.inputBox.height))
    x2_surface = pg.Surface((x2_input.inputBox.width, x2_input.inputBox.height))
    y2_surface = pg.Surface((y2_input.inputBox.width, y2_input.inputBox.height))
    x3_surface = pg.Surface((x3_input.inputBox.width, x3_input.inputBox.height))
    y3_surface = pg.Surface((y3_input.inputBox.width, y3_input.inputBox.height))

    # Create a surface for the button
    button_surface = pg.Surface((200, 50))
    button_surface_set = pg.Surface((200, 50))
    button_surface_path = pg.Surface((200, 50))
    button_surface_disconnect = pg.Surface((200, 50))
    button_surface_update = pg.Surface((200, 50))

    button_surface_lu = pg.Surface((35, 35))
    button_surface_ld = pg.Surface((35, 35))
    button_surface_u = pg.Surface((35, 35))
    button_surface_d = pg.Surface((35, 35))
    button_surface_ru = pg.Surface((35, 35))
    button_surface_rd = pg.Surface((35, 35))

    button_surface_clockwise = pg.Surface((35, 35))
    button_surface_counterclockwise = pg.Surface((35, 35))

    # Button rectangles
    button_start = pg.Rect(760, 220, 200, 50)
    button_disconnect = pg.Rect(990, 220, 200, 50)
    button_set_coord = pg.Rect(870, 550, 200, 50)
    button_path = pg.Rect(760, 630, 200, 50)
    button_update = pg.Rect(990, 630, 200, 50)

    button_lu = pg.Rect(1050, 110, 35, 35)
    button_ld = pg.Rect(1050, 150, 35, 35)
    button_u = pg.Rect(1090, 90, 35, 35)
    button_d = pg.Rect(1090, 170, 35, 35)
    button_ru = pg.Rect(1130, 110, 35, 35)
    button_rd = pg.Rect(1130, 150, 35, 35)

    button_counterclockwise = pg.Rect(1050, 20, 35, 35)
    button_clockwise = pg.Rect(1130, 20, 35, 35)
    # (760, 290), (1190, 290)

    # Create a font object
    font = pg.font.Font(None, 29)

    text = font.render("Start move", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_surface.get_width() / 2, button_surface.get_height() / 2))
    text_disconnect = font.render("Disconnect", True, (255, 255, 255))
    text_disconnect_rect = text_disconnect.get_rect(
        center=(button_surface_disconnect.get_width() / 2, button_surface_disconnect.get_height() / 2))
    text_set = font.render("Set coordinates", True, (255, 255, 255))
    text_rect_set = text_set.get_rect(
        center=(button_surface_set.get_width() / 2, button_surface_set.get_height() / 2))
    text_path = font.render("Build path", True, (255, 255, 255))
    text_path_set = text_path.get_rect(
        center=(button_surface_path.get_width() / 2, button_surface_path.get_height() / 2))

    text_move = font.render("Start move", True, (255, 255, 255))
    text_move_rect = text_move.get_rect(
        center=(robot_input.inputBox.x + robot_input.inputBox.width / 2, robot_input.inputBox.y - 30))

    text_set_coords = font.render("Set robot coordinates", True, (255, 255, 255))
    text_set_coords_rect = text_set_coords.get_rect(
        center=(r2_input.inputBox.x + r2_input.inputBox.width / 2, r2_input.inputBox.y - 30))

    text_update = font.render("Update", True, (255, 255, 255))
    text_update_rect = text_update.get_rect(
        center=(button_surface_update.get_width() / 2, button_surface_update.get_height() / 2))

    r_text1 = font.render("Robot:", True, (255, 255, 255))
    r_text1_rect = text.get_rect(center=(
        robot_input.inputBox.x - r_text1.get_width() + 40, robot_input.inputBox.y + robot_input.inputBox.height / 2))

    x_text = font.render("X:", True, (255, 255, 255))
    x_text_rect = text.get_rect(center=(
        x_input.inputBox.x - x_text.get_width() + 40, x_input.inputBox.y + x_input.inputBox.height / 2))

    y_text = font.render("Y:", True, (255, 255, 255))
    y_text_rect = text.get_rect(center=(
        y_input.inputBox.x - y_text.get_width() + 40, y_input.inputBox.y + y_input.inputBox.height / 2))

    r_text2 = font.render("Robot N.", True, (255, 255, 255))
    r_text2_rect = text.get_rect(center=(
        r2_input.inputBox.x - r_text2.get_width() + 40, r2_input.inputBox.y + r2_input.inputBox.height / 2))

    text_hand_1 = font.render("Hand 1", True, (255, 255, 255))
    text_hand_1_rect = text_hand_1.get_rect(center=(
        x1_input.inputBox.x + x1_input.inputBox.width / 2, x1_input.inputBox.y - 20))

    text_hand_2 = font.render("Hand 2", True, (255, 255, 255))
    text_hand_2_rect = text_hand_2.get_rect(center=(
        x2_input.inputBox.x + x2_input.inputBox.width / 2, x2_input.inputBox.y - 20))

    text_hand_3 = font.render("Hand 3", True, (255, 255, 255))
    text_hand_3_rect = text_hand_3.get_rect(center=(
        x3_input.inputBox.x + x3_input.inputBox.width / 2, x3_input.inputBox.y - 20))

    x1_text = font.render("X:", True, (255, 255, 255))
    x1_text_rect = x1_text.get_rect(center=(
        x1_input.inputBox.x - x1_text.get_width(), x1_input.inputBox.y + x1_input.inputBox.height / 2))

    x2_text = font.render("X:", True, (255, 255, 255))
    x2_text_rect = x2_text.get_rect(center=(
        x2_input.inputBox.x - x2_text.get_width(), x2_input.inputBox.y + x2_input.inputBox.height / 2))

    x3_text = font.render("X:", True, (255, 255, 255))
    x3_text_rect = x3_text.get_rect(center=(
        x3_input.inputBox.x - x3_text.get_width(), x3_input.inputBox.y + x3_input.inputBox.height / 2))

    y1_text = font.render("Y:", True, (255, 255, 255))
    y1_text_rect = y1_text.get_rect(center=(
        y1_input.inputBox.x - y1_text.get_width(), y1_input.inputBox.y + y1_input.inputBox.height / 2))

    y2_text = font.render("Y:", True, (255, 255, 255))
    y2_text_rect = y2_text.get_rect(center=(
        y2_input.inputBox.x - y2_text.get_width(), y2_input.inputBox.y + y2_input.inputBox.height / 2))

    y3_text = font.render("Y:", True, (255, 255, 255))
    y3_text_rect = y3_text.get_rect(center=(
        y3_input.inputBox.x - y3_text.get_width(), y3_input.inputBox.y + y3_input.inputBox.height / 2))

    clock = pg.time.Clock()
    screen.fill((48, 48, 48))

    # radioButtons = [
    #     RadioButton(1050, 25, 115, 25, font, "hexagonal", on_click_hex),
    #     RadioButton(1050, 55, 115, 25, font, "square", on_click_square)
    # ]
    # for rb in radioButtons:
    #     rb.setRadioButtons(radioButtons)
    # radioButtons[0].clicked = True
    # group = pg.sprite.Group(radioButtons)

    # running = True
    global running, sock
    while running:  # main loop
        events = pg.event.get()
        # BUTTON EVENTS
        for event in events:
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                sock.settimeout(1.0)
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                sys.exit(1)
                # Check for the mouse button down event
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # Call the on_mouse_button_down() function
                if button_start.collidepoint(event.pos):
                    if (robot_input.text == '') or (x_input.text == '') or (y_input.text == ''):
                        print("Invalid input")
                    else:
                        robot_num = int(robot_input.text)
                        try:
                            x = float(x_input.text)
                            y = float(y_input.text)
                        except:
                            print("Invalid input")
                            break
                        # x = int(x_input.text)
                        # y = int(y_input.text)
                        robot_input.text = ''
                        x_input.text = ''
                        y_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break

                        print(f"Robot no. {robot_num} to ({x}, {y})")
                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        elif (x < 0) or (x > 2000) or (y < 0) or (y > 2000):
                            print("Invalid coordinates")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            xo_s, yo_s = ceil.robots[robot_num].get_center()
                            # t_path = threading.Thread(target=ceil.path_manual, args=[robot_num, x])
                            # t_path.start()

                            print(f"Os: ({xo_s}, {yo_s}); Ot: ({x}, {y})")
                            # break
                            global ot
                            ot[0] = x
                            ot[1] = y
                            ceil.robots[robot_num].os = (xo_s, yo_s)
                            ceil.robots[robot_num].ot = (x, y)
                            # path_, centers = ceil.build_path(0, xo_s, yo_s, xo_t, yo_t)
                            if ceil_type == 0:
                                t_path = threading.Thread(target=ceil.build_path_hex,
                                                          args=[robot_num, xo_s, yo_s, x, y])
                                t_path.start()
                                t_path.join()
                            elif ceil_type == 1:
                                t_path = threading.Thread(target=ceil.build_path_lines_2,
                                                          args=[robot_num, xo_s, yo_s, x, y])
                                t_path.start()
                                t_path.join()

                            t_start = threading.Thread(target=ceil.start_robot_by_path, args=[robot_num])
                            t_start.start()
                            # t1 = threading.Thread(target=ceil.move_robot, args=[robot_num, x, y])
                            # t1.start()
                if button_disconnect.collidepoint(event.pos):
                    # print("SET COORD BUTTON")
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        print("disconnect")
                        robot_num = int(robot_input.text)
                        ceil.robots[robot_num].socket.shutdown(2)
                        ceil.robots[robot_num].socket.close()
                        ceil.robots[robot_num].isAlive = False
                if button_update.collidepoint(event.pos):
                    # print("SET COORD BUTTON")
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        print("update")
                        robot_num = int(robot_input.text)
                        ceil.robots[robot_num].get_robot_params()
                        draw_ceil(screen)
                if button_set_coord.collidepoint(event.pos):
                    # print("SET COORD BUTTON")
                    x1, x2, x3, y1, y2, y3 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
                    if (((x1_input.text == '') or (y1_input.text == '')
                            or (x2_input.text == '') or (y2_input.text == ''))
                            or (x3_input.text == '') or (y3_input.text == '')
                            or (r2_input.text == '')):
                        print("Invalid input")
                    else:
                        robot_num = int(r2_input.text)
                        try:
                            x1 = float(x1_input.text)
                            y1 = float(y1_input.text)
                            x2 = float(x2_input.text)
                            y2 = float(y2_input.text)
                            x3 = float(x3_input.text)
                            y3 = float(y3_input.text)
                        except:
                            print("Invalid input")
                            break
                        r2_input.text = ''
                        x1_input.text = ''
                        y1_input.text = ''
                        x2_input.text = ''
                        y2_input.text = ''
                        x3_input.text = ''
                        y3_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break

                        print(f"Set coords: Robot no. {robot_num} to ({x1}, {y1}), ({x2}, {y2}), ({x3}, {y3})")
                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        elif ((x1 < 0) or (x1 > 2000) or (y1 < 0) or (y1 > 2000)
                            or (x2 < 0) or (x2 > 2000) or (y2 < 0) or (y2 > 2000)
                              or (x3 < 0) or (x3 > 2000) or (y3 < 0) or (y3 > 2000)):
                            print("Invalid coordinates")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            ceil.set_hand_coordinates(robot_num, x1, y1, x2, y2, x3, y3)
                            draw_ceil(screen)
                            # t1 = threading.Thread(target=ceil.start_move, args=[robot_num, x, y])
                            # t1.start()
                    # t1 = threading.Thread(target=imitate_command)
                    # t1.start()
                if button_path.collidepoint(event.pos):
                    if len(ceil.robots) == 0:
                        break
                    print("Build path")
                    xo_t = random.randint(0, 2000)
                    yo_t = random.randint(0, 2000)
                    xo_s, yo_s = ceil.robots[0].get_center()
                    print(f"Os: ({xo_s}, {yo_s}); Ot: ({xo_t}, {yo_t})")
                    # global ot
                    ceil.robots[0].ot = (xo_t, yo_t)

                    # path_, centers = ceil.build_path(0, xo_s, yo_s, xo_t, yo_t)
                    if ceil_type == 0:
                        t_path = threading.Thread(target=ceil.build_path_hex,
                                                  args=[robot_num, xo_s, yo_s, x, y])
                        t_path.start()
                        t_path.join()
                    elif ceil_type == 1:
                        t_path = threading.Thread(target=ceil.build_path_lines_2,
                                                  args=[robot_num, xo_s, yo_s, x, y])
                        t_path.start()
                        t_path.join()

                    # t_path.join()
                    # t_start = threading.Thread(target=ceil.start_robot_by_path, args=[0])
                    # t_start.start()
                    # global path
                    # path = path_[:]
                if button_lu.collidepoint(event.pos):
                    if ceil_type != 0:
                        print("Wrong ceil type!")
                        break
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        try:
                            robot_num = int(robot_input.text)
                        except:
                            print("Invalid input")
                            break
                        # robot_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break
                        if ceil.robots[robot_num].isMoving:
                            print("Robot is moving already!")
                            break

                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            t_step = threading.Thread(target=ceil.path_manual, args=[robot_num, 0])
                            t_step.start()
                if button_ld.collidepoint(event.pos):
                    if ceil_type != 0:
                        print("Wrong ceil type!")
                        break
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        try:
                            robot_num = int(robot_input.text)
                        except:
                            print("Invalid input")
                            break
                        # robot_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break
                        if ceil.robots[robot_num].isMoving:
                            print("Robot is moving already!")
                            break

                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            t_step = threading.Thread(target=ceil.path_manual, args=[robot_num, 1])
                            t_step.start()
                if button_u.collidepoint(event.pos):
                    if ceil_type != 0:
                        print("Wrong ceil type!")
                        break
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        try:
                            robot_num = int(robot_input.text)
                        except:
                            print("Invalid input")
                            break
                        # robot_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break
                        if ceil.robots[robot_num].isMoving:
                            print("Robot is moving already!")
                            break

                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            t_step = threading.Thread(target=ceil.path_manual, args=[robot_num, 2])
                            t_step.start()
                if button_d.collidepoint(event.pos):
                    if ceil_type != 0:
                        print("Wrong ceil type!")
                        break
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        try:
                            robot_num = int(robot_input.text)
                        except:
                            print("Invalid input")
                            break
                        # robot_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break
                        if ceil.robots[robot_num].isMoving:
                            print("Robot is moving already!")
                            break

                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            t_step = threading.Thread(target=ceil.path_manual, args=[robot_num, 3])
                            t_step.start()
                if button_ru.collidepoint(event.pos):
                    if ceil_type != 0:
                        print("Wrong ceil type!")
                        break
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        try:
                            robot_num = int(robot_input.text)
                        except:
                            print("Invalid input")
                            break
                        # robot_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break
                        if ceil.robots[robot_num].isMoving:
                            print("Robot is moving already!")
                            break

                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            t_step = threading.Thread(target=ceil.path_manual, args=[robot_num, 4])
                            t_step.start()
                if button_rd.collidepoint(event.pos):
                    if ceil_type != 0:
                        print("Wrong ceil type!")
                        break
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        try:
                            robot_num = int(robot_input.text)
                        except:
                            print("Invalid input")
                            break
                        # robot_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break
                        if ceil.robots[robot_num].isMoving:
                            print("Robot is moving already!")
                            break

                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            t_step = threading.Thread(target=ceil.path_manual, args=[robot_num, 5])
                            t_step.start()
                if button_counterclockwise.collidepoint(event.pos):
                    if ceil_type != 0:
                        print("Wrong ceil type!")
                        break
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        try:
                            robot_num = int(robot_input.text)
                        except:
                            print("Invalid input")
                            break
                        # robot_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break
                        if ceil.robots[robot_num].isMoving:
                            print("Robot is moving already!")
                            break

                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            t_turn = threading.Thread(target=ceil.turn_clock, args=[robot_num, False])
                            t_turn.start()
                if button_clockwise.collidepoint(event.pos):
                    if ceil_type != 0:
                        print("Wrong ceil type!")
                        break
                    if robot_input.text == '':
                        print("Invalid input")
                    else:
                        try:
                            robot_num = int(robot_input.text)
                        except:
                            print("Invalid input")
                            break
                        # robot_input.text = ''

                        if not ceil.robots[robot_num].isAlive:
                            print("Robot is inactive")
                            break
                        if ceil.robots[robot_num].isMoving:
                            print("Robot is moving already!")
                            break

                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        else:
                            ceil.robots[robot_num].get_robot_params()
                            t_turn = threading.Thread(target=ceil.turn_clock, args=[robot_num, True])
                            t_turn.start()

            robot_input.handle_event(event)
            x_input.handle_event(event)
            y_input.handle_event(event)

            r2_input.handle_event(event)
            x1_input.handle_event(event)
            y1_input.handle_event(event)
            x2_input.handle_event(event)
            y2_input.handle_event(event)
            x3_input.handle_event(event)
            y3_input.handle_event(event)

        # START MOVE BUTTON
        # Check if the mouse is over the button. This will create the button hover effect
        if button_start.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface, (5, 99, 46), (1, 1, 200, 48))

        # Show the button text
        button_surface.blit(text, text_rect)
        # Draw the button on the screen
        screen.blit(button_surface, (button_start.x, button_start.y))

        # DISCONNECT BUTTON
        # Check if the mouse is over the button. This will create the button hover effect
        if button_disconnect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_disconnect, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_disconnect, (5, 99, 46), (1, 1, 200, 48))

        # Show the button text
        button_surface_disconnect.blit(text_disconnect, text_disconnect_rect)
        # Draw the button on the screen
        screen.blit(button_surface_disconnect, (button_disconnect.x, button_disconnect.y))

        # SET COORDINATES BUTTON
        if button_set_coord.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_set, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_set, (5, 99, 46), (1, 1, 200, 48))

        button_surface_set.blit(text_set, text_rect_set)
        screen.blit(button_surface_set, (button_set_coord.x, button_set_coord.y))

        # BUILD PATH BUTTON
        if button_path.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_path, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_path, (5, 99, 46), (1, 1, 200, 48))

        button_surface_path.blit(text_path, text_path_set)
        screen.blit(button_surface_path, (button_path.x, button_path.y))

        # UPDATE PARAMS BUTTON
        if button_update.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_update, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_update, (5, 99, 46), (1, 1, 200, 48))

        button_surface_update.blit(text_update, text_update_rect)
        screen.blit(button_surface_update, (button_update.x, button_update.y))


        # manual control buttons
        if button_lu.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_lu, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_lu, (5, 99, 46), (1, 1, 200, 48))

        if button_ld.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_ld, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_ld, (5, 99, 46), (1, 1, 200, 48))

        if button_u.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_u, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_u, (5, 99, 46), (1, 1, 200, 48))

        if button_d.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_d, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_d, (5, 99, 46), (1, 1, 200, 48))

        if button_ru.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_ru, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_ru, (5, 99, 46), (1, 1, 200, 48))

        if button_rd.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_rd, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_rd, (5, 99, 46), (1, 1, 200, 48))

        if button_counterclockwise.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_counterclockwise, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_counterclockwise, (5, 99, 46), (1, 1, 200, 48))

        if button_clockwise.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_clockwise, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_clockwise, (5, 99, 46), (1, 1, 200, 48))

        # Show the button text
        # button_surface.blit(text, text_rect)
        # Draw the button on the screen
        screen.blit(button_surface_lu, (button_lu.x, button_lu.y))
        screen.blit(button_surface_ld, (button_ld.x, button_ld.y))
        screen.blit(button_surface_u, (button_u.x, button_u.y))
        screen.blit(button_surface_d, (button_d.x, button_d.y))
        screen.blit(button_surface_ru, (button_ru.x, button_ru.y))
        screen.blit(button_surface_rd, (button_rd.x, button_rd.y))

        screen.blit(button_surface_counterclockwise, (button_counterclockwise.x, button_counterclockwise.y))
        screen.blit(button_surface_clockwise, (button_clockwise.x, button_clockwise.y))


        pg.draw.line(screen, (255, 255, 255), (760, 290), (1090 + x3_input.inputBox.width, 290))
        pg.draw.line(screen, (255, 255, 255), (760, 620), (1090 + x3_input.inputBox.width, 620))

        screen.blit(text_move, text_move_rect)
        screen.blit(text_set_coords, text_set_coords_rect)
        screen.blit(text_update, text_update_rect)
        screen.blit(r_text1, r_text1_rect)
        screen.blit(x_text, x_text_rect)
        screen.blit(y_text, y_text_rect)

        screen.blit(r_text2, r_text2_rect)
        screen.blit(text_hand_1, text_hand_1_rect)
        screen.blit(text_hand_2, text_hand_2_rect)
        screen.blit(text_hand_3, text_hand_3_rect)

        screen.blit(x1_text, x1_text_rect)
        screen.blit(x2_text, x2_text_rect)
        screen.blit(x3_text, x3_text_rect)
        screen.blit(y1_text, y1_text_rect)
        screen.blit(y2_text, y2_text_rect)
        screen.blit(y3_text, y3_text_rect)

        # Draw input boxes
        screen.blit(robot_surface, (robot_input.inputBox.x, robot_input.inputBox.y))
        screen.blit(x_surface, (x_input.inputBox.x, x_input.inputBox.y))
        screen.blit(y_surface, (y_input.inputBox.x, y_input.inputBox.y))

        screen.blit(r2_surface, (r2_input.inputBox.x, r2_input.inputBox.y))
        screen.blit(x1_surface, (x1_input.inputBox.x, x1_input.inputBox.y))
        screen.blit(y1_surface, (y1_input.inputBox.x, y1_input.inputBox.y))
        screen.blit(x2_surface, (x2_input.inputBox.x, x2_input.inputBox.y))
        screen.blit(y2_surface, (y2_input.inputBox.x, y2_input.inputBox.y))
        screen.blit(x3_surface, (x3_input.inputBox.x, x3_input.inputBox.y))
        screen.blit(y3_surface, (y3_input.inputBox.x, y3_input.inputBox.y))

        draw_ceil(screen)
        robot_input.draw(screen)
        x_input.draw(screen)
        y_input.draw(screen)
        r2_input.draw(screen)
        x1_input.draw(screen)
        y1_input.draw(screen)
        x2_input.draw(screen)
        y2_input.draw(screen)
        x3_input.draw(screen)
        y3_input.draw(screen)
        clock.tick(60)

        # group.update(events)
        # group.draw(screen)

        pg.display.update()

