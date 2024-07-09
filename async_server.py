#!/usr/bin/python3


import errno
import threading
import socket
import logging
import time
from struct import unpack

from pygame import font

from arm_geometry_test import *
from pygame_elements import InputBox
from robot import *
from ceil import *

logger = logging.getLogger('main')


BIND_ADDRESS = ('192.168.0.91', 8686)
BACKLOG = 5

ceil = Ceil()


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
            print("---")
            # print(f"Robot no. {robot_num}")
            ceil.robots[robot_num].print()
            # move_robot_simu(robot_num)
            print("---")
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
    # ceil.turn_robot_hu_to_vr(0)
    # ceil.turn_robot_vr_to_hu(0)
    # ceil.start_move(0, 500.0, 300.0)
    ceil.start_move(0, 500.0, 700.0)
    # ceil.move_robot(0, 400.0, 0)
    # ceil.move_robot(0, 300.0, 0)
    # ceil.turn_robot(0)
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

    # t1 = threading.Thread(target=imitate_command)
    # t1.start()

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

            hand_red_x, hand_red_y = (hand_points[0][0] * rect_side / side + outer_border_add,
                                      hand_points[0][1] * rect_side / side + outer_border_add)
            hand_green_x, hand_green_y = (hand_points[1][0] * rect_side / side + outer_border_add,
                                          hand_points[1][1] * rect_side / side + outer_border_add)
            hand_blue_x, hand_blue_y = (hand_points[2][0] * rect_side / side + outer_border_add,
                                        hand_points[2][1] * rect_side / side + outer_border_add)

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


def command_panel():
    pg.init()
    screen = pg.display.set_mode([1210, 750])

    # Inputs
    robot_input = InputBox(870, 50, 200, 32)
    x_input = InputBox(870, 100, 200, 32)
    y_input = InputBox(870, 150, 200, 32)

    r2_input = InputBox(900, 320)
    x1_input = InputBox(750, 390)
    y1_input = InputBox(750, 440)

    x2_input = InputBox(900, 390)
    y2_input = InputBox(900, 440)

    x3_input = InputBox(1050, 390)
    y3_input = InputBox(1050, 440)

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

    # Create a font object
    font = pg.font.Font(None, 24)

    # Render text
    text = font.render("Start move", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_surface.get_width() / 2, button_surface.get_height() / 2))
    text_set = font.render("Set coordinates", True, (255, 255, 255))
    text_rect_set = text_set.get_rect(center=(button_surface_set.get_width() / 2, button_surface_set.get_height() / 2))

    r_text1 = font.render("Robot №", True, (255, 255, 255))
    r_text1_rect = text.get_rect(center=(robot_surface.get_width() / 2, robot_surface.get_height() / 2 - 50))

    # Button rectangles
    button_start = pg.Rect(870, 200, 200, 50)
    button_set_coord = pg.Rect(870, 500, 200, 50)

    clock = pg.time.Clock()
    screen.fill((48, 48, 48))

    running = True
    while True:  # main loop
        events = pg.event.get()
        # BUTTON EVENTS
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
                # Check for the mouse button down event
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # Call the on_mouse_button_down() function
                if button_start.collidepoint(event.pos):
                    # print("Button clicked!")
                    if (robot_input.text == '') or (x_input.text == '') or (y_input.text == ''):
                        print("Invalid input")
                    else:
                        robot_num = int(robot_input.text)
                        x = int(x_input.text)
                        y = int(y_input.text)
                        robot_input.text = ''
                        x_input.text = ''
                        y_input.text = ''
                        print(f"Robot no. {robot_num} to ({x}, {y})")
                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        elif (x < 0) or (x > 2000) or (y < 0) or (y > 2000):
                            print("Invalid coordinates")
                        else:
                            # t1 = threading.Thread(target=ceil.start_move, args=[robot_num, x, y])
                            t1 = threading.Thread(target=ceil.move_robot, args=[robot_num, x, y])
                            t1.start()
                            # t1 = threading.Thread(target=imitate_command)
                if button_set_coord.collidepoint(event.pos):
                    print("SET COORD BUTTON")
                    if (((x1_input.text == '') or (y1_input.text == '')
                            or (x2_input.text == '') or (y2_input.text == ''))
                            or (x3_input.text == '') or (y3_input.text == '')
                            or (r2_input.text == '')):
                        print("Invalid input")
                    else:
                        robot_num = int(r2_input.text)
                        x1 = int(x1_input.text)
                        y1 = int(y1_input.text)
                        x2 = int(x2_input.text)
                        y2 = int(y2_input.text)
                        x3 = int(x3_input.text)
                        y3 = int(y3_input.text)
                        r2_input.text = ''
                        x1_input.text = ''
                        y1_input.text = ''
                        x2_input.text = ''
                        y2_input.text = ''
                        x3_input.text = ''
                        y3_input.text = ''
                        print(f"Set coords: Robot no. {robot_num} to ({x1}, {y1}), ({x2}, {y2}), ({x3}, {y3})")
                        if (robot_num < 0) or (robot_num >= len(ceil.robots)):
                            print("There's no robot with such No.")
                        elif ((x1 < 0) or (x1 > 2000) or (y1 < 0) or (y1 > 2000)
                            or (x2 < 0) or (x2 > 2000) or (y2 < 0) or (y2 > 2000)
                              or (x3 < 0) or (x3 > 2000) or (y3 < 0) or (y3 > 2000)):
                            print("Invalid coordinates")
                        else:
                            ceil.set_hand_coordinates(robot_num, x1, y1, x2, y2, x3, y3)
                            draw_ceil(screen)
                            # t1 = threading.Thread(target=ceil.start_move, args=[robot_num, x, y])
                            # t1.start()
                    # t1 = threading.Thread(target=imitate_command)
                    # t1.start()

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

        # SET COORDINATES BUTTON
        # Check if the mouse is over the button. This will create the button hover effect
        if button_set_coord.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(button_surface_set, (5, 60, 57), (1, 1, 200, 48))
        else:
            pg.draw.rect(button_surface_set, (5, 99, 46), (1, 1, 200, 48))

            # Show the button text
        button_surface_set.blit(text_set, text_rect_set)
        # Draw the button on the screen
        screen.blit(button_surface_set, (button_set_coord.x, button_set_coord.y))

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

        pg.display.update()

