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
        # self.default_coordinates = {"x1": 100,
        #                             "y1": 100,
        #                             "x2": 300,
        #                             "y2": 100,
        #                             "x3": 500,
        #                             "y3": 100}
        #
        # self.default_ceil = {"x1": 0,
        #                      "y1": 0,
        #                      "x2": 1,
        #                      "y2": 0,
        #                      "x3": 2,
        #                      "y3": 0}

        self.default_coordinates = {"x1": 100,
                                    "y1": 300,
                                    "x2": 300,
                                    "y2": 300,
                                    "x3": 500,
                                    "y3": 300}

        self.default_ceil = {"x1": 0,
                             "y1": 0,
                             "x2": 1,
                             "y2": 1,
                             "x3": 2,
                             "y3": 1}

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
        # must check if there's no possible robot movements in this point

        # DON'T FORGET coordinates_to_ceil !!!

        for i in range(len(self.robots)):
            if i == robot_num:
                continue
            else:
                if self.robots[i].is_horizontal_aligned() or self.robots[i].is_vertical_aligned():
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

    def get_real_coordinates(self, robot_num, hand_a, hand_b, hand_c, shifts, angs, aa0):
        # print(f"Shifts {shifts}, Angs: {angs}")
        sa = shifts[hand_a]
        sb = shifts[hand_b]
        sc = shifts[hand_c]

        aa = angs[hand_a] - aa0
        ab = angs[hand_b] - aa0
        ac = angs[hand_c] - aa0

        # координати центру відносно А - це "віддзеркалені" кординати А відносно центру
        o = (-1 * sa * math.sin(aa * math.pi / 180),
             -1 * sa * math.cos(aa * math.pi / 180))
        a = (0, 0)
        b = (sb * math.sin(ab * math.pi / 180) + o[0],
             sb * math.cos(ab * math.pi / 180) + o[1])
        c = (sc * math.sin(ac * math.pi / 180) + o[0],
             sc * math.cos(ac * math.pi / 180) + o[1])

        a_x = float(self.robots[robot_num].hands[hand_a].x)
        a_y = float(self.robots[robot_num].hands[hand_a].y)
        a_real = a[0] + a_x, a[1] + a_y
        b_real = b[0] + a_x, b[1] + a_y
        c_real = c[0] + a_x, c[1] + a_y
        o_real = o[0] + a_x, o[1] + a_y

        coord = [(0, 0), (0, 0), (0, 0), (0, 0)]
        coord[hand_a] = (a_real[0], a_real[1])
        coord[hand_b] = (b_real[0], b_real[1])
        coord[hand_c] = (c_real[0], c_real[1])
        coord[3] = (o_real[0], o_real[1])
        # print(f"Coord: {coord}")

        self.robots[robot_num].set_real_coordinates(coord[0], coord[1], coord[2], coord[3])

    # TODO
    def get_real_coordinates_hand(self, robot_num, hand_a, hand_b, hand_c, angs, aa0):
        # delta = 1e-12  # 47.999999999->48.0 або -0.0000000001->0.0
        delta = 0

        sa = 210.0
        sb = 210.0
        sc = 210.0

        aa = angs[hand_a] - aa0
        ab = angs[hand_b] - aa0
        ac = angs[hand_c] - aa0

        # координати центру відносно А - це "віддзеркалені" кординати А відносно центру
        o = (-1 * sa * math.sin(aa * math.pi / 180),
             -1 * sa * math.cos(aa * math.pi / 180))
        a = (0, 0)
        b = (sb * math.sin(ab * math.pi / 180) + o[0],
             sb * math.cos(ab * math.pi / 180) + o[1])
        c = (sc * math.sin(ac * math.pi / 180) + o[0],
             sc * math.cos(ac * math.pi / 180) + o[1])

        a_x = float(self.robots[robot_num].hands[hand_a].x)
        a_y = float(self.robots[robot_num].hands[hand_a].y)
        a_real = a[0] + a_x, a[1] + a_y
        b_real = b[0] + a_x, b[1] + a_y
        c_real = c[0] + a_x, c[1] + a_y
        o_real = o[0] + a_x, o[1] + a_y

        coord = [(0, 0), (0, 0), (0, 0), (0, 0)]
        coord[hand_a] = (a_real[0], a_real[1])
        coord[hand_b] = (b_real[0], b_real[1])
        coord[hand_c] = (c_real[0], c_real[1])
        coord[3] = (o_real[0], o_real[1])
        # print(f"Coord: {coord}")

        self.robots[robot_num].set_real_coordinates_hand(coord[0], coord[1], coord[2], coord[3])

    # візуалізація лап робота для функцій переміщення
    #    .
    #  / | \
    # C  A  B
    # рух вперед (вправо від центру)
    # def move_forward(self, robot_num, hand_a, hand_b, hand_c):
    #     h = 48
    #     L = size["netStep"]  # 200.0
    #     N = 20  # amount of substeps
    #
    #     # Умовні позначення рук
    #     # А - найкоротша на початку
    #     # В - одна з двох найдовших на початку, не змінює координати
    #     # С - рука, що змінює свої координати (пролітає)
    #     # рука A на мінімальній відстані від вісі = h = 48mm
    #     # руки В і С на відстані sqrt(L^2+h^2) = 205.68mm
    #
    #     # кут, з яким А входить до процедури - це напрям "компасу", загального для усіх
    #     # з початковим кутом А нічого не робимо, його значення - це і є показник компасу
    #     aa0 = self.robots[robot_num].hands[hand_a].ang
    #
    #     for n in range(N + 1):
    #         # отримуємо параметри для рук робота для поточного кроку
    #         shifts, angs, holds = calc_params_forward(L, N, n, h, aa0, hand_a, hand_b, hand_c)
    #
    #         # send these parameters to robot
    #         # send_destination(robot_num, shifts, angs, holds)
    #         # print(
    #         #     f"{robot_num}: [{shifts[0]}, {angs[0]}, {holds[0]}], [{shifts[1]}, {angs[1]}, {holds[1]}], [{shifts[2]}, {angs[2]}, {holds[2]}]")
    #         # wait until the robot will respond
    #         p = pack('@ffiffiffi',
    #                  shifts[0], angs[0], holds[0],
    #                  shifts[1], angs[1], holds[1],
    #                  shifts[2], angs[2], holds[2])
    #         # print(f"PACKAGE: {p}")
    #         self.robots[robot_num].isMoving = True
    #         self.robots[robot_num].out_buffer = p
    #         # print(f"BUFFER: {self.robots[robot_num].out_buffer}")
    #         # print(self.robots[robot_num].socket)
    #         print(f"Shifts {shifts}, Angs: {angs}")
    #         self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, aa0)
    #         self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs)
    #         wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
    #              waiting_for="waiting for robot to finish move")
    #
    #     return 1

    def to_right(self, robot_num, hand_a, hand_b, hand_c):
        N = 20  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0
        LL = 210

        robot_head = self.robots[robot_num].hands[hand_a].ang

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # ідеальна модель з кутом А = 0
        aa0 = 0
        ac0 = 360 - darctan(L / l)
        acN = darctan(L / l)

        # рука С при русі не змінює довжини
        sc0 = math.sqrt(L ** 2 + l ** 2)

        for n in range(N + 1):
            sa = math.sqrt((L / N * n) ** 2 + l ** 2)
            sb = math.sqrt((L - L / N * n) ** 2 + l ** 2)
            sc = sc0

            # зачеп руки С
            if n == 1:
                hc = 0
            elif n == N:
                hc = 1

            # кути рахуються проти годинникової стрілки
            aa = -darctan(L * n / N / l)
            ab = darctan(L * (1 - n / N) / l)
            ac = ac0 + (acN - ac0) * n / N

            aa += robot_head
            ab += robot_head
            ac += robot_head

            shifts = [0.0, 0.0, 0.0]
            shifts[hand_a] = sa
            shifts[hand_b] = sb
            shifts[hand_c] = sc

            angs = [0.0, 0.0, 0.0]
            angs[hand_a] = normalize(aa)
            angs[hand_b] = normalize(ab)
            angs[hand_c] = normalize(ac)

            holds = [0, 0, 0]
            holds[hand_a] = 1
            holds[hand_b] = 1
            holds[hand_c] = hc

            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            # print(f"PACKAGE: {p}")
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            # print(f"BUFFER: {self.robots[robot_num].out_buffer}")
            # print(self.robots[robot_num].socket)
            print(f"Shifts {shifts}, Angs: {angs}")
            self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, robot_head)
            self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def to_left(self, robot_num, hand_a, hand_b, hand_c):
        N = 20  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0
        LL = 210

        robot_head = self.robots[robot_num].hands[hand_a].ang

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # ідеальна модель з кутом А = 0
        sa0 = l
        aa0 = 0

        ab0 = darctan(L / l)
        abN = 360 - darctan(L / l)

        # рука B при русі не змінює довжини
        sb0 = math.sqrt(L ** 2 + l ** 2)

        for n in range(N + 1):
            sa = math.sqrt((L * n / N) ** 2 + l ** 2)
            sb = sb0
            sc = math.sqrt((L * (1 - n / N)) ** 2 + l ** 2)

            # зачеп руки B
            if n == 1:
                hb = 0
            elif n == N:
                hb = 1

            # кути рахуються проти годинникової стрілки
            aa = darctan(L * n / N / l)
            ac = -darctan(L * (1 - n / N) / l)
            ab = ab0 + (abN - ab0) * n / N

            aa += robot_head
            ab += robot_head
            ac += robot_head

            shifts = [0.0, 0.0, 0.0]
            shifts[hand_a] = sa
            shifts[hand_b] = sb
            shifts[hand_c] = sc

            angs = [0.0, 0.0, 0.0]
            angs[hand_a] = normalize(aa)
            angs[hand_b] = normalize(ab)
            angs[hand_c] = normalize(ac)

            holds = [0, 0, 0]
            holds[hand_a] = 1
            holds[hand_b] = 1
            holds[hand_c] = hc

            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            print(f"Shifts {shifts}, Angs: {angs}")
            self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, robot_head)
            self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def hu_to_L1(self, robot_num, hand_a, hand_b, hand_c):
        N = 20  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0
        LL = 210

        robot_head = self.robots[robot_num].hands[hand_a].ang

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # TODO check if the robot is able to make this move

        sa0 = l
        aa0 = 0
        aaN = -45
        sc0 = math.sqrt(l ** 2 + L ** 2)
        scN = math.sqrt(l ** 2 + L ** 2 - L * l * math.sqrt(2))
        ac0 = -darctan(L / l)
        acN = -90 - darctan(L / l * math.sqrt(2) - 1)
        sb0 = sc0
        ab0 = darctan(L / l)

        for n in range(N + 1):
            aa = aaN * n / N  # 0..-45, НЕ через 180 (0..180..315)
            ac = ac0 + (acN - ac0) * n / N
            ab = darctan((L + l * dsin(aa)) / (l * dcos(aa)))

            sa = sa0  # не змінюється впродовж всього маневру
            sb = math.sqrt((L + l * dsin(aa)) ** 2 + (l * dcos(aa)) ** 2)  # sin(315) = sin(-45) = -sin(45)
            sc = sc0 + (scN - sc0) * n / N

            # ЗАЧЕП руки, що пролітає
            if n == 1:
                hc = 0
            elif n == N:
                hc = 1

            aa += robot_head
            ab += robot_head
            ac += robot_head

            shifts = [0.0, 0.0, 0.0]
            shifts[hand_a] = sa
            shifts[hand_b] = sb
            shifts[hand_c] = sc

            angs = [0.0, 0.0, 0.0]
            angs[hand_a] = normalize(aa)
            angs[hand_b] = normalize(ab)
            angs[hand_c] = normalize(ac)

            holds = [0, 0, 0]
            holds[hand_a] = 1
            holds[hand_b] = 1
            holds[hand_c] = hc

            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            print(f"Shifts {shifts}, Angs: {angs}")
            self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, robot_head)
            self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def L1_to_Vr(self, robot_num, hand_a, hand_b, hand_c):  # перехід з L у вертикальне за часовою стрілкою
        N = 20  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0
        LL = 210

        robot_head = self.robots[robot_num].hands[hand_a].ang - 315

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # Друга половина маневру - A і C у зачепах, B пролітає з лівого у вертикальне положення, центр зміщується на 45 градусів вправо-вниз від A
        sa0 = l
        aa0 = -45  # початковий кут лапи A = -45
        aaN = -90  # кінцевий кут лапи A = -90

        sb0 = math.sqrt(l ** 2 + L ** 2 - L * l * math.sqrt(2))  # початкова довжина руки B
        sbN = math.sqrt(l ** 2 + L ** 2)  # кінцева довжина руки B

        ab0 = darctan(L / l * math.sqrt(2) - 1)
        abN = -90 + darctan(L / l)  # БЕЗ normalize! інакше піде не через 0, а через 180

        sc0 = sb0  #
        scN = sbN  # під час руху її довжина змінюється пропорційно n/N

        for n in range(N + 1):
            if n == 1:
                hb = 0
            elif n == N:
                hb = 1

            # кути рахуються ПРОТИ годинникової стрілки
            aa = aa0 + (aaN - aa0) * n / N  # лапа А рівномірно повертається
            ab = ab0 + (abN - ab0) * n / N  # лапа В рівномірно пролітає

            sa = sa0  # не змінюється впродовж всього маневру
            sb = sb0 + (sbN - sb0) * n / N
            sc = math.sqrt(L ** 2 + l ** 2 - 2 * l * L * dcos(
                aa))  # тут враховується кут А ідеальної моделі (А від 315 до 270), тому початкове зміщення робимо далі
            ac = -90 + darctan((L - l * dcos(aa)) / (l * dsin(
                aa)))  # тут враховується кут А ідеальної моделі (А від 315 до 270), тому початкове зміщення робимо далі

            aa += robot_head
            ab += robot_head
            ac += robot_head

            shifts = [0.0, 0.0, 0.0]
            shifts[hand_a] = sa
            shifts[hand_b] = sb
            shifts[hand_c] = sc

            angs = [0.0, 0.0, 0.0]
            angs[hand_a] = normalize(aa)
            angs[hand_b] = normalize(ab)
            angs[hand_c] = normalize(ac)

            holds = [0, 0, 0]
            holds[hand_a] = 1
            holds[hand_b] = 1
            holds[hand_c] = hc

            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            # print(f"PACKAGE: {p}")
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            # print(f"BUFFER: {self.robots[robot_num].out_buffer}")
            # print(self.robots[robot_num].socket)
            print(f"Shifts {shifts}, Angs: {angs}")
            self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, robot_head)
            self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    # def move_backward(self, robot_num, hand_a, hand_b, hand_c):
    #     # A середня, C передня, B задня вилітаюча
    #     h = 48
    #     L = size["netStep"]  # 200
    #     N = 20  # amount of substeps
    #
    #     # Умовні позначення рук
    #     # А - найкоротша на початку
    #     # C - одна з двох найдовших на початку, не змінює координати
    #     # B - рука, що змінює свої координати (пролітає)
    #     # рука A на мінімальній відстані від вісі = h = 48mm
    #     # руки В і С на відстані sqrt(L^2+h^2) = 205.68mm
    #
    #     # кут, з яким А входить до процедури - це напрям "компасу", загального для усіх
    #     # з початковим кутом А нічого не робимо, його значення - це і є показник компасу
    #     aa0 = self.robots[robot_num].hands[hand_a].ang
    #
    #     for n in range(N + 1):
    #         # отримуємо параметри для рук робота для поточного кроку
    #         shifts, angs, holds = calc_params_backward(L, N, n, h, aa0, hand_a, hand_b, hand_c)
    #
    #         p = pack('@ffiffiffi',
    #                  shifts[0], angs[0], holds[0],
    #                  shifts[1], angs[1], holds[1],
    #                  shifts[2], angs[2], holds[2])
    #         # print(f"PACKAGE: {p}")
    #         self.robots[robot_num].isMoving = True
    #         self.robots[robot_num].out_buffer = p
    #         # print(f"BUFFER: {self.robots[robot_num].out_buffer}")
    #         # print(self.robots[robot_num].socket)
    #         self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, aa0)
    #         self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs)
    #         wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
    #              waiting_for="waiting for robot to finish move")
    #
    #     return 1

    # перевірка наявності робота в масиві за IP
    def match_IPs(self, ip):
        robot_i = -1
        for i in range(len(self.robots)):
            if self.robots[i].get_ip() == ip:
                robot_i = i
        return robot_i

    # additional for get L hand letters
    def hand_in_point(self, x, y, x1, x2, y1, y2):
        if (x == x1) and (y == y1):
            return 1
        if (x == x2) and (y == y1):
            return 2
        if (x == x2) and (y == y2):
            return 3
        if (x == x1) and (y == y2):
            return 4
        return -1

    # TODO test
    def get_L_hand_letters(self, robot_num):
        # 1  2
        # 4  3
        a, b, c = -1, -1, -1
        x1 = min(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[1].x,
                 self.robots[robot_num].hands[2].x)
        x2 = max(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[1].x,
                 self.robots[robot_num].hands[2].x)
        y1 = min(self.robots[robot_num].hands[0].y, self.robots[robot_num].hands[1].y,
                 self.robots[robot_num].hands[2].y)
        y2 = max(self.robots[robot_num].hands[0].y, self.robots[robot_num].hands[1].y,
                 self.robots[robot_num].hands[2].y)

        points = [self.hand_in_point(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y,
                                     x1, x2, y1, y2),
                  self.hand_in_point(self.robots[robot_num].hands[1].x, self.robots[robot_num].hands[1].y,
                                     x1, x2, y1, y2),
                  self.hand_in_point(self.robots[robot_num].hands[2].x, self.robots[robot_num].hands[2].y,
                                     x1, x2, y1, y2)]

        if (1 in points) and (3 in points) and (4 in points):
            a = points.index(4)
            b = points.index(3)
            c = points.index(1)

        return a, b, c

    def get_hand_letters(self, robot_num):
        #  hand a - center hand
        #  hand b - right hand
        #  hand c - left hand
        if not (self.robots[robot_num].is_horizontal_aligned() or self.robots[robot_num].is_vertical_aligned()):
            # call another function
            return self.get_L_hand_letters(robot_num)
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
        y_path = abs(delta_y)
        # print(f"x_path: {x_path}")
        # print(f"x(C): {self.robots[robot_num].hands[c].x}")
        # check the alignment of the robot and center position, determine move on which axis should be first (x or y)
        if dest_x > center_x:
            # improve
            while x_path > 0.1 and self.robots[robot_num].hands[c].x + 3 * 200 < ceil_to_coordinates(self.max_x):
                # self.move_forward(robot_num, a, b, c)
                self.to_right(robot_num, a, b, c)
                # new_x = ceil_to_coordinates(self.robots[robot_num].hands[c].x+3*200)
                self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x + 3 * 200,
                               self.robots[robot_num].hands[c].y)
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
                self.to_left(robot_num, a, b, c)
                self.move_hand(robot_num, b, self.robots[robot_num].hands[b].x - 3 * 200,
                               self.robots[robot_num].hands[b].y)
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

    def start_move(self, robot_num, dest_x, dest_y):
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
        y_path = abs(delta_y)

        while x_path > 100 or y_path > 100:
            if x_path > 100:
                # turn if vertical
                # move
                pass
            if y_path > 100:
                if self.robots[robot_num].is_horizontal_aligned():
                    self.turn_robot(robot_num)
                # move
                pass

        # TEMPORARY FUNCTION

    def turn_robot(self, robot_num):
        center_x, center_y = self.robots[robot_num].get_center()
        # print(f"c_x: {center_x}, c_y: {center_y}")

        #  hand a - center hand
        #  hand b - right hand
        #  hand c - left hand
        a, b, c = self.get_hand_letters(robot_num)

        self.hu_to_L1(robot_num, a, b, c)
        self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x + 1 * 200,
                       self.robots[robot_num].hands[c].y - 1 * 200)
        self.show_ceil()
        center_x, center_y = self.robots[robot_num].get_center()
        a, b, c = self.get_hand_letters(robot_num)
        self.L1_to_Vr(robot_num, a, b, c)

        # res = self.move_forward(robot_num, 1, 2, 0)
        # if res == -1:
        #     print("oups")
        #     return -1
        # self.move_hand(robot_num, 0, self.robots[robot_num].hands[0].x + 3, self.robots[robot_num].hands[0].y)
        # return 1
