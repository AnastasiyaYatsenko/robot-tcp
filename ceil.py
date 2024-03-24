import select
import sys
import time
from struct import pack
from waiting import wait

from arm_geometry_test import *
from robot import *
import pygame as pg
import pygame_textinput


# клас з функціями роботи з роботами
class Ceil:

    def __init__(self):
        self.max_x = 10
        self.max_y = 10
        # масив лунок
        self.ceil_arr = [[0 for i in range(self.max_x)] for j in range(self.max_y)]

        # дефолтні координати для роботів
        self.default_coordinates = {"x1": 100,
                                    "y1": 100,
                                    "x2": 300,
                                    "y2": 100,
                                    "x3": 500,
                                    "y3": 100}

        self.default_ceil = {"x1": 0,
                             "y1": 0,
                             "x2": 1,
                             "y2": 0,
                             "x3": 2,
                             "y3": 0}

        # масив роботів
        self.robots = []

        self.rect_side = 620
        self.side = 2 * size["netBorder"] + (self.max_x - 1) * size["netStep"]
        self.rect_border = int(size["netBorder"] * self.rect_side / self.side)
        self.rect_step = int(size["netStep"] * self.rect_side / self.side)

    # додавання роботу
    def add_robot(self, ip):
        r = Robot()
        r.set_ip(ip)
        r.set_coordinates(self.default_coordinates["x1"], self.default_coordinates["y1"],
                          self.default_coordinates["x2"], self.default_coordinates["y2"],
                          self.default_coordinates["x3"], self.default_coordinates["y3"])

        # self.ceil_arr[0][0] = 1
        # self.ceil_arr[0][1] = 1
        # self.ceil_arr[0][2] = 1

        self.ceil_arr[self.default_ceil["y1"]][self.default_ceil["x1"]] = 1
        self.ceil_arr[self.default_ceil["y2"]][self.default_ceil["x2"]] = 1
        self.ceil_arr[self.default_ceil["y3"]][self.default_ceil["x3"]] = 1

        # set start coordinates, paarameters will be handled with data reading
        self.robots.append(r)

    # TODO
    # перевірка, чи можна в точку (х,у) поставити лапу
    def is_point_free(self, x, y, robot_num):
        # for i in range(robots_num):
        #     c_x, c_y = robots[i].get_center()
        #     if (x - c_x)**2 + (y - c_y)**2 <= robot_hand_len**2:
        #         return False

        # must check if there's no possible robot movements in this point

        # DON'T FORGET coordinates_to_ceil !!!

        for i in range(len(self.robots)):
            if i == robot_num:
                continue
            else:
                if (self.robots[i].hands[0].x == self.robots[i].hands[1].x and self.robots[i].hands[1].x ==
                    self.robots[i].hands[2].x) \
                        or (
                        self.robots[i].hands[0].y == self.robots[i].hands[1].y and self.robots[i].hands[1].y ==
                        self.robots[i].hands[2].y):
                    pass
                else:
                    pass
        if self.ceil_arr[y][x] == 0:
            return True
        else:
            return False

    # виведення масиву стелі на екран
    def show_ceil(self):
        print("- - - - - - - - - -")
        for i in range(self.max_y):
            for j in range(self.max_x):
                print(self.ceil_arr[i][j], end=' ')
            print()
        print("- - - - - - - - - -")

    # def draw_ceil(self):
    #     # rect_side = 620
    #     # side = 2 * size["netBorder"] + (self.max_x - 1) * size["netStep"]
    #     # rect_border = int(size["netBorder"]*rect_side/side)
    #     # rect_step = int(size["netStep"] * rect_side / side)
    #
    #     # side_x = 2*size["netBorder"]+(self.max_x-1)*size["netStep"]
    #     # side_y = 2 * size["netBorder"] + (self.max_y - 1) * size["netStep"]
    #     pg.draw.rect(self.screen, (255, 255, 255), (20, 20, 640, 640))
    #     pg.draw.rect(self.screen, (0, 0, 0), (30, 30, 620, 620), 1)
    #
    #     for y in range(self.max_y):
    #         for x in range(self.max_x):
    #             pg.draw.circle(self.screen, (0, 0, 0), (self.rect_border+x*self.rect_step+30,
    #                                                     self.rect_border+y*self.rect_step+30), 5, 1)
    #
    #     for r in self.robots:
    #         points = r.get_all_points()
    #         # self.rect_border + x * self.rect_step + 30
    #         red_x, red_y = (self.rect_border+points[0]*self.rect_step+30,
    #                         self.rect_border + points[1] * self.rect_step + 30)
    #         green_x, green_y = (self.rect_border + points[2] * self.rect_step + 30,
    #                         self.rect_border + points[3] * self.rect_step + 30)
    #         blue_x, blue_y = (self.rect_border + points[4] * self.rect_step + 30,
    #                         self.rect_border + points[5] * self.rect_step + 30)
    #         center_x, center_y = (self.rect_border + points[6] * self.rect_step + 30,
    #                             self.rect_border + points[7] * self.rect_step + 30)
    #
    #         pg.draw.line(self.screen, (255, 0, 0), (red_x, red_y), (center_x, center_y), 1)
    #         pg.draw.line(self.screen, (0, 255, 0), (green_x, green_y), (center_x, center_y), 1)
    #         pg.draw.line(self.screen, (0, 0, 255), (blue_x, blue_y), (center_x, center_y), 1)
    #
    #         pg.draw.circle(self.screen, (255, 0, 0), (red_x, red_y), 5, 1)
    #         pg.draw.circle(self.screen, (0, 255, 0), (green_x, green_y), 5, 1)
    #         pg.draw.circle(self.screen, (0, 0, 255), (blue_x, blue_y), 5, 1)
    #         pg.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 5, 1)
    #
    #
    # def command_panel(self):
    #     print('gogo')
    #     pg.init()
    #     self.screen = pg.display.set_mode([1200, 700])
    #     robot_input = pygame_textinput.TextInputVisualizer()
    #     x_input = pygame_textinput.TextInputVisualizer()
    #     y_input = pygame_textinput.TextInputVisualizer()
    #     self.screen.fill((48, 48, 48))
    #
    #     # pg.draw.rect(self.screen, (255, 255, 255), (20, 20, 620, 620))
    #
    #     running = True
    #     # while self.get_working():
    #     #     for event in pg.event.get():
    #     #         if event.type == pg.QUIT:
    #     #             pass
    #     while running:  # main game loop
    #         events = pg.event.get()
    #         self.draw_ceil()
    #         # Feed it with events every frame
    #         # robot_input.update(events)
    #         # x_input.update(events)
    #         # y_input.update(events)
    #         # Blit its surface onto the screen
    #         # self.screen.blit(robot_input.surface, (10, 10))
    #         # self.screen.blit(x_input.surface, (100, 10))
    #         # self.screen.blit(y_input.surface, (200, 10))
    #
    #         for event in events:
    #             if event.type == pg.QUIT:
    #                 running = False
    #                 pg.quit()
    #                 sys.exit()
    #
    #         pg.display.update()

    # etc

    # зміна координат руки
    def move_hand(self, robot_num, hand_num, x, y):
        ceil_x = coordinates_to_ceil(x)
        ceil_y = coordinates_to_ceil(y)
        # print(f"CEIL x: {ceil_x}, y: {ceil_y}")
        if self.ceil_arr[ceil_y][ceil_x] == 0:
            old_x = coordinates_to_ceil(self.robots[robot_num].hands[hand_num].x)
            old_y = coordinates_to_ceil(self.robots[robot_num].hands[hand_num].y)
            self.ceil_arr[old_y][old_x] = 0

            self.ceil_arr[ceil_y][ceil_x] = 1
            self.robots[robot_num].set_hand_coordinates(hand_num, x, y)

    def get_real_coordinates(self, robot_num, hand_a, hand_b, hand_c, shifts, angs):
        # delta = 1e-12  # 47.999999999->48.0 або -0.0000000001->0.0
        delta = 0

        sa = shifts[hand_a]
        sb = shifts[hand_b]
        sc = shifts[hand_c]

        aa = angs[hand_a]
        ab = angs[hand_b]
        ac = angs[hand_c]

        # координати центру відносно А - це "віддзеркалені" кординати А відносно центру
        o = (-1 * sa * math.sin(aa * math.pi / 180),
             -1 * sa * math.cos(aa * math.pi / 180) + delta)
        a = (0, 0)
        b = (sb * math.sin(ab * math.pi / 180) + o[0] + delta,
             sb * math.cos(ab * math.pi / 180) + o[1] + delta)
        c = (sc * math.sin(ac * math.pi / 180) + o[0] + delta,
             sc * math.cos(ac * math.pi / 180) + o[1] + delta)

        a_real = a[0] + self.robots[robot_num].hands[hand_a].x, a[1] + self.robots[robot_num].hands[hand_a].y
        b_real = b[0] + self.robots[robot_num].hands[hand_a].x, b[1] + self.robots[robot_num].hands[hand_a].y
        c_real = c[0] + self.robots[robot_num].hands[hand_a].x, c[1] + self.robots[robot_num].hands[hand_a].y
        o_real = o[0] + self.robots[robot_num].hands[hand_a].x, o[1] + self.robots[robot_num].hands[hand_a].y

        coord = [(0, 0), (0, 0), (0, 0), (0, 0)]
        coord[hand_a] = (a_real[0], a_real[1])
        coord[hand_b] = (b_real[0], b_real[1])
        coord[hand_c] = (c_real[0], c_real[1])
        coord[3] = (o_real[0], o_real[1])
        # print(f"Coord: {coord}")

        self.robots[robot_num].set_real_coordinates(coord[0], coord[1], coord[2], coord[3])

    # візуалізація лап робота для функцій переміщення
    #    .
    #  / | \
    # C  A  B
    # рух вперед (вправо від центру)
    def move_forward(self, robot_num, hand_a, hand_b, hand_c):
        h = 48
        L = size["netStep"]  # 200
        N = 20  # amount of substeps

        # Умовні позначення рук
        # А - найкоротша на початку
        # В - одна з двох найдовших на початку, не змінює координати
        # С - рука, що змінює свої координати (пролітає)
        # рука A на мінімальній відстані від вісі = h = 48mm
        # руки В і С на відстані sqrt(L^2+h^2) = 205.68mm

        # кут, з яким А входить до процедури - це напрям "компасу", загального для усіх
        # з початковим кутом А нічого не робимо, його значення - це і є показник компасу
        aa0 = self.robots[robot_num].hands[hand_a].ang

        for n in range(N + 1):
            # отримуємо параметри для рук робота для поточного кроку
            shifts, angs, holds = calc_params_forward(L, N, n, h, aa0, hand_a, hand_b, hand_c)

            # send these parameters to robot
            # send_destination(robot_num, shifts, angs, holds)
            # print(
            #     f"{robot_num}: [{shifts[0]}, {angs[0]}, {holds[0]}], [{shifts[1]}, {angs[1]}, {holds[1]}], [{shifts[2]}, {angs[2]}, {holds[2]}]")
            # wait until the robot will respond
            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            # print(f"PACKAGE: {p}")
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            # print(f"BUFFER: {self.robots[robot_num].out_buffer}")
            # print(self.robots[robot_num].socket)
            self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def move_backward(self, robot_num, hand_a, hand_b, hand_c):
        # A средняя, C передняя, B задняя вылетающая (не меняем расположения, но двигаемся обратно)
        h = 48
        L = size["netStep"]  # 200
        N = 20  # amount of substeps

        # Умовні позначення рук
        # А - найкоротша на початку
        # C - одна з двох найдовших на початку, не змінює координати
        # B - рука, що змінює свої координати (пролітає)
        # рука A на мінімальній відстані від вісі = h = 48mm
        # руки В і С на відстані sqrt(L^2+h^2) = 205.68mm

        # кут, з яким А входить до процедури - це напрям "компасу", загального для усіх
        # з початковим кутом А нічого не робимо, його значення - це і є показник компасу
        aa0 = self.robots[robot_num].hands[hand_a].ang

        for n in range(N + 1):
            # отримуємо параметри для рук робота для поточного кроку
            shifts, angs, holds = calc_params_backward(L, N, n, h, aa0, hand_a, hand_b, hand_c)

            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            # print(f"PACKAGE: {p}")
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            # print(f"BUFFER: {self.robots[robot_num].out_buffer}")
            # print(self.robots[robot_num].socket)
            self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1



    # перевірка наявності робота в масиві за IP
    def match_IPs(self, ip):
        robot_i = -1
        for i in range(len(self.robots)):
            if self.robots[i].get_ip() == ip:
                robot_i = i
        return robot_i

    def get_hand_letters(self, robot_num):
        #  hand a - center hand
        #  hand b - right hand
        #  hand c - left hand
        if not (self.robots[robot_num].is_horizontal_aligned() or self.robots[robot_num].is_vertical_aligned()):
            # call another function
            return -1, -1, -1
        center_x, center_y = self.robots[robot_num].get_center()
        a = -1
        b = -1
        c = -1
        eps = 0.1
        if (self.robots[robot_num].hands[0].lin < self.robots[robot_num].hands[1].lin
                and self.robots[robot_num].hands[0].lin < self.robots[robot_num].hands[2].lin):
            a = 0
        elif (self.robots[robot_num].hands[1].lin < self.robots[robot_num].hands[0].lin
              and self.robots[robot_num].hands[1].lin < self.robots[robot_num].hands[2].lin):
            a = 1
        else:
            a = 2
        bc = [0, 1, 2]
        bc.remove(a)
        # print(bc)
        delta_x = self.robots[robot_num].hands[a].x - center_x
        delta_y = self.robots[robot_num].hands[a].y - center_y
        # print(f"d_x: {delta_x}, d_y: {delta_y}")
        # print(f"bc[0] x: {self.robots[robot_num].hands[bc[0]].x}")
        # print(f"bc[1] x: {self.robots[robot_num].hands[bc[1]].x}")
        if delta_y > 0 and abs(delta_x) <= eps:
            # min x - c
            # max x - b
            if self.robots[robot_num].hands[bc[0]].x < self.robots[robot_num].hands[bc[1]].x:
                c = bc[0]
                b = bc[1]
            else:
                c = bc[1]
                b = bc[0]
        elif delta_y < 0 and abs(delta_x) <= eps:
            # max x - c
            # min x - b
            if self.robots[robot_num].hands[bc[0]].x < self.robots[robot_num].hands[bc[1]].x:
                b = bc[0]
                c = bc[1]
            else:
                b = bc[1]
                c = bc[0]
        elif delta_x < 0 and abs(delta_y) <= eps:
            # min y - c
            # max y - b
            if self.robots[robot_num].hands[bc[0]].y < self.robots[robot_num].hands[bc[1]].y:
                c = bc[0]
                b = bc[1]
            else:
                c = bc[1]
                b = bc[2]
        elif delta_x > 0 and abs(delta_y) <= eps:
            # max y - c
            # min y - b
            if self.robots[robot_num].hands[bc[0]].y < self.robots[robot_num].hands[bc[1]].y:
                b = bc[0]
                c = bc[1]
            else:
                b = bc[1]
                c = bc[2]
        return a, b, c

    # MUST be in a thread, so it won't block other robots movement
    # рух робота, буде аналіз координат цілі і координат поточних, куди і як рухатись
    def move_robot(self, robot_num, dest_x, dest_y):
        # determine the path to the destination
        # call corresponding functions
        # self.robots[robot_num].isMoving = True
        center_x, center_y = self.robots[robot_num].get_center()
        # print(f"c_x: {center_x}, c_y: {center_y}")

        #  hand a - center hand
        #  hand b - right hand
        #  hand c - left hand
        a, b, c = self.get_hand_letters(robot_num)
        # print(f"a: {a}, b: {b}, c: {c}")

        delta_x = dest_x - center_x
        delta_y = dest_y - center_y
        x_path = abs(delta_x)
        # print(f"x_path: {x_path}")
        # print(f"x(C): {self.robots[robot_num].hands[c].x}")
        y_path = abs(delta_y)
        # check the alignment of the robot and center position, determine move on which axis should be first (x or y)
        if dest_x > center_x:
            # improve
            while x_path > 0.1 and self.robots[robot_num].hands[c].x+3*200 < ceil_to_coordinates(self.max_x):
                self.move_forward(robot_num, a, b, c)
                # new_x = ceil_to_coordinates(self.robots[robot_num].hands[c].x+3*200)
                self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x+3*200, self.robots[robot_num].hands[c].y)
                self.show_ceil()
                center_x, center_y = self.robots[robot_num].get_center()
                a, b, c = self.get_hand_letters(robot_num)
                # print(f"a: {a}, b: {b}, c: {c}")
                delta_x = dest_x - center_x
                delta_y = dest_y - center_y
                x_path = abs(delta_x)
                # print(f"x_path: {x_path}")
                y_path = abs(delta_y)
        if dest_x < center_x:
            while x_path > 0.1 and self.robots[robot_num].hands[b].x - 3 * 200 >= 0:
                self.move_backward(robot_num, a, b, c)
                self.move_hand(robot_num, b, self.robots[robot_num].hands[b].x-3*200, self.robots[robot_num].hands[b].y)
                self.show_ceil()
                center_x, center_y = self.robots[robot_num].get_center()
                a, b, c = self.get_hand_letters(robot_num)
                # print(f"a: {a}, b: {b}, c: {c}")
                # print(f"a: {a}, b: {b}, c: {c}")
                delta_x = dest_x - center_x
                delta_y = dest_y - center_y
                x_path = abs(delta_x)
                # print(f"x_path: {x_path}")
                y_path = abs(delta_y)
        print("move finished")

        # res = self.move_forward(robot_num, 1, 2, 0)
        # if res == -1:
        #     print("oups")
        #     return -1
        # self.move_hand(robot_num, 0, self.robots[robot_num].hands[0].x + 3, self.robots[robot_num].hands[0].y)
        # return 1
