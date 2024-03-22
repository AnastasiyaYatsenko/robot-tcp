import select
import time
from struct import pack
from waiting import wait

from arm_geometry_test import *
from robot import *

# клас з функціями роботи з роботами
class Ceil:

    def __init__(self):
        self.max_x = 10
        self.max_y = 10
        # масив лунок
        self.ceil_arr = [[0 for i in range(self.max_x)] for j in range(self.max_y)]

        # дефолтні координати для роботів
        self.default_coordinates = {"x1": 0,
                                    "y1": 0,
                                    "x2": 1,
                                    "y2": 0,
                                    "x3": 2,
                                    "y3": 0}

        # масив роботів
        self.robots = []

    # додавання роботу
    def add_robot(self, ip):
        r = Robot()
        r.set_ip(ip)
        r.set_coordinates(self.default_coordinates["x1"], self.default_coordinates["y1"],
                          self.default_coordinates["x2"], self.default_coordinates["y2"],
                          self.default_coordinates["x3"], self.default_coordinates["y3"])

        # set start coordinates, paarameters will be handled with data reading
        self.robots.append(r)

    # перевірка, чи можна в точку (х,у) поставити лапу
    def is_point_free(self, x, y, robot_num):
        # for i in range(robots_num):
        #     c_x, c_y = robots[i].get_center()
        #     if (x - c_x)**2 + (y - c_y)**2 <= robot_hand_len**2:
        #         return False

        # must check if there's no possible robot movements in this point
        for i in range(len(self.robots)):
            if i == robot_num:
                continue
            else:
                if (self.robots[i].hands[0].x == self.robots[i].hands[1].x and self.robots[i].hands[1].x == self.robots[i].hands[2].x) \
                        or (
                        self.robots[i].hands[0].y == self.robots[i].hands[1].y and self.robots[i].hands[1].y == self.robots[i].hands[2].y):
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
        if self.ceil_arr[y][x] == 0:
            old_x = self.robots[robot_num].hands[hand_num].x
            old_y = self.robots[robot_num].hands[hand_num].y
            self.ceil_arr[old_y][old_x] = 0

            self.ceil_arr[y][x] = 1
            self.robots[robot_num].set_hand_coordinates(hand_num, x, y)

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
            print(
                f"{robot_num}: [{shifts[0]}, {angs[0]}, {holds[0]}], [{shifts[1]}, {angs[1]}, {holds[1]}], [{shifts[2]}, {angs[2]}, {holds[2]}]")
            # wait until the robot will respond
            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            # print(f"PACKAGE: {p}")
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            print(f"BUFFER: {self.robots[robot_num].out_buffer}")
            # print(self.robots[robot_num].socket)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1
        # update coordinates

    # перевірка наявності робота в масиві за IP
    def match_IPs(self, ip):
        robot_i = -1
        for i in range(len(self.robots)):
            if self.robots[i].get_ip() == ip:
                robot_i = i
        return robot_i

    # MUST be in a thread, so it won't block other robots movement
    # рух робота, буде аналіз координат цілі і координат поточних, куди і як рухатись
    def move_robot(self, robot_num, dest_x, dest_y):
        # determine the path to the destination
        # call corresponding functions
        # self.robots[robot_num].isMoving = True
        res = self.move_forward(robot_num, 1, 2, 0)
        if res == -1:
            print("oups")
            return -1
        self.move_hand(robot_num, 0, self.robots[robot_num].hands[0].x+3, self.robots[robot_num].hands[0].y)
        return 1
