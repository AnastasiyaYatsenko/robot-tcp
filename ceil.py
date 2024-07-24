import math
import select
import sys
import time
from struct import pack
from waiting import wait

import arm_geometry_test
from arm_geometry_test import *
from robot import *


# клас з функціями роботи з роботами
class Ceil:

    def __init__(self):
        self.max_x = 10
        self.max_y = 10
        # масив лунок
        self.ceil_arr = [[0 for i in range(self.max_x)] for j in range(self.max_y)]
        #self.N = 2
        self.N = 2

        # дефолтні координати для роботів
        self.default_coordinates = {"x1": 300,
                                    "y1": 300,
                                    "x2": 500,
                                    "y2": 300,
                                    "x3": 100,
                                    "y3": 300}

        # self.default_ceil = {"x1": 1,
        #                      "y1": 1,
        #                      "x2": 0,
        #                      "y2": 1,
        #                      "x3": 2,
        #                      "y3": 1}

        # self.default_coordinates = {"x1": 100,
        #                             "y1": 300,
        #                             "x2": 300,
        #                             "y2": 300,
        #                             "x3": 500,
        #                             "y3": 300}
        #
        # self.default_ceil = {"x1": 0,
        #                      "y1": 1,
        #                      "x2": 1,
        #                      "y2": 1,
        #                      "x3": 2,
        #                      "y3": 1}

        # self.default_coordinates = {"x3": 500,
        #                             "y3": 300,
        #                             "x1": 300,
        #                             "y1": 300,
        #                             "x2": 100,
        #                             "y2": 300}
        #
        # self.default_ceil = {"x3": 2,
        #                      "y3": 1,
        #                      "x1": 1,
        #                      "y1": 1,
        #                      "x2": 0,
        #                      "y2": 1}

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

        y1 =  int((self.default_coordinates["y1"] - 100) / 200)
        x1 = int((self.default_coordinates["x1"] - 100) / 200)
        y2 = int((self.default_coordinates["y2"] - 100) / 200)
        x2 = int((self.default_coordinates["x2"] - 100) / 200)
        y3 = int((self.default_coordinates["y3"] - 100) / 200)
        x3 = int((self.default_coordinates["x3"] - 100) / 200)

        self.ceil_arr[y1][x1] = 1
        self.ceil_arr[y2][x2] = 1
        self.ceil_arr[y3][x3] = 1

        # set start coordinates, parameters will be handled with data reading
        self.robots.append(r)

    # TODO check and debug
    # перевірка, чи можна в точку (х,у) поставити лапу
    def is_point_free(self, x, y, robot_num):
        # must check if there's no possible robot movements in this point
        x_ceil = ceil_to_coordinates(x)
        y_ceil = ceil_to_coordinates(y)

        for i in range(len(self.robots)):
            if i == robot_num:
                continue
            else:
                x_robot, y_robot = self.robots[i].get_center()
                is_in_circle = False
                if (x_ceil - x_robot) ** 2 + (-y_ceil + y_robot) ** 2 <= size["outerRadLimit"] ** 2:
                    is_in_circle = True
                if is_in_circle:
                    return False
        return True
                # if self.robots[i].is_horizontal_aligned() or self.robots[i].is_vertical_aligned():
                #     pass
                # else:
                #     pass
        # if self.ceil_arr[y][x] == 0:
        #     return True
        # else:
        #     return False

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

    def set_hand_coordinates(self, robot_num, x1, y1, x2, y2, x3, y3):
        print("IN SET COORDS")
        self.robots[robot_num].set_coordinates(x1, y1, x2, y2, x3, y3)
        self.move_hand(robot_num, 0, x1, y1)
        self.move_hand(robot_num, 1, x2, y2)
        self.move_hand(robot_num, 2, x3, y3)
        # a, b, c = self.get_hand_letters(robot_num)
        # print(f"a: {a} b: {b} c: {c}")
        shifts = [self.robots[robot_num].hands[0].lin,
                  self.robots[robot_num].hands[1].lin,
                  self.robots[robot_num].hands[2].lin]
        angles = [self.robots[robot_num].hands[0].ang,
                  self.robots[robot_num].hands[1].ang,
                  self.robots[robot_num].hands[2].ang]
        base = 0
        if self.robots[robot_num].is_vertical_aligned():
            base = 270

        center_x, center_y = self.robots[robot_num].get_center()
        print(f"IN SET COORDS center: {center_x} {center_y}")
        # new_a, new_b, new_c, new_ang_a, new_ang_b, new_ang_c, robot_head_ = self.get_new_params_by_vector(robot_num,
        #                                                                                                  center_x, center_x,
        #                                                                                                  center_x, center_x,
        #                                                                                                  a, b, c)

        robot_head = self.get_robot_angle_shift(robot_num)
        print(f"SETCOORDS ROBOT HEAD: {robot_head}")
        # print(f"SETCOORDS ROBOT HEAD 2: {robot_head_}")

        #self.get_real_coordinates(robot_num, a, b, c, shifts, angles, self.robots[robot_num].hands[a].ang - base)
        self.get_real_coordinates(robot_num, 0, 1, 2, shifts, angles, robot_head)

    def get_robot_angle_shift(self, robot_num):
        ang_a = self.robots[robot_num].hands[0].ang

        center_x, center_y = self.robots[robot_num].get_center()

        print(f"START ANGLES a: {ang_a}")

        xa, ya = get_vector_coords(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y,
                                   center_x, center_y)

        print(f"GET VECTOR COORDS a: ({xa}, {ya})")

        a = get_abs_vector(xa, ya)

        print(f"GET VECTOR ABS a: {a}")

        # base vector is vertical vector from which the angles and offset will be counted
        base_vector_x = 0
        base_vector_y = 5

        base_to_a = angle_between_vectors(base_vector_x, base_vector_y, xa, ya)
        shift = normalize(ang_a - base_to_a)

        return shift

    def get_real_coordinates(self, robot_num, hand_a, hand_b, hand_c, shifts, angs, aa0):
        # print(f"GRC: Shifts {shifts}, Angs: {angs}, AA0: {aa0}")

        sa = shifts[hand_a]
        sb = shifts[hand_b]
        sc = shifts[hand_c]

        aa = normalize(angs[hand_a] - aa0)
        ab = normalize(angs[hand_b] - aa0)
        ac = normalize(angs[hand_c] - aa0)

        o = (0, 0)
        a = (sa * dsin(aa), sa * dcos(aa))
        b = (sb * dsin(ab), sb * dcos(ab))
        c = (sc * dsin(ac), sc * dcos(ac))

        base = a
        base_i = hand_a
        if self.robots[robot_num].hands[hand_a].hold == 0:
            base = b
            base_i = hand_b

        sa = sb = sc = size["outerRadLimit"]

        # ЛАПИ
        # Обчислюємо все відносно O
        o_ = (0, 0)
        a_ = (sa * dsin(aa),
              sa * dcos(aa))  # координаты центра относительно А - это "отзеркаленные" кординаты А относительно центра
        b_ = (sb * dsin(ab), sb * dcos(ab))
        c_ = (sc * dsin(ac), sc * dcos(ac))

        # и смещаем зацеп A в начало координат, из координаты конца ЛИНИИ вычитаем координату ЗАЦЕПА!!
        o_ = (o_[0] - base[0], o_[1] - base[1])
        b_ = (b_[0] - base[0], b_[1] - base[1])
        c_ = (c_[0] - base[0], c_[1] - base[1])
        a_ = (a_[0] - base[0], a_[1] - base[1])

        # и смещаем зацеп A в начало координат
        o = (o[0] - base[0], o[1] - base[1])
        a = (a[0] - base[0], a[1] - base[1])
        b = (b[0] - base[0], b[1] - base[1])
        c = (c[0] - base[0], c[1] - base[1])
        # print(f"GRC: A1: {a}, B1: {b}, C1: {c}, O1: {o}")

        base_x = float(self.robots[robot_num].hands[base_i].x)
        base_y = float(self.robots[robot_num].hands[base_i].y)
        a_real = a[0] + base_x, a[1] + base_y
        b_real = b[0] + base_x, b[1] + base_y
        c_real = c[0] + base_x, c[1] + base_y
        o_real = o[0] + base_x, o[1] + base_y
        # print(f"GRC: A2: {a_real}, B2: {b_real}, C2: {c_real}, O2: {o_real}")

        a_real_ = a_[0] + base_x, a_[1] + base_y
        b_real_ = b_[0] + base_x, b_[1] + base_y
        c_real_ = c_[0] + base_x, c_[1] + base_y
        o_real_ = o_[0] + base_x, o_[1] + base_y

        coord = [(0, 0), (0, 0), (0, 0), (0, 0)]
        coord[hand_a] = (a_real[0], a_real[1])
        coord[hand_b] = (b_real[0], b_real[1])
        coord[hand_c] = (c_real[0], c_real[1])
        coord[3] = (o_real[0], o_real[1])

        coord_ = [(0, 0), (0, 0), (0, 0), (0, 0)]
        coord_[hand_a] = (a_real_[0], a_real_[1])
        coord_[hand_b] = (b_real_[0], b_real_[1])
        coord_[hand_c] = (c_real_[0], c_real_[1])
        coord_[3] = (o_real_[0], o_real_[1])
        center_x, center_y = self.robots[robot_num].get_center()
        # print(f"IN COORD SCENTER x: ({center_x}, {center_y})")
        # print(f"Coord: {coord}")

        self.robots[robot_num].set_real_coordinates(coord[0], coord[1], coord[2], coord[3])
        self.robots[robot_num].set_real_coordinates_hand(coord_[0], coord_[1], coord_[2], coord_[3])

    # візуалізація лап робота для функцій переміщення
    #    .
    #  / | \
    # C  A  B

    def get_new_params_by_vector(self, robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords, move_hand = -1):
        # TODO get params from robot
        ang_0 = self.robots[robot_num].hands[0].ang
        print(f"Angle A: {ang_0}")
        # x0, y0 = get_vector_coords(hand_coords[0][0], hand_coords[0][1],
        #                            xo_s, yo_s)
        x0, y0 = get_vector_coords(xo_s, yo_s,
                                   hand_coords[0][0], hand_coords[0][1])

        if move_hand == 0:
            ang_0 = self.robots[robot_num].hands[1].ang
            x0, y0 = get_vector_coords(xo_s, yo_s,
                                       hand_coords[1][0], hand_coords[1][1])
            # x0, y0 = get_vector_coords(hand_coords[1][0], hand_coords[1][1],
            #                            xo_s, yo_s)

        a = get_abs_vector(x0, y0)

        print(f"GET VECTOR ABS a: {a}, x0: {x0}, y0: {y0}")

        # base vector is vertical vector from which the angles and offset will be counted
        base_vector_x = 0
        base_vector_y = -5

        base_to_0 = angle_between_vectors(base_vector_x, base_vector_y, x0, y0)
        shift = normalize(ang_0 - base_to_0)
        # shift = 4
        print(f"BASE TO A: {base_to_0} SHIFT: {shift}")

        #x_head, y_head = get_head_vector(a, ang_a, b, ang_b, xa, ya, xb, yb)
        # print(f"GET HEAD head: ({x_head}, {y_head})")

        # new_x0, new_y0 = get_vector_coords(hand_coords[0][0], hand_coords[0][1],
        #                                    xo_t, yo_t)
        # new_x1, new_y1 = get_vector_coords(hand_coords[1][0], hand_coords[1][1],
        #                                    xo_t, yo_t)
        # new_x2, new_y2 = get_vector_coords(hand_coords[2][0], hand_coords[2][1],
        #                                    xo_t, yo_t)

        new_x0, new_y0 = get_vector_coords(xo_t, yo_t,
                                   hand_coords[0][0], hand_coords[0][1])
        new_x1, new_y1 = get_vector_coords(xo_t, yo_t,
                                   hand_coords[1][0], hand_coords[1][1])
        new_x2, new_y2 = get_vector_coords(xo_t, yo_t,
                                   hand_coords[2][0], hand_coords[2][1])

        print(f"GET NEW VECTOR COORDS a: ({new_x0}, {new_y0}) b: ({new_x1}, {new_y1}) c: ({new_x2}, {new_y2})")

        new_0 = get_abs_vector(new_x0, new_y0)
        new_1 = get_abs_vector(new_x1, new_y1)
        new_2 = get_abs_vector(new_x2, new_y2)

        print(f"GET NEW VECTOR ABS a: {new_0} b: {new_1} c: {new_2}")

        '''new_ang_a = angle_between_vectors(x_head, y_head, new_xa, new_ya)
        new_ang_b = angle_between_vectors(x_head, y_head, new_xb, new_yb)
        new_ang_c = angle_between_vectors(x_head, y_head, new_xc, new_yc)'''

        new_ang_0 = angle_between_vectors(base_vector_x, base_vector_y, new_x0, new_y0)
        new_ang_1 = angle_between_vectors(base_vector_x, base_vector_y, new_x1, new_y1)
        new_ang_2 = angle_between_vectors(base_vector_x, base_vector_y, new_x2, new_y2)

        print(f"ANGS BEFORE SHIFT a: {new_ang_0} b: {new_ang_1} c: {new_ang_2}")

        new_ang_0 = normalize(new_ang_0 + shift)
        new_ang_1 = normalize(new_ang_1 + shift)
        new_ang_2 = normalize(new_ang_2 + shift)

        print(f"GET ANGS a: {new_ang_0} b: {new_ang_1} c: {new_ang_2}")

        return new_0, new_1, new_2, new_ang_0, new_ang_1, new_ang_2, shift

    # check if hand shifts will be of possible lengths throughout the move
    def is_move_possible_two_holds(self, robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords, hand_c):
        print(f"Is possible two holds; hand: {hand_c}, coords: {hand_coords}, Os: ({xo_s}, {yo_s}), On: ({xo_t}, {yo_t})")
        N = 10
        hands = [0, 1, 2]
        hands.remove(hand_c)
        for n in range(N + 1):
            xo_n = xo_s
            yo_n = yo_s
            if 0 < n < N:
                l = n / (N - n)
                xo_n = (xo_s + l * xo_t) / (1 + l)
                yo_n = (yo_s + l * yo_t) / (1 + l)
            elif n == N:
                xo_n = xo_t
                yo_n = yo_t
            # print("---------")
            # print(f"s X: {xo_s} Y: {yo_s}")
            # print(f"n X: {xo_n} Y: {yo_n}")
            # print(f"t X: {xo_t} Y: {yo_t}")
            # print("---------")
            in_reach_zone = is_in_two_hands_area(hand_coords[hands[0]][0], hand_coords[hands[0]][1],
                                                 hand_coords[hands[1]][0], hand_coords[hands[1]][1],
                                                 xo_n, yo_n)
            if not in_reach_zone:
                # print("NOT IN REACH ZONE")
                return False
            # print("IN REACH ZONE")
        return True

    def is_move_possible_three_holds(self, robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords):
        print("is possible two holds")
        N = 10
        for n in range(N + 1):
            xo_n = xo_s
            yo_n = yo_s
            if 0 < n < N:
                l = n / (N - n)
                xo_n = (xo_s + l * xo_t) / (1 + l)
                yo_n = (yo_s + l * yo_t) / (1 + l)
            elif n == N:
                xo_n = xo_t
                yo_n = yo_t
            # print("---------")
            # print(f"s X: {xo_s} Y: {yo_s}")
            # print(f"n X: {xo_n} Y: {yo_n}")
            # print(f"t X: {xo_t} Y: {yo_t}")
            # print("---------")
            in_reach_zone = is_in_three_hands_area(hand_coords[0][0], hand_coords[0][1],
                                                   hand_coords[1][0], hand_coords[1][1],
                                                   hand_coords[2][0], hand_coords[2][1],
                                                   xo_n, yo_n)
            if not in_reach_zone:
                # print("NOT IN REACH ZONE")
                return False
            # print("IN REACH ZONE")
        return True

    def check_coord_change(self, robot_num, hand_num, x, y):
        if self.robots[robot_num].hands[hand_num].x != x or self.robots[robot_num].hands[hand_num].y != y:
            return True
        return False

    def check_conditions_pos(self, robot_num, center_x, center_y, xo_s, yo_s, hand_coords, hand_c = -1):
        # if we've got -1, -1, it means these shifts are impossible
        if center_x != -1 and center_y != -1:
            # print("------")
            # print(f"IN FIND SHIFTS: ({center_x}, {center_y})")
            # checking new center point for min angle
            is_possible = is_in_three_hands_area(hand_coords[0][0], hand_coords[0][1],
                                                 hand_coords[1][0], hand_coords[1][1],
                                                 hand_coords[2][0], hand_coords[2][1], center_x, center_y)
            new_0, new_1, new_2, ang_0, ang_1, ang_2, rh = self.get_new_params_by_vector(robot_num,
                                                                                         xo_s, yo_s,
                                                                                         center_x, center_y,
                                                                                         hand_coords)
            is_correct_hand_order = mirroring_check(ang_0, ang_1, ang_2)
            is_move_possible = True

            if hand_c != -1:
                is_move_possible = self.is_move_possible_two_holds(robot_num, xo_s, yo_s,
                                                                   center_x, center_y,
                                                                   hand_coords, hand_c)
            else:
                is_move_possible = self.is_move_possible_three_holds(robot_num, xo_s, yo_s,
                                                                     center_x, center_y,
                                                                     hand_coords)
            print(f"Coords: {hand_coords}; Conditions are: pose: {is_possible}, move: {is_move_possible}, mirroring: {is_correct_hand_order}")
            if not is_possible or not is_move_possible or not is_correct_hand_order:
                return False
            return True
        return False

    # finds the center for the robot; TODO change brute force search to smth more effective
    def find_pos_by_shifts(self, robot_num, xo_s, yo_s, hand_coords, start_shifts, hand_c = -1):
        print(f"Find pos by shifts for {hand_coords}; start shifts: {start_shifts}")
        best_shifts = [-1, -1, -1]
        best_center = -1, -1

        # min1, max1 = size["innerRadLimit"], size["outerRadLimit"] + 1
        # min2, max2 = size["innerRadLimit"], size["outerRadLimit"] + 1
        # min3, max3 = size["innerRadLimit"], size["outerRadLimit"] + 1

        min1, max1 = (int(max(start_shifts[0] - size["innerRadLimit"], size["innerRadLimit"])),
                      int(min(start_shifts[0] + size["innerRadLimit"] + 1, size["outerRadLimit"] + 1)))
        min2, max2 = (int(max(start_shifts[1] - size["innerRadLimit"], size["innerRadLimit"])),
                      int(min(start_shifts[1] + size["innerRadLimit"] + 1, size["outerRadLimit"] + 1)))
        min3, max3 = (int(max(start_shifts[2] - size["innerRadLimit"], size["innerRadLimit"])),
                      int(min(start_shifts[2] + size["innerRadLimit"] + 1, size["outerRadLimit"] + 1)))

        # brute force through all possible options
        for shift_1 in range(min1, max1):
            for shift_2 in range(min2, max2):
                for shift_3 in range(min3, max3):
                    # trying to find a center
                    # print(f"{shift_1} - {shift_2} - {shift_3}")
                    center_x, center_y = center_by_params(hand_coords, shift_1, shift_2, shift_3)
                    pos_conditions = self.check_conditions_pos(robot_num, center_x, center_y,
                                                               xo_s, yo_s, hand_coords, hand_c)
                    if not pos_conditions:
                        continue
                    if best_shifts[0] == -1:
                        # first option that we've found
                        best_shifts[0] = shift_1
                        best_shifts[1] = shift_2
                        best_shifts[2] = shift_3
                        best_center = (center_x, center_y)
                    else:
                        # checking if current shifts are better than previous
                        # (if they are closer to the start shifts)
                        deltas_saved = [abs(best_shifts[0]-start_shifts[0]),
                                        abs(best_shifts[1]-start_shifts[1]),
                                        abs(best_shifts[2]-start_shifts[2])]
                        deltas_new = [abs(shift_1 - start_shifts[0]),
                                      abs(shift_2 - start_shifts[1]),
                                      abs(shift_3 - start_shifts[2])]
                        if sum(deltas_new) < sum(deltas_saved):
                            best_shifts[0] = shift_1
                            best_shifts[1] = shift_2
                            best_shifts[2] = shift_3
                            best_center = (center_x, center_y)
                        elif sum(deltas_new) == sum(deltas_saved):
                            diff = [int(deltas_new[0] < deltas_saved[0]),
                                    int(deltas_new[1] < deltas_saved[1]),
                                    int(deltas_new[2] < deltas_saved[2])]
                            if sum(diff) >= 2:
                                best_shifts[0] = shift_1
                                best_shifts[1] = shift_2
                                best_shifts[2] = shift_3
                                best_center = (center_x, center_y)
        if best_center[0] == -1:
            print("Can't find proper position for these coordinates")
            return -1, -1

        return best_center

    # finds the suitable shifts for the robot; TODO change brute force search to smth more effective
    def find_pos_by_hand_coords(self, robot_num, xo_s, yo_s, hand_coords, hand_c=-1):
        best_shifts = [-1, -1, -1]
        best_center = -1, -1
        # brute force through all possible options
        min_shift = int(size["innerRadLimit"] + (size["outerRadLimit"] - size["innerRadLimit"]) / 3)
        max_shift = int(size["outerRadLimit"] - (size["outerRadLimit"] - size["innerRadLimit"]) / 3)
        # min_shift = size["innerRadLimit"]
        # max_shift = size["outerRadLimit"]
        for shift_1 in range(min_shift, max_shift + 1):
            for shift_2 in range(min_shift, max_shift + 1):
                for shift_3 in range(min_shift, max_shift + 1):
                    # trying to find a center
                    print(f"Searching pos, {shift_1}; {shift_2}; {shift_3}")
                    center_x, center_y = center_by_params(hand_coords, shift_1, shift_2, shift_3)
                    pos_conditions = self.check_conditions_pos(robot_num, center_x, center_y,
                                                               xo_s, yo_s, hand_coords, hand_c)
                    if not pos_conditions:
                        continue
                    if best_shifts[0] == -1:
                        # first option that we've found
                        best_shifts[0] = shift_1
                        best_shifts[1] = shift_2
                        best_shifts[2] = shift_3
                        best_center = (center_x, center_y)

        if best_center[0] == -1:
            print("Can't find proper position for these coordinates")
            return -1, -1

        return best_center


    # when move is impossible because of min/max shift or min angle, we need to find suitable coordinate
    # for the robot to move to
    def find_new_position_three_holds(self, robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords, hand_c = -1):
        shift_0 = dist(hand_coords[0][0], hand_coords[0][1],
                       xo_t, yo_t)
        shift_1 = dist(hand_coords[1][0], hand_coords[1][1],
                       xo_t, yo_t)
        shift_2 = dist(hand_coords[2][0], hand_coords[2][1],
                       xo_t, yo_t)
        shifts = [shift_0, shift_1, shift_2]
        max_shifts = [int(shift_0 > size["outerRadLimit"]),
                      int(shift_1 > size["outerRadLimit"]),
                      int(shift_2 > size["outerRadLimit"])]
        min_shifts = [int(shift_0 < size["innerRadLimit"]),
                      int(shift_1 < size["innerRadLimit"]),
                      int(shift_2 < size["innerRadLimit"])]
        for i in range(3):
            if max_shifts[i]:
                shifts[i] = size["outerRadLimit"]
            if min_shifts[i]:
                shifts[i] = size["innerRadLimit"]

        new_xo_t, new_yo_t = -1, -1
        center_x, center_y = center_by_params(hand_coords, shifts[0], shifts[1], shifts[2])
        # if is_aligned(hand_coords):
        #     new_xo_t, new_yo_t = calculate_center(hand_coords[0][0], hand_coords[0][1],
        #                                           hand_coords[1][0], hand_coords[1][1],
        #                                           hand_coords[2][0], hand_coords[2][1],
        #                                           shifts[0], shifts[1], shifts[2])
        # else:
        #     new_xo_t, new_yo_t = calculate_center_three_points(hand_coords[0][0], hand_coords[0][1],
        #                                                        hand_coords[1][0], hand_coords[1][1],
        #                                                        hand_coords[2][0], hand_coords[2][1],
        #                                                        shifts[0], shifts[1], shifts[2])

        pos_conditions = self.check_conditions_pos(robot_num, new_xo_t, new_yo_t,
                                                   xo_s, yo_s, hand_coords, hand_c)
        if not pos_conditions:
            new_xo_t, new_yo_t = self.find_pos_by_shifts(robot_num, xo_s, yo_s,
                                                 hand_coords, shifts, hand_c)
            if new_xo_t == -1 or new_yo_t == -1:
                print("Can't find proper position for these coordinates")
                return -1, -1

        return new_xo_t, new_yo_t

    def check_clockwise(self, robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords, old_shift, old_ang, delta_shift, new_ang, move_hand):
        print(f"IN FUNC N = {self.N}; move_hand is {move_hand}; old_shift: {old_shift}, old_ang: {old_ang};"
              f"delta_shift: {delta_shift}, new_ang: {new_ang}")
        for n in range(self.N + 1):
            xo_n = xo_s
            yo_n = yo_s
            if 0 < n < self.N:
                l = n / (self.N - n)
                xo_n = (xo_s + l * xo_t) / (1 + l)
                yo_n = (yo_s + l * yo_t) / (1 + l)
            elif n == (self.N):
                xo_n = xo_t
                yo_n = yo_t
            # print("---------")
            # print(f"s X: {xo_s} Y: {yo_s}")
            # print(f"n X: {xo_n} Y: {yo_n}")
            # print(f"t X: {xo_t} Y: {yo_t}")
            # print("---------")
            new_0, new_1, new_2, new_ang_0, new_ang_1, new_ang_2, robot_head = self.get_new_params_by_vector(robot_num,
                                                                                                             xo_s, yo_s,
                                                                                                             xo_n, yo_n,
                                                                                                             hand_coords,
                                                                                                             move_hand)
            shifts = [0.0, 0.0, 0.0]
            shifts[0] = new_0
            shifts[1] = new_1
            shifts[2] = new_2

            angs = [0.0, 0.0, 0.0]
            angs[0] = normalize(new_ang_0)
            angs[1] = normalize(new_ang_1)
            angs[2] = normalize(new_ang_2)

            holds = [1, 1, 1]

            # print(f"t_ang: {t_angs[move_hand]}, t_shift: {t_shifts[move_hand]}")

            if move_hand != -1 and n < self.N:
                # print(f"Hold 0: {n}")
                holds[move_hand] = 0
                shifts[move_hand] = old_shift + delta_shift * n
                angs[move_hand] = normalize(old_ang + clockwise(new_ang - old_ang) * n / self.N)
            print(f"n = {n}, shifts: {shifts}; angs: {angs}")

            mirror = mirroring_check(angs[0], angs[1], angs[2])
            if not mirror:
                print("mirror false")
                return False
            else:
                print("mirror true")
        return True

    def move_vector(self, robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords, move_hand = -1):
        #robot_head = self.robots[robot_num].hands[hand_a].ang

        #self.N = 10

        t_0, t_1, t_2, t_ang_0, t_ang_1, t_ang_2, robot_head = self.get_new_params_by_vector(robot_num,
                                                                                             xo_s, yo_s,
                                                                                             xo_t, yo_t,
                                                                                             hand_coords,
                                                                                             move_hand)
        t_shifts = [t_0, t_1, t_2]
        t_angs = [t_ang_0, t_ang_1, t_ang_2]
        print(f"t_shifts: {t_shifts}; t_angs: {t_angs}")
        delta_ang = -1.0
        delta_shift = -1
        old_ang = -1.0
        old_shift = -1
        is_clockwise = -1

        # print(f"move hand: {move_hand}")

        is_possible = False
        if move_hand == -1:
            is_possible = self.is_move_possible_three_holds(robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords)
        else:
            is_possible = self.is_move_possible_two_holds(robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords, move_hand)

        if not is_possible:
            print("MOVE IS NOT POSSIBLE")
            return -1

        if move_hand != -1:
            delta_ang = (t_angs[move_hand] - self.robots[robot_num].hands[move_hand].ang) / self.N
            delta_shift = (t_shifts[move_hand] - self.robots[robot_num].hands[move_hand].lin) / self.N
            old_ang = self.robots[robot_num].hands[move_hand].ang
            old_shift = self.robots[robot_num].hands[move_hand].lin
            is_clockwise = self.check_clockwise(robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords,
                                                old_shift, old_ang,
                                                delta_shift, t_angs[move_hand], move_hand)
        print(f"move_hand is {move_hand}; old_shift: {old_shift}, old_ang: {old_ang}; delta_shift: {delta_shift}, delta_ang: {delta_ang}")

        prev_x_n, prev_y_n = xo_s, yo_s

        for n in range(self.N + 1):
            xo_n = xo_s
            yo_n = yo_s
            if 0 < n < self.N:
                l = n / (self.N - n)
                xo_n = (xo_s + l * xo_t) / (1 + l)
                yo_n = (yo_s + l * yo_t) / (1 + l)
            elif n == self.N:
                xo_n = xo_t
                yo_n = yo_t
            print("---------")
            print(f"s X: {xo_s} Y: {yo_s}")
            print(f"n X: {xo_n} Y: {yo_n}")
            print(f"t X: {xo_t} Y: {yo_t}")
            print("---------")
            print(f"Coords: {hand_coords}")
            new_0, new_1, new_2, new_ang_0, new_ang_1, new_ang_2, robot_head = self.get_new_params_by_vector(robot_num,
                                                                                                             prev_x_n, prev_y_n,
                                                                                                             xo_n, yo_n,
                                                                                                             hand_coords,
                                                                                                             move_hand)
            shifts = [0.0, 0.0, 0.0]
            shifts[0] = new_0
            shifts[1] = new_1
            shifts[2] = new_2

            angs = [0.0, 0.0, 0.0]
            angs[0] = normalize(new_ang_0)
            angs[1] = normalize(new_ang_1)
            angs[2] = normalize(new_ang_2)

            #TODO
            holds = [1, 1, 1]
            print(f"n = {n}; N = {self.N}")
            # print(f"t_ang: {t_angs[move_hand]}, t_shift: {t_shifts[move_hand]}")

            print(f"1 Shifts {shifts}, Angs: {angs}")
            if move_hand != -1 and n < self.N:
                # print(f"Hold 0: {n}")
                holds[move_hand] = 0
                shifts[move_hand] = old_shift + delta_shift * n
                if is_clockwise:
                    print("clockwise")
                    print(f"delta: {(t_angs[move_hand] - old_ang) / self.N}")
                    print(f"clockwise: {clockwise(t_angs[move_hand] - old_ang)}")
                    print(f"old_ang: {old_ang}")
                    print(f"new ang: {old_ang + clockwise(t_angs[move_hand] - old_ang) * n / self.N}")
                    angs[move_hand] = normalize(old_ang + clockwise(t_angs[move_hand] - old_ang) * n / self.N)
                else:
                    print("counterclockwise")
                    # angs[move_hand] = old_ang + n * (t_angs[move_hand] - old_ang) / self.N
                    print(f"delta: {(t_angs[move_hand] - old_ang) / self.N}")
                    print(f"counterclockwise: {counterclockwise(t_angs[move_hand] - old_ang) * n / self.N}")
                    print(f"old_ang: {old_ang}")
                    print(f"new ang: {old_ang + counterclockwise(t_angs[move_hand] - old_ang) * n / self.N}")
                    angs[move_hand] = normalize(old_ang + counterclockwise(t_angs[move_hand] - old_ang) * n / self.N)

            mirror = mirroring_check(angs[0], angs[1], angs[2])
            print(f"2 Shifts {shifts}, Angs: {angs}")
            if not mirror:
                print("Critical error with angles, abort!")
                return -1

            # time.sleep(2)

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
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")
            prev_x_n, prev_y_n = xo_n, yo_n
            self.move_hand(robot_num, 0, hand_coords[0][0], hand_coords[0][1])
            self.move_hand(robot_num, 1, hand_coords[1][0], hand_coords[1][1])
            self.move_hand(robot_num, 2, hand_coords[2][0], hand_coords[2][1])
            self.get_real_coordinates(robot_num, 0, 1, 2, shifts, angs, robot_head)
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)

    def adjust_hand(self, robot_num, xo_s, yo_s, hand_num):
        shift_0 = dist(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y,
                       xo_s, yo_s)
        shift_1 = dist(self.robots[robot_num].hands[1].x, self.robots[robot_num].hands[1].y,
                       xo_s, yo_s)
        shift_2 = dist(self.robots[robot_num].hands[2].x, self.robots[robot_num].hands[2].y,
                       xo_s, yo_s)
        shifts = [shift_0, shift_1, shift_2]

        stable_hands = [0, 1, 2]
        stable_hands.remove(hand_num)
        hand_c = stable_hands[0]
        if shifts[stable_hands[1]] > shifts[stable_hands[1]]:
            hand_c = stable_hands[1]
        stable_hands.remove(hand_c)
        stable_hands.append(hand_num)
        old_x = self.robots[robot_num].hands[hand_c].x
        old_y = self.robots[robot_num].hands[hand_c].y
        hand_coords = [(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y),
                       (self.robots[robot_num].hands[1].x, self.robots[robot_num].hands[1].y),
                       (self.robots[robot_num].hands[2].x, self.robots[robot_num].hands[2].y)]

        min_x = max(math.floor((((xo_s - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        max_x = max(math.floor((((xo_s + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        min_y = max(math.floor((((yo_s - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        max_y = max(math.floor((((yo_s + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)

        print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

        min_shift = size["outerRadLimit"] + 1
        best_x, best_y = -1, -1
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                print("---")
                print(f"IN LOOP x: {x}, y: {y}")
                x_ceil = ceil_to_coordinates(x)
                y_ceil = ceil_to_coordinates(y)
                print(f"TRUE COORDS x: {x_ceil}, y: {y_ceil}")

                # check if the point is inside the circle
                is_in_circle = False
                if (x_ceil - xo_s) ** 2 + (-y_ceil + yo_s) ** 2 <= size["outerRadLimit"] ** 2:
                    is_in_circle = True
                print(f"Is in circle? - {is_in_circle}")
                if not is_in_circle:
                    continue

                v1x, v1y = get_vector_coords(xo_s, yo_s,
                                             self.robots[robot_num].hands[stable_hands[0]].x,
                                             self.robots[robot_num].hands[stable_hands[0]].y)
                v2x, v2y = get_vector_coords(xo_s, yo_s,
                                             self.robots[robot_num].hands[stable_hands[1]].x,
                                             self.robots[robot_num].hands[stable_hands[1]].y)
                # check if the point is inside stable hands sector
                is_in_sector = point_in_sector(x_ceil, y_ceil, xo_s, yo_s, v1x, v1y, v2x, v2y)
                print(f"Is in sector? - {is_in_sector}")
                if is_in_sector:
                    continue

                # TODO limitations of greedy algorithm - need to improve
                xy_shift = dist(xo_s, yo_s, x_ceil, y_ceil)
                is_in_area = is_in_three_hands_area(self.robots[robot_num].hands[stable_hands[0]].x,
                                                    self.robots[robot_num].hands[stable_hands[0]].y,
                                                    self.robots[robot_num].hands[stable_hands[1]].x,
                                                    self.robots[robot_num].hands[stable_hands[1]].y,
                                                    x_ceil, y_ceil, xo_s, yo_s)
                print(f"Needed conditions are met? - {is_in_area}")
                if min_shift > xy_shift >= size["innerRadLimit"] and is_in_area and x_ceil != old_x and y_ceil != old_y:
                    a = is_in_three_hands_area(self.robots[robot_num].hands[stable_hands[0]].x,
                                               self.robots[robot_num].hands[stable_hands[0]].y,
                                               self.robots[robot_num].hands[stable_hands[1]].x,
                                               self.robots[robot_num].hands[stable_hands[1]].y,
                                               x_ceil, y_ceil, xo_s, yo_s)
                    min_shift = xy_shift
                    best_x = x_ceil
                    best_y = y_ceil

        # now we acquired the point to move hand C to
        # TODO check if the point is free!!
        if best_x != -1 and best_y != -1:
            hand_coords[hand_c] = (best_x, best_y)
            self.move_vector(robot_num, xo_s, yo_s, xo_s, yo_s, hand_coords)
        else:
            print("CAN'T FINISH THE MOVE, NO POSSIBLE POINTS")
            return -1
        #     return -1


    def move_step(self, robot_num, xo_s, yo_s, xo_t, yo_t, d = 0, hand_c = -1):
        a, b, c = get_line_equation(xo_s, yo_s, xo_t, yo_t)
        opt_points = optimal_points(a, b, c)

        print(f"xos: {xo_s} yos: {yo_s} xot: {xo_t} yot: {yo_t}")
        h = math.sqrt(size["outerRadLimit"]**2 - (size["netStep"]/2)**2) # TODO: not netStep, but dist between two stable holders
        if d==0:
            d = math.sqrt(h**2 + (size["netStep"] - size["innerRadLimit"])**2 / 4) / 2
        print(f"d: {d}")
        x_t_, y_t_ = get_point_on_dist(xo_s, yo_s, xo_t, yo_t, d)
        print(f"TEMP x {x_t_} y {y_t_}")


        shift_0 = dist(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y,
                       x_t_, y_t_)
        shift_1 = dist(self.robots[robot_num].hands[1].x, self.robots[robot_num].hands[1].y,
                       x_t_, y_t_)
        shift_2 = dist(self.robots[robot_num].hands[2].x, self.robots[robot_num].hands[2].y,
                       x_t_, y_t_)

        print(f"SHIFTS FOR 0: {shift_0} 1: {shift_1} 2: {shift_2}")

        shift_diff = [int(shift_0 > size["outerRadLimit"] or shift_0 < size["innerRadLimit"]),
                      int(shift_1 > size["outerRadLimit"] or shift_1 < size["innerRadLimit"]),
                      int(shift_2 > size["outerRadLimit"] or shift_2 < size["innerRadLimit"])]
        if hand_c != -1:
            shift_diff[hand_c] = 1
        sum_diff = sum(shift_diff)
        # print(f"sum_diff: {sum_diff}")

        hand_coords = [(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y),
                       (self.robots[robot_num].hands[1].x, self.robots[robot_num].hands[1].y),
                       (self.robots[robot_num].hands[2].x, self.robots[robot_num].hands[2].y)]

        if sum_diff == 0:
            # no need to check if the point is free - current robot occupies the area
            print("CASE 0")
            is_in_area = is_in_three_hands_area(self.robots[robot_num].hands[0].x,
                                                self.robots[robot_num].hands[0].y,
                                                self.robots[robot_num].hands[1].x,
                                                self.robots[robot_num].hands[1].y,
                                                self.robots[robot_num].hands[2].x,
                                                self.robots[robot_num].hands[2].y,
                                                x_t_, y_t_)
            is_possible = self.is_move_possible_three_holds(robot_num, xo_s, yo_s, x_t_, y_t_, hand_coords)
            if is_in_area and is_possible:
                    print("move possible")
                    self.move_vector(robot_num, xo_s, yo_s, x_t_, y_t_, hand_coords)
                # else:
                #     print("move NOT possible")
                #     shifts = [shift_0, shift_1, shift_2]
                #     min_shift = min(shifts)
                #     hand_c = shifts.index(min_shift)
                #     shift_diff[hand_c] = 1
                #     sum_diff = sum(shift_diff)
            else:
                shifts = [shift_0, shift_1, shift_2]
                max_shift = max(shifts)
                hand_c = shifts.index(max_shift)
                shift_diff[hand_c] = 1
                sum_diff = sum(shift_diff)

        if sum_diff == 1:
            print("CASE 1")
            hand_c = shift_diff.index(1)
            print(f"hand_c: {hand_c}")
            stable_hands = [0, 1, 2]
            stable_hands.remove(hand_c)

            is_limited = is_limited_by_others(self.robots[robot_num].hands[0].x,
                                              self.robots[robot_num].hands[0].y,
                                              self.robots[robot_num].hands[1].x,
                                              self.robots[robot_num].hands[1].y,
                                              self.robots[robot_num].hands[2].x,
                                              self.robots[robot_num].hands[2].y,
                                              xo_s, yo_s, hand_c)

            # if is_limited:
            #     self.adjust_hand(robot_num, xo_s, yo_s, hand_c)
            #     return 1

            # only one hand can't reach, move that hand to another hole; find the closest vacant place for a hand
            # give that as coordinates for moving function along with two stable hand coordinates

            # we have a circle with center in Ot and r = outerRadLimit
            # and a triangle, formed by two stable hands

            #min and max x and y for potentially available holes
            min_x = max(math.floor((((x_t_ - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
            max_x = max(math.floor((((x_t_ + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
            min_y = max(math.floor((((y_t_ - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
            max_y = max(math.floor((((y_t_ + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)

            print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

            min_shift = size["outerRadLimit"] + 1
            best_x, best_y = -1, -1
            for y in range(min_y, max_y+1):
                for x in range(min_x, max_x + 1):
                    # print("---")
                    # print(f"IN LOOP x: {x}, y: {y}")
                    x_ceil = ceil_to_coordinates(x)
                    y_ceil = ceil_to_coordinates(y)
                    # print(f"TRUE COORDS x: {x_ceil}, y: {y_ceil}")

                    # check if the point is inside the circle
                    is_in_circle = False
                    if (x_ceil-x_t_)**2 + (-y_ceil + y_t_)**2 <= size["outerRadLimit"]**2:
                        is_in_circle = True
                    # print(f"Is in circle? - {is_in_circle}")
                    if not is_in_circle:
                        continue

                    v1x, v1y = get_vector_coords(x_t_, y_t_,
                                                 self.robots[robot_num].hands[stable_hands[0]].x,
                                                 self.robots[robot_num].hands[stable_hands[0]].y)
                    v2x, v2y = get_vector_coords(x_t_, y_t_,
                                                 self.robots[robot_num].hands[stable_hands[1]].x,
                                                 self.robots[robot_num].hands[stable_hands[1]].y)
                    # check if the point is inside stable hands sector
                    is_in_sector = point_in_sector(x_ceil, y_ceil, x_t_, y_t_, v1x, v1y, v2x, v2y)
                    # print(f"Is in sector? - {is_in_sector}")
                    if is_in_sector or (not is_in_sector and is_limited): # TODO check and test
                        continue

                    # TODO limitations of greedy algorithm - need to improve
                    xy_shift = dist(x_t_, y_t_, x_ceil, y_ceil)
                    # is_in_area = is_in_three_hands_area(self.robots[robot_num].hands[stable_hands[0]].x,
                    #                                     self.robots[robot_num].hands[stable_hands[0]].y,
                    #                                     self.robots[robot_num].hands[stable_hands[1]].x,
                    #                                     self.robots[robot_num].hands[stable_hands[1]].y,
                    #                                     x_ceil, y_ceil, x_t_, y_t_)
                    temp_hand_coords = hand_coords[:]
                    temp_hand_coords[hand_c] = (x_ceil, y_ceil)
                    # is_possible = self.is_move_possible_two_holds(robot_num,
                    #                                               xo_s, yo_s,
                    #                                               x_t_, y_t_,
                    #                                               temp_hand_coords, hand_c)
                    # print(f"Needed conditions are met? - {is_in_area}")
                    xy = (x_ceil, y_ceil)
                    is_in_optimal = xy in opt_points
                    if is_in_optimal and xy_shift < min_shift:
                        min_shift = xy_shift
                        best_x = x_ceil
                        best_y = y_ceil

            # now we acquired the point to move hand C to
            # TODO check if the point is free!!
            print(f"BEST x: {best_x}, y: {best_y}")
            if best_x != -1 and best_y != -1:
                hand_coords[hand_c] = (best_x, best_y)
                is_possible = self.is_move_possible_two_holds(robot_num,
                                                              xo_s, yo_s,
                                                              x_t_, y_t_,
                                                              hand_coords, hand_c)
                if is_possible:
                    print("Move is possible (move_step case 1)")
                    print(f"hand c: {hand_c}")
                    self.move_vector(robot_num, xo_s, yo_s, x_t_, y_t_, hand_coords, hand_c)
                else:
                    print("Move is impossible (move_step case 1), searching for a new Ot'")
                    new_xo_t_, new_yo_t_ = self.find_new_position_three_holds(robot_num, xo_s, yo_s,
                                                                              x_t_, y_t_, hand_coords, hand_c)
                    print(f"New Ot' coords: ({new_xo_t_}, {new_yo_t_})")
                    if new_xo_t_ == -1 or new_yo_t_ == -1:
                        print("No possible position, return")
                        return -1
                    self.move_vector(robot_num, xo_s, yo_s, new_xo_t_, new_yo_t_, hand_coords)
            else:
                print("CAN'T FINISH THE MOVE, NO POSSIBLE POINTS")
                # need to either adjust other hands OR mark another hand as hand C
                if is_limited:
                    self.adjust_hand(robot_num, xo_s, yo_s, hand_c)
                else:
                    return -1
                # else:
                #     new_xo_t_, new_yo_t_ = self.find_new_position_three_holds(robot_num, xo_t, yo_t, hand_coords)
                #     self.move_vector(robot_num, xo_s, yo_s, new_xo_t_, new_yo_t_, hand_coords)
                # self.move_step(robot_num, xo_s, yo_s, xo_t, yo_t)
                # time.sleep(2)
                # new_d = d - size["innerRadLimit"]  # just for testing, TODO need to come up with something reasonable
                # if new_d <= 0:
                #     print("CAN'T FINISH THE MOVE, ADJUST THE Ot`")
                #     # if is_limited:
                #     #     self.adjust_hand(robot_num, xo_s, yo_s, hand_c)
                #     #     return 1
                #     # time.sleep(2)
                #     # sign_delta_x = (xo_t - xo_s) / abs(xo_t - xo_s)
                #     # sign_delta_y = (yo_t - yo_s) / abs(yo_t - yo_s)
                #     # adj_x = x_t_ + sign_delta_x * size["innerRadLimit"]
                #     # adj_y = y_t_ + sign_delta_y * size["innerRadLimit"]
                #     # self.move_step(robot_num, xo_s, yo_s, adj_x, adj_y, 0)
                #     return -1

                # self.move_step(robot_num, xo_s, yo_s, xo_t, yo_t, new_d)
                # return -1

        if sum_diff >= 2:
            print("CASE 2")
            # can't move to that point in one step, need to find closer point
            # TODO strategy for point (Ot) selection
            new_d = d - size["innerRadLimit"] # just for testing, TODO need to come up with something reasonable
            if new_d <= 0:
                print("CAN'T FINISH THE MOVE")
                # time.sleep(5)
                return -1
            self.move_step(robot_num, xo_s, yo_s, xo_t, yo_t, new_d)

        return 0

    def get_neighbours(self, hand_coords):
        neighbours = []
        # min_x = coordinates_to_ceil(min(hand_coords[0][0], hand_coords[1][0], hand_coords[2][0]))
        # min_y = coordinates_to_ceil(min(hand_coords[0][1], hand_coords[1][1], hand_coords[2][1]))
        # max_x = coordinates_to_ceil(max(hand_coords[0][0], hand_coords[1][0], hand_coords[2][0]))
        # max_y = coordinates_to_ceil(max(hand_coords[0][1], hand_coords[1][1], hand_coords[2][1]))

        # min_x = max(min_x - size["outerRadLimit"] * 2, 0)
        # min_y = max(min_y - size["outerRadLimit"] * 2, 0)
        # max_x = min(max_x + size["outerRadLimit"] * 2, self.max_x)
        # max_y = min(max_y + size["outerRadLimit"] * 2, self.max_y)

        min_x = coordinates_to_ceil((min(hand_coords[0][0], hand_coords[1][0], hand_coords[2][0])) - 2 * size["outerRadLimit"])
        min_y = coordinates_to_ceil((min(hand_coords[0][1], hand_coords[1][1], hand_coords[2][1])) - 2 * size["outerRadLimit"])
        max_x = coordinates_to_ceil((max(hand_coords[0][0], hand_coords[1][0], hand_coords[2][0])) + 2 * size["outerRadLimit"])
        max_y = coordinates_to_ceil((max(hand_coords[0][1], hand_coords[1][1], hand_coords[2][1])) + 2 * size["outerRadLimit"])

        print(f"IN GET NEIGHBOURS BEFORE MODIFICATION: x: {min_x}-{max_x}; y: {min_y}-{max_y}")

        min_x = max(min_x, 0)
        min_y = max(min_y, 0)
        max_x = min(max_x, self.max_x)
        max_y = min(max_y, self.max_y)

        print(f"IN GET NEIGHBOURS: x: {min_x}-{max_x}; y: {min_y}-{max_y}")

        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                x_ceil = ceil_to_coordinates(x)
                y_ceil = ceil_to_coordinates(y)
                is_in_circle_1 = False
                is_in_circle_2 = False
                is_in_circle_3 = False
                if (x_ceil - hand_coords[0][0]) ** 2 + (-y_ceil + hand_coords[0][1]) ** 2 <= (size["outerRadLimit"]*2) ** 2:
                    is_in_circle_1 = True
                if (x_ceil - hand_coords[1][0]) ** 2 + (-y_ceil + hand_coords[1][1]) ** 2 <= (size["outerRadLimit"]*2) ** 2:
                    is_in_circle_2 = True
                if (x_ceil - hand_coords[2][0]) ** 2 + (-y_ceil + hand_coords[2][1]) ** 2 <= (size["outerRadLimit"]*2) ** 2:
                    is_in_circle_3 = True
                if (is_in_circle_1 and is_in_circle_2) or (is_in_circle_2 and is_in_circle_3) or (is_in_circle_3 and is_in_circle_1):
                    neighbours.append((x_ceil, y_ceil))
        return neighbours

    def get_robot_angle(self, hand_coords, xo_t, yo_t):
        # TODO take the farthest hand, calculate the middle point between two other hands, use this as a vector
        # TODO take robot head position into account?
        robot_angle = -1
        x_horizontal = 5  # horizontal vector
        y_horizontal = 0
        d = dists(hand_coords[0][0], hand_coords[0][1],
                  hand_coords[1][0], hand_coords[1][1],
                  hand_coords[2][0], hand_coords[2][1],
                  xo_t, yo_t)
        m = max(d)
        a = d.index(m)
        a_x = hand_coords[a][0]
        a_y = hand_coords[a][1]

        hands = [0, 1, 2]
        hands.remove(a)

        b_x = (hand_coords[hands[0]][0] + hand_coords[hands[1]][0]) / 2
        b_y = (hand_coords[hands[0]][1] + hand_coords[hands[1]][1]) / 2

        x_r_vector, y_r_vector = get_vector_coords(a_x, a_y,
                                                   b_x, b_y)
        robot_angle = angle_between_vectors(x_horizontal, y_horizontal, x_r_vector, y_r_vector)


        # if is_aligned(hand_coords):
        #     x_r_vector, y_r_vector = get_vector_coords(hand_coords[0][0], hand_coords[0][1],
        #                                                hand_coords[1][0], hand_coords[1][1])  # vector of robot line
        #     robot_angle = angle_between_vectors(x_horizontal, y_horizontal, x_r_vector, y_r_vector)
        # else:
        #     # take two points where x1 != x2 and y1 != y2 and this line will be robot line
        #     # TODO detect T-position?
        #     hand1 = 0
        #     hand2 = 1
        #     if hand_coords[hand1][0] == hand_coords[hand2][0] or hand_coords[hand1][1] == hand_coords[hand2][1]:
        #         hand2 = 2
        #     x_r_vector, y_r_vector = get_vector_coords(hand_coords[hand1][0], hand_coords[hand1][1],
        #                                                hand_coords[hand2][0], hand_coords[hand2][1])
        #     robot_angle = angle_between_vectors(x_horizontal, y_horizontal, x_r_vector, y_r_vector)
        return robot_angle

    def is_in(self, point, arr):
        for xy in arr:
            print(f"Comparison: {xy} AND {point}", end="")
            if point[0] == xy[0] and point[1] == xy[1]:
                print("yes")
                return True
            print("no")
        return False

    def adjust_robot(self, robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords):
        d = dists(hand_coords[0][0], hand_coords[0][1],
                  hand_coords[0][0], hand_coords[0][1],
                  hand_coords[0][0], hand_coords[0][1],
                  xo_t, yo_t)
        shift_diff = [int(d[0] > size["outerRadLimit"] or d[0] < size["innerRadLimit"]),
                      int(d[1] > size["outerRadLimit"] or d[1] < size["innerRadLimit"]),
                      int(d[2] > size["outerRadLimit"] or d[2] < size["innerRadLimit"])]
        sum_diff = sum(shift_diff)
        if sum_diff == 0:
            # no need to check if the point is free - current robot occupies the area
            print("CASE 0")
            is_in_area = is_in_three_hands_area(self.robots[robot_num].hands[0].x,
                                                self.robots[robot_num].hands[0].y,
                                                self.robots[robot_num].hands[1].x,
                                                self.robots[robot_num].hands[1].y,
                                                self.robots[robot_num].hands[2].x,
                                                self.robots[robot_num].hands[2].y,
                                                xo_t, yo_t)
            is_possible = self.is_move_possible_three_holds(robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords)
            if is_in_area and is_possible:
                    print("move possible")
                    return [(hand_coords[0][0], hand_coords[0][1]),
                            (hand_coords[1][0], hand_coords[1][1]),
                            (hand_coords[2][0], hand_coords[2][1])]
                    # self.move_vector(robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords)
            else:
                shifts = [d[0], d[1], d[2]]
                max_shift = max(shifts)
                hand_c = shifts.index(max_shift)
                shift_diff[hand_c] = 1
                sum_diff = sum(shift_diff)

        if sum_diff == 1:
            print("CASE 1")
            hand_c = shift_diff.index(1)
            print(f"hand_c: {hand_c}")
            stable_hands = [0, 1, 2]
            stable_hands.remove(hand_c)

            # is_limited = is_limited_by_others(hand_coords[0][0],
            #                                   hand_coords[0][1],
            #                                   hand_coords[1][0],
            #                                   hand_coords[1][1],
            #                                   hand_coords[2][0],
            #                                   hand_coords[2][1],
            #                                   xo_s, yo_s, hand_c)


            # only one hand can't reach, move that hand to another hole; find the closest vacant place for a hand
            # give that as coordinates for moving function along with two stable hand coordinates

            # we have a circle with center in Ot and r = outerRadLimit
            # and a triangle, formed by two stable hands

            #min and max x and y for potentially available holes
            min_x = max(math.floor((((xo_t - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
            max_x = min(math.floor((((xo_t + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), self.max_x-1)
            min_y = max(math.floor((((yo_t - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
            max_y = min(math.floor((((yo_t + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), self.max_y-1)

            print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

            min_shift = size["outerRadLimit"] + 1
            best_x, best_y = -1, -1
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    # print("---")
                    # print(f"IN LOOP x: {x}, y: {y}")
                    x_ceil = ceil_to_coordinates(x)
                    y_ceil = ceil_to_coordinates(y)

                    if (hand_coords[0][0] == x_ceil and hand_coords[0][1] == y_ceil) or (
                            hand_coords[1][0] == x_ceil and hand_coords[1][1] == y_ceil) or (
                            hand_coords[2][0] == x_ceil and hand_coords[2][1] == y_ceil):
                        print(f"Exist in current pos: {x_ceil}, {y_ceil}")
                        continue
                    # print(f"TRUE COORDS x: {x_ceil}, y: {y_ceil}")

                    # check if the point is inside the circle
                    is_in_circle = False
                    if (x_ceil-xo_t)**2 + (-y_ceil + yo_t)**2 <= size["outerRadLimit"]**2:
                        is_in_circle = True
                    # print(f"Is in circle? - {is_in_circle}")
                    if not is_in_circle:
                        print(f"Not in circle: {x_ceil}, {y_ceil}")
                        continue

                    temp_hand_coords = hand_coords[:]
                    temp_hand_coords[hand_c] = (x_ceil, y_ceil)

                    new_0, new_1, new_2, ang_0, ang_1, ang_2, rh = self.get_new_params_by_vector(robot_num,
                                                                                                 xo_s, yo_s,
                                                                                                 xo_t,
                                                                                                 yo_t,
                                                                                                 temp_hand_coords)
                    is_correct_hand_order = mirroring_check(ang_0, ang_1, ang_2)
                    pos_conditions = self.check_conditions_pos(robot_num, xo_t, yo_t, xo_s, yo_s, temp_hand_coords, hand_c)

                    # print(f"Is in sector? - {is_in_sector}")
                    if not is_correct_hand_order or not pos_conditions: # TODO check and test
                        print(f"Conditions are not met: {x_ceil}, {y_ceil}")
                        continue

                    xy_shift = dist(xo_t, yo_t, x_ceil, y_ceil)

                    # xy = (x_ceil, y_ceil)
                    # is_in_optimal = xy in opt_points
                    # if is_in_optimal and xy_shift < min_shift:
                    if xy_shift < min_shift:
                        min_shift = xy_shift
                        best_x = x_ceil
                        best_y = y_ceil

            # now we acquired the point to move hand C to
            # TODO check if the point is free!!
            print(f"BEST x: {best_x}, y: {best_y}")
            if best_x != -1 and best_y != -1:
                hand_coords[hand_c] = (best_x, best_y)
                is_possible = self.is_move_possible_two_holds(robot_num,
                                                              xo_s, yo_s,
                                                              xo_t, yo_t,
                                                              hand_coords, hand_c)
                if is_possible:
                    print("Move is possible (move_step case 1)")
                    print(f"hand c: {hand_c}")
                    return [(hand_coords[0][0], hand_coords[0][1]),
                            (hand_coords[1][0], hand_coords[1][1]),
                            (hand_coords[2][0], hand_coords[2][1])]
                    # self.move_vector(robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords, hand_c)
            else:
                print("CAN'T FINISH THE MOVE, NO POSSIBLE POINTS")
                # else:
        return [(-1, -1)]

    def check_point(self, robot_num, hand_coords, hand_c, xo_s, yo_s, neighbour, opt_points):
        stable_hands = [0, 1, 2]
        stable_hands.remove(hand_c)
        # print(neighbour)
        # print(f"Function optimal: {opt_points}")

        # is_limited = is_limited_by_others(hand_coords[0][0],
        #                                   hand_coords[0][1],
        #                                   hand_coords[1][0],
        #                                   hand_coords[1][1],
        #                                   hand_coords[2][0],
        #                                   hand_coords[2][1],
        #                                   xo_s, yo_s, hand_c)

        x_ceil = neighbour[0]
        y_ceil = neighbour[1]

        xy = (x_ceil, y_ceil)
        is_in_optimal = xy in opt_points

        temp_hand_coords = hand_coords[:]
        print(f"Temp hand coords: {temp_hand_coords}")


        new_center_x, new_center_y = -1, -1
        # print("HELLO HELLO HELLO")
        if is_aligned(temp_hand_coords):
            #find from triangles
            middle = middle_point((temp_hand_coords[0][0], temp_hand_coords[0][1]),
                                  (temp_hand_coords[1][0], temp_hand_coords[1][1]),
                                  (temp_hand_coords[2][0], temp_hand_coords[2][1]))
            non_middle = [0, 1, 2]
            non_middle.remove(middle)
            # print(f"Middle: {middle}, non-middle: {non_middle}")
            l1 = dist(temp_hand_coords[middle][0], temp_hand_coords[middle][1],
                     temp_hand_coords[non_middle[0]][0], temp_hand_coords[non_middle[0]][1])
            l2 = dist(temp_hand_coords[middle][0], temp_hand_coords[middle][1],
                     temp_hand_coords[non_middle[1]][0], temp_hand_coords[non_middle[1]][1])
            # print(f"l1: {l1}, l2: {l2}")

            temp_shifts = [-1, -1, -1]
            temp_shifts[middle] = size["innerRadLimit"]*1.05
            temp_shifts[non_middle[0]] = math.sqrt(temp_shifts[middle] ** 2 + l1 ** 2)
            temp_shifts[non_middle[1]] = math.sqrt(temp_shifts[middle] ** 2 + l2 ** 2)
            print(f"Temp shifts: {temp_shifts}")
            new_center_x, new_center_y = calculate_center(temp_hand_coords[0][0], temp_hand_coords[0][1],
                                                          temp_hand_coords[1][0], temp_hand_coords[1][1],
                                                          temp_hand_coords[2][0], temp_hand_coords[2][1],
                                                          temp_shifts[0], temp_shifts[1], temp_shifts[2])
            print(f"New center: {new_center_x}, {new_center_y}")
        else:
            new_center_x = (temp_hand_coords[0][0] + temp_hand_coords[1][0] + temp_hand_coords[2][0]) / 3
            new_center_y = (temp_hand_coords[0][1] + temp_hand_coords[1][1] + temp_hand_coords[2][1]) / 3
            print(f"New center: {new_center_x}, {new_center_y}")

            # check if the point is inside the circle
            # is_in_circle = False
            # if (x_ceil - xo_s) ** 2 + (-y_ceil + yo_s) ** 2 <= size["outerRadLimit"] ** 2:
            #     is_in_circle = True
            # if not is_in_circle:
            #     return -1, -1

        is_possible = is_in_three_hands_area(hand_coords[0][0], hand_coords[0][1],
                                             hand_coords[1][0], hand_coords[1][1],
                                             hand_coords[2][0], hand_coords[2][1], new_center_x, new_center_y)
        new_0, new_1, new_2, ang_0, ang_1, ang_2, rh = self.get_new_params_by_vector(robot_num,
                                                                                     xo_s, yo_s,
                                                                                     new_center_x, new_center_y,
                                                                                     hand_coords)
        is_correct_hand_order = mirroring_check(ang_0, ang_1, ang_2)
        is_move_possible = True

        if hand_c != -1:
            is_move_possible = self.is_move_possible_two_holds(robot_num, xo_s, yo_s,
                                                               new_center_x, new_center_y,
                                                               hand_coords, hand_c)
        else:
            is_move_possible = self.is_move_possible_three_holds(robot_num, xo_s, yo_s,
                                                                 new_center_x, new_center_y,
                                                                 hand_coords)
        print(f"Conditions: {is_possible}, {is_correct_hand_order}")
        if is_possible and is_correct_hand_order:
            if not is_move_possible:
                # global new_center_x, new_center_y
                new_center_x, new_center_y = self.find_new_position_three_holds(robot_num, xo_s, yo_s,
                                                                                new_center_x, new_center_y,
                                                                                hand_coords, hand_c)
                return new_center_x, new_center_y
            return new_center_x, new_center_y
            # print("Move is possible (move_step case 1)")
            # new_center_x, new_center_y = self.find_new_position_three_holds(robot_num, xo_s, yo_s,
            #                                    new_center_x, new_center_y, hand_coords, hand_c)
            # if new_center_x == -1 or new_center_y == -1:
            # return -1, -1
            # return new_center_x, new_center_y
            # print(f"hand c: {hand_c}")
            # self.move_vector(robot_num, xo_s, yo_s, x_t_, y_t_, hand_coords, hand_c)
        return -1, -1

    # first we determine optimal path by holes, then robot moves to a specified holes
    def build_path(self, robot_num, xo_s, yo_s, xo_t, yo_t):
        self.robots[robot_num].isMoving = True
        self.robots[robot_num].curr_index = -1
        a, b, c = get_line_equation(xo_s, yo_s, xo_t, yo_t)
        opt_points = optimal_points(a, b, c)
        self.robots[robot_num].opt_points = opt_points[:]
        # print(f"Start optimal: {opt_points}")

        # since we are not actually moving robot yet, we need to store it's params for position evaluation
        hand_coords = [(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y),
                       (self.robots[robot_num].hands[1].x, self.robots[robot_num].hands[1].y),
                       (self.robots[robot_num].hands[2].x, self.robots[robot_num].hands[2].y)]

        # path format: [ [(x0, y0), (x1, y1), (x2, y2)], ... [(x0, y0), (x1, y1), (x2, y2)] ]
        # where [(x0, y0), (x1, y1), (x2, y2)] (path[n]) in position of robot in form of coordinates
        path = [hand_coords]

        # format: [(x, y), (x, y), ... (x, y)]
        # for storing centers
        centers = [(xo_s, yo_s)]

        pos_conditions = self.check_conditions_pos(robot_num, xo_t, yo_t, xo_s, yo_s, hand_coords)
        if pos_conditions:
            # the point Ot is within robot's reach, no need to move hands or adjust position
            print("move possible")
            path.append(hand_coords)
            centers.append((xo_t, yo_t))
            self.robots[robot_num].path = path[:]
            self.robots[robot_num].centers = centers[:]
            print(path)
            print(centers)
            self.robots[robot_num].isMoving = False
            return

        # temp_hand_coords = [(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y),
        #                     (self.robots[robot_num].hands[1].x, self.robots[robot_num].hands[1].y),
        #                     (self.robots[robot_num].hands[2].x, self.robots[robot_num].hands[2].y)]

        robot_shifts = [self.robots[robot_num].hands[0].lin,
                        self.robots[robot_num].hands[1].lin,
                        self.robots[robot_num].hands[2].lin]
        robot_angs = [self.robots[robot_num].hands[0].ang,
                      self.robots[robot_num].hands[1].ang,
                      self.robots[robot_num].hands[2].ang]

        # 1. Calculate the Os-Ot vector direction
        # 2. Calculate the robot vector direction (by the holders)
        # 3. Align robot +- to the OsOt vector, so it can reach more path holes
        # 4. Start algorithm of point (holes) selection

        x_horizontal = 5  # horizontal vector
        y_horizontal = 0

        x_osot_vector, y_osot_vector = get_vector_coords(xo_s, yo_s, xo_t, yo_t)  # vector of Os-Ot line
        osot_angle = angle_between_vectors(x_horizontal, y_horizontal, x_osot_vector, y_osot_vector)

        robot_angle = self.get_robot_angle(hand_coords, xo_t, yo_t)

        # now compare osot and robot angles and try to align robot (mark points for alignment)
        # TODO take the 180 angle into account
        delta_ang = min(abs(osot_angle - robot_angle), 360-abs(osot_angle - robot_angle))
        eps = 22.5 # 45 degrees, might change later TODO check this value mathematically
        best_delta = delta_ang
        center_x, center_y = center_by_params(hand_coords, robot_shifts[0], robot_shifts[1], robot_shifts[2])
        best_center = (-1, -1)
        # turn_pos = []
        counter = 0
        print(f"BEFORE BUILD PATH TURN, DELTA IS: {best_delta}")

        while best_delta > eps and counter < 2 and yo_t-yo_s > size["netStep"]:
            turn_pos = []
            # TODO secure from dead-end positions AND T-pos should have different angle calc
            print(f"IN BUILD PATH TURN, DELTA IS: {best_delta}")
            counter += 1
            neighbours = self.get_neighbours(hand_coords)
            print(f"Neighbours: {neighbours}")
            point_found = False
            # best_delta = delta_ang
            for point in neighbours:
                if (hand_coords[0][0] == point[0] and hand_coords[0][1] == point[1]) or (
                        hand_coords[1][0] == point[0] and hand_coords[1][1] == point[1]) or (
                        hand_coords[2][0] == point[0] and hand_coords[2][1] == point[1]):
                    print("Exist in current pos")
                    continue
                # determine which hand(s) can be moved to this point
                # print(f"In point search, we have {len(neighbours)} neighbours")
                can_move_hands = []
                can_move_to = []
                # best_center = -1, -1
                for j in range(3):
                    stable_hands = [0, 1, 2]
                    stable_hands.remove(j)
                    # print(f"Iteration {i}, hand {j}")
                    # print(f"Temp coords before: {temp_hand_coords}")
                    temp_coords = hand_coords[:]

                    temp_coords[j] = point
                    print(f"Temp coords: {temp_coords}")
                    new_center_x, new_center_y = self.check_point(robot_num, temp_coords, j, center_x, center_y, point, opt_points)
                    print(f"Hand {j}: ({new_center_x}, {new_center_y})")
                    if new_center_x != -1 and new_center_y != -1:
                        new_0, new_1, new_2, ang_0, ang_1, ang_2, rh = self.get_new_params_by_vector(robot_num,
                                                                                                     center_x, center_y,
                                                                                                     new_center_x,
                                                                                                     new_center_y,
                                                                                                     temp_coords)
                        mirror_check = mirroring_check(ang_0, ang_1, ang_2)
                        # if is_in_sector or (not is_in_sector and is_limited) or not mirror_check:
                        if not mirror_check:  # TODO check and test
                            # print("nope")
                            continue
                        else:
                            can_move_hands.append(j)
                            can_move_to.append((new_center_x, new_center_y))

                # print(f"Can move hands: {can_move_hands}")
                for j in range(len(can_move_hands)):
                    # re-calculate robot angle
                    temp_coords = hand_coords[:]
                    hand = can_move_hands[j]
                    temp_coords[hand] = point
                    # print(f"J: {j}")
                    # print(f"Hand: {hand}")
                    # print(f"Can move to: {can_move_to}")
                    # print(f"Turn coords: {temp_hand_coords}")

                    new_robot_angle = self.get_robot_angle(temp_coords, xo_t, yo_t)
                    # print(f"Robot angle: {new_robot_angle}")
                    new_delta_ang = abs(osot_angle - new_robot_angle)
                    print(f"Delta: {new_delta_ang}")
                    if new_delta_ang < best_delta:
                        best_delta = new_delta_ang
                        turn_pos = temp_coords[:]
                        print(f"Turn pos: {turn_pos}")
                        best_center = can_move_to[j]
                        print(f"Best center: {best_center}")
                        point_found = True
                    temp_coords = hand_coords[:]
            if point_found:
                point_found = False
                path.append(turn_pos)
                centers.append(best_center)
                # print(f"Hand coords before: {hand_coords}")
                hand_coords = turn_pos[:]
                # print(f"Hand coords after: {hand_coords}")
                new_0, new_1, new_2, ang_0, ang_1, ang_2, rh = self.get_new_params_by_vector(robot_num,
                                                                                             center_x, center_y,
                                                                                             best_center[0], best_center[1],
                                                                                             hand_coords)
                robot_shifts[0] = new_0
                robot_shifts[1] = new_1
                robot_shifts[2] = new_2
                robot_angs[0] = ang_0
                robot_angs[1] = ang_1
                robot_angs[2] = ang_2
                center_x = best_center[0]
                center_y = best_center[1]


        # TODO protect from dead-end positions
        move_finished = False
        counter = -1
        # old_center_x, old_center_y = -1, -1
        print(f"PATH AFTER TURN: {path}")
        while not move_finished and counter <= 2000:
            print(f"Is move finished? {move_finished}")
            print(f"Path in loop: {path}")
            # if center_x == old_center_x and center_y == old_center_y:
            #     print("Position hasn't changed, abort")
            #     break
            # old_center_x = center_x
            # old_center_y = center_y
            # print(counter)
            counter += 1
            pos_conditions = self.check_conditions_pos(robot_num, xo_t, yo_t, xo_s, yo_s, hand_coords)
            if pos_conditions:
                # the point Ot is within robot's reach, no need to move hands or adjust position
                print("move possible")
                path.append(hand_coords)
                centers.append((xo_t, yo_t))
                move_finished = True
            else:
                # TODO check if we can move ONE hand to get the needed position
                neighbours = self.get_neighbours(hand_coords)
                sorted_neighbours = sorted(neighbours, key=lambda p: dist(p[0], p[1], xo_t, yo_t))
                print(f"Sorted neighbours: {sorted_neighbours}")

                potential_pos = self.adjust_robot(robot_num, center_x, center_y, xo_t, yo_t, hand_coords)
                print(f"Potential pos: {potential_pos}")
                if potential_pos[0][0] != -1:
                    path.append(potential_pos)
                    centers.append((xo_t, yo_t))
                    move_finished = True
                    print("Move finished!")
                    break
                    # continue
                print(f"Move finished? {move_finished}")

                point_found = False
                # hand_found = False
                for point in sorted_neighbours:
                    if point_found:
                        break
                    print(f"Point: {point}")
                    print(f"Hand coords: {hand_coords}")
                    if not point in opt_points:
                        print("Not optimal")
                        continue
                    if (hand_coords[0][0] == point[0] and hand_coords[0][1] == point[1]) or (
                            hand_coords[1][0] == point[0] and hand_coords[1][1] == point[1]) or (
                            hand_coords[2][0] == point[0] and hand_coords[2][1] == point[1]):
                        print("Exist in current pos")
                        continue
                    # set of centers that will be obtained in case we move the i hand
                    centers_for_hand_moves = [(-1, -1), (-1, -1), (-1, -1)]
                    for j in range(3):
                        print(f"IN LOOP Hand coords: {hand_coords}")
                        temp_coords = hand_coords[:]
                        temp_coords[j] = point
                        print(f"IN LOOP Temp coords: {temp_coords}")
                        new_x, new_y = self.check_point(robot_num, temp_coords, j, center_x, center_y, point, opt_points)
                        print(f"Hand {j}: ({new_x}, {new_y})")
                        # print(f"Temp coords: {temp_hand_coords}")
                        # print(f"Loop optimal: {opt_points}")
                        if new_x != -1 and new_y != -1:
                            print(f"ADDING {point} FOR {j}")
                            if temp_coords in path:
                                print("There is already such position in path, aborting the loop!")
                                temp_coords = hand_coords[:]
                                # move_finished = True
                                # print(f"Is move finished? (pos exist): {move_finished}")
                                # break
                            else:
                                print(f"Adding the position: {temp_coords}")
                                centers_for_hand_moves[j] = (new_x, new_y)
                                path.append(temp_coords)
                                centers.append((new_x, new_y))
                                point_found = True
                                new_0, new_1, new_2, ang_0, ang_1, ang_2, rh = self.get_new_params_by_vector(robot_num,
                                                                                                             center_x,
                                                                                                             center_y,
                                                                                                             new_x, new_y,
                                                                                                             temp_coords)
                                robot_shifts[0] = new_0
                                robot_shifts[1] = new_1
                                robot_shifts[2] = new_2
                                robot_angs[0] = ang_0
                                robot_angs[1] = ang_1
                                robot_angs[2] = ang_2
                                center_x = new_x
                                center_y = new_y
                                hand_coords = temp_coords[:]
                                break
                        if point_found or move_finished:
                            break
                if not point_found:
                    print("Didn't find the point!!!")
                    move_finished = True
                    break

        print(f"AFTER Is move finished? {move_finished}")
        self.robots[robot_num].path = path[:]
        self.robots[robot_num].centers = centers[:]
        print(path)
        print(centers)
        self.robots[robot_num].isMoving = False

    def start_robot_by_path(self, robot_num):
        for i in range(1, len(self.robots[robot_num].path)):
            x_t, y_t = self.robots[robot_num].centers[i]
            x_s, y_s = self.robots[robot_num].get_center()
            print(f"Iteration No.{i}: Os = ({x_s}, {y_s}); Ot = ({x_t}, {y_t});")
            pos = self.robots[robot_num].path[i]
            print(f"Position: {pos}")
            move_hand = -1
            for j in range(3):
                if pos[j][0] != self.robots[robot_num].hands[j].x or pos[j][1] != self.robots[robot_num].hands[j].y:
                    if move_hand != -1:
                        print("Need to move two hands at the same time, impossible!")
                        return -1
                    else:
                        move_hand = j
            res = self.move_vector(robot_num, x_s, y_s, x_t, y_t, pos, move_hand)
            if res == -1:
                print("Critical error, return")
                return
        return 1


    # --- OLD FUNCTIONS ---
    '''
    def to_right(self, robot_num, hand_a, hand_b, hand_c):
        # N = 2  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0

        BASE = 0

        print(f"hand_a = {hand_a}; hand_b = {hand_b}; hand_c = {hand_c}")

        robot_head = self.robots[robot_num].hands[hand_a].ang - BASE

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # ідеальна модель з кутом А = 0
        aa0 = BASE
        ab0 = BASE + darctan(L / l)
        ac0 = BASE - darctan(L / l)
        acN = BASE + darctan(L / l)

        # рука С при русі не змінює довжини
        sa0 = l
        sb0 = sc0 = math.sqrt(L ** 2 + l ** 2)
        # TODO if not in correct position, return

        for n in range(self.N + 1):
            sa = math.sqrt((L / self.N * n) ** 2 + l ** 2)
            sb = math.sqrt((L - L / self.N * n) ** 2 + l ** 2)
            sc = sc0

            # зачеп руки С
            if n == 1:
                hc = 0
            elif n == self.N:
                hc = 1

            # кути рахуються проти годинникової стрілки
            aa = BASE - darctan(L / l * n / self.N)
            ab = BASE + darctan(L / l * (1 - n / self.N))
            ac = ac0 + clockwise(acN - ac0) * n / self.N

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
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def to_left(self, robot_num, hand_a, hand_b, hand_c):
        # N = 2  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0

        BASE = 0

        robot_head = self.robots[robot_num].hands[hand_a].ang - BASE

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # ідеальна модель з кутом А = 0
        aa0 = BASE
        ab0 = BASE + darctan(L / l)
        ac0 = BASE - darctan(L / l)
        abN = BASE - darctan(L / l)

        sa0 = l
        sb0 = sc0 = math.sqrt(L**2 + l**2)
        # TODO if not in correct position, return

        for n in range(self.N + 1):
            sa = math.sqrt((L * n / self.N) ** 2 + l ** 2)
            sb = sb0
            sc = math.sqrt((L * (1 - n / self.N)) ** 2 + l ** 2)

            # зачеп руки B
            if n == 1:
                hb = 0
            elif n == self.N:
                hb = 1

            # кути рахуються проти годинникової стрілки
            aa = BASE + darctan(L / l * n / self.N)
            ac = BASE - darctan(L / l * (1 - n / self.N))
            ab = ab0 + counterclockwise(abN - ab0) * n / self.N

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
            holds[hand_b] = hb
            holds[hand_c] = 1

            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            print(f"Shifts {shifts}, Angs: {angs}")
            self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, robot_head)
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def to_down(self, robot_num, hand_a, hand_b, hand_c):
        # N = 2  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0

        BASE = 270

        print(f"hand_a = {hand_a}; hand_b = {hand_b}; hand_c = {hand_c}")

        robot_head = self.robots[robot_num].hands[hand_a].ang - BASE

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # ідеальна модель з кутом А = 0
        aa0 = BASE
        ab0 = BASE + darctan(L / l)
        ac0 = BASE - darctan(L / l)
        acN = BASE + darctan(L / l)

        # рука С при русі не змінює довжини
        sa0 = l
        sb0 = sc0 = math.sqrt(L ** 2 + l ** 2)
        # TODO if not in correct position, return

        for n in range(self.N + 1):
            sa = math.sqrt((L / self.N * n) ** 2 + l ** 2)
            sb = math.sqrt((L - L / self.N * n) ** 2 + l ** 2)
            sc = sc0

            # зачеп руки С
            if n == 1:
                hc = 0
            elif n == self.N:
                hc = 1

            # кути рахуються проти годинникової стрілки
            aa = BASE - darctan(L / l * n / self.N)
            ab = BASE + darctan(L / l * (1 - n / self.N))
            ac = ac0 + clockwise(acN - ac0) * n / self.N

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
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def to_up(self, robot_num, hand_a, hand_b, hand_c):
        # N = 2  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0

        BASE = 270

        robot_head = self.robots[robot_num].hands[hand_a].ang - BASE

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # ідеальна модель з кутом А = 0
        aa0 = BASE
        ab0 = BASE + darctan(L / l)
        ac0 = BASE - darctan(L / l)
        abN = BASE - darctan(L / l)

        sa0 = l
        sb0 = sc0 = math.sqrt(L**2 + l**2)
        # TODO if not in correct position, return

        for n in range(self.N + 1):
            sa = math.sqrt((L * n / self.N) ** 2 + l ** 2)
            sb = sb0
            sc = math.sqrt((L * (1 - n / self.N)) ** 2 + l ** 2)

            # зачеп руки B
            if n == 1:
                hb = 0
            elif n == self.N:
                hb = 1

            # кути рахуються проти годинникової стрілки
            aa = BASE + darctan(L / l * n / self.N)
            ac = BASE - darctan(L / l * (1 - n / self.N))
            ab = ab0 + counterclockwise(abN - ab0) * n / self.N

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
            holds[hand_b] = hb
            holds[hand_c] = 1

            p = pack('@ffiffiffi',
                     shifts[0], angs[0], holds[0],
                     shifts[1], angs[1], holds[1],
                     shifts[2], angs[2], holds[2])
            self.robots[robot_num].isMoving = True
            self.robots[robot_num].out_buffer = p
            print(f"Shifts {shifts}, Angs: {angs}")
            self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, robot_head)
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def hu_to_L1(self, robot_num, hand_a, hand_b, hand_c):
        # N = 20  # amount of substeps

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

        for n in range(self.N + 1):
            aa = aaN * n / self.N  # 0..-45, НЕ через 180 (0..180..315)
            ac = ac0 + (acN - ac0) * n / self.N
            ab = darctan((L + l * dsin(aa)) / (l * dcos(aa)))

            sa = sa0  # не змінюється впродовж всього маневру
            sb = math.sqrt((L + l * dsin(aa)) ** 2 + (l * dcos(aa)) ** 2)  # sin(315) = sin(-45) = -sin(45)
            sc = sc0 + (scN - sc0) * n / self.N

            # ЗАЧЕП руки, що пролітає
            if n == 1:
                hc = 0
            elif n == self.N:
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
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def L1_to_Vr(self, robot_num, hand_a, hand_b, hand_c):  # перехід з L у вертикальне за часовою стрілкою
        # N = 20  # amount of substeps

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

        for n in range(self.N + 1):
            if n == 1:
                hb = 0
            elif n == self.N:
                hb = 1

            # кути рахуються ПРОТИ годинникової стрілки
            aa = aa0 + (aaN - aa0) * n / self.N  # лапа А рівномірно повертається
            ab = ab0 + (abN - ab0) * n / self.N  # лапа В рівномірно пролітає

            sa = sa0  # не змінюється впродовж всього маневру
            sb = sb0 + (sbN - sb0) * n / self.N
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
            holds[hand_b] = hb
            holds[hand_c] = 1

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
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def Vr_to_L1(self, robot_num, hand_a, hand_b, hand_c):  # перехід з вертикального у L проти часової стрілки
        # N = 20  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0
        LL = 210

        robot_head = self.robots[robot_num].hands[hand_a].ang - 270

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # Перша половина оберненого маневру - A і C у зачепах, B пролітає з нижнього у праве положення, центр зміщується на 45 градусів вліво-вверх від A
        sa0 = l
        aa0 = -90  # початковий кут лапи A = -45
        aaN = -45  # кінцевий кут лапи A = -90

        sbN = math.sqrt(l ** 2 + L ** 2 - L * l * math.sqrt(2))  # початкова довжина руки B
        sb0 = math.sqrt(l ** 2 + L ** 2)  # кінцева довжина руки B

        abN = darctan(L / l * math.sqrt(2) - 1)
        ab0 = -90 + darctan(L / l)

        sc0 = sb0  #
        scN = sbN  # під час руху її довжина змінюється пропорційно n/N

        for n in range(self.N + 1):
            if n == 1:
                hb = 0
            elif n == self.N:
                hb = 1

            # кути рахуються ПРОТИ годинникової стрілки
            aa = aa0 + (aaN - aa0) * n / self.N  # лапа А рівномірно повертається
            ab = ab0 + (abN - ab0) * n / self.N  # лапа В рівномірно пролітає

            sa = sa0  # не змінюється впродовж всього маневру
            sb = sb0 + (sbN - sb0) * n / self.N
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
            holds[hand_b] = hb
            holds[hand_c] = 1

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
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1

    def L1_to_Hu(self, robot_num, hand_a, hand_b, hand_c):  # перехід з L у горизонтальне проти часової стрілки
        # N = 20  # amount of substeps

        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0
        LL = 210

        robot_head = self.robots[robot_num].hands[hand_a].ang - 315

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        # TODO check if the robot is able to make this move
        # Друга половина оберненого маневру - A і B в зачепах, C пролітає з лівого у вертикальне положення, центр зміщується на 45 градусів вправо-вниз від A

        sa0 = l
        aa0 = -45
        aaN = 0
        scN = math.sqrt(l ** 2 + L ** 2)
        sc0 = math.sqrt(l ** 2 + L ** 2 - L * l * math.sqrt(2))
        acN = -darctan(L / l)
        ac0 = -90 - darctan(L / l * math.sqrt(2) - 1)
        sb0 = sc0
        ab0 = darctan(L / l)

        for n in range(self.N + 1):
            aa = aa0 + (aaN - aa0) * n / self.N  # 0..-45, НЕ через 180 (0..180..315)
            ac = ac0 + (acN - ac0) * n / self.N
            ab = darctan((L + l * dsin(aa)) / (l * dcos(aa)))

            sa = sa0  # не змінюється впродовж всього маневру
            sb = math.sqrt((L + l * dsin(aa)) ** 2 + (l * dcos(aa)) ** 2)  # sin(315) = sin(-45) = -sin(45)
            sc = sc0 + (scN - sc0) * n / self.N

            # ЗАЧЕП руки, що пролітає
            if n == 1:
                hc = 0
            elif n == self.N:
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
            # self.get_real_coordinates_hand(robot_num, hand_a, hand_b, hand_c, angs, robot_head)
            wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
                 waiting_for="waiting for robot to finish move")

        return 1
    '''
    # --- END OF OLD FUNCTIONS ---

    def match_IPs(self, ip):
        # перевірка наявності робота в масиві за IP
        robot_i = -1
        for i in range(len(self.robots)):
            if self.robots[i].get_ip() == ip:
                robot_i = i
        return robot_i

    # additional for get L hand letters
    def hand_in_point(self, x, y, x1, x2, y1, y2):
        # print("IN HAND IN POINT")
        # print(f"X: {x} Y: {y} | x1: {x1}; y1: {y1}; x2: {x2}; y2: {y2}")
        if (x == x1) and (y == y1):
            # print(f"X: {x} Y: {y} | 1")
            return 1
        if (x == x2) and (y == y1):
            # print(f"X: {x} Y: {y} | 2")
            return 2
        if (x == x2) and (y == y2):
            # print(f"X: {x} Y: {y} | 3")
            return 3
        if (x == x1) and (y == y2):
            # print(f"X: {x} Y: {y} | 4")
            return 4
        return -1

    # --- OLD FUNCTIONS ---
    '''
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
        # print("---------GET HAND LETTERS---------")
        print(f"CENTER x: ({center_x}, {center_y})")
        # print(
        #     f"ROBOT COORDINATES: ({self.robots[robot_num].hands[0].x}, {self.robots[robot_num].hands[0].y}) ({self.robots[robot_num].hands[1].x}, {self.robots[robot_num].hands[1].y}) ({self.robots[robot_num].hands[2].x}, {self.robots[robot_num].hands[2].y})")
        # print(
        #     f"ROBOT PARAMS: ({self.robots[robot_num].hands[0].lin}, {self.robots[robot_num].hands[0].ang}) ({self.robots[robot_num].hands[1].lin}, {self.robots[robot_num].hands[1].ang}) ({self.robots[robot_num].hands[2].lin}, {self.robots[robot_num].hands[2].ang})")

        a = -1
        b = -1
        c = -1
        # eps = 0.1
        eps = 10

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
        # print(f"bc: {bc}")
        delta_x = self.robots[robot_num].hands[a].x - center_x
        delta_y = self.robots[robot_num].hands[a].y - center_y
        # print(f"delta_x: {delta_x}")
        # print(f"delta_y: {delta_y}")
        if delta_y > 0 and abs(delta_x) <= eps:
            # print("in delta if 1")
            # min x - c
            # max x - b
            if self.robots[robot_num].hands[bc[0]].x < self.robots[robot_num].hands[bc[1]].x:
                c = bc[0]
                b = bc[1]
            else:
                c = bc[1]
                b = bc[0]
        elif delta_y < 0 and abs(delta_x) <= eps:
            # print("in delta if 2")
            # max x - c
            # min x - b
            if self.robots[robot_num].hands[bc[0]].x < self.robots[robot_num].hands[bc[1]].x:
                b = bc[0]
                c = bc[1]
            else:
                b = bc[1]
                c = bc[0]
        elif delta_x < 0 and abs(delta_y) <= eps:
            # print("in delta if 3")
            # min y - c
            # max y - b
            if self.robots[robot_num].hands[bc[0]].y < self.robots[robot_num].hands[bc[1]].y:
                c = bc[0]
                b = bc[1]
            else:
                c = bc[1]
                b = bc[0]
        elif delta_x > 0 and abs(delta_y) <= eps:
            # print("in delta if 4")
            # max y - c
            # min y - b
            if self.robots[robot_num].hands[bc[0]].y < self.robots[robot_num].hands[bc[1]].y:
                b = bc[0]
                c = bc[1]
            else:
                b = bc[1]
                c = bc[0]
        return a, b, c
    '''
    # --- END OF OLD FUNCTIONS ---

    def move_robot(self, robot_num, dest_x, dest_y):
        # determine the path to the destination
        # call corresponding functions
        # self.robots[robot_num].isMoving = True
        center_x, center_y = self.robots[robot_num].get_center()
        # print(f"c_x: {center_x}, c_y: {center_y}")
        x_path = abs(dest_x - center_x)
        y_path = abs(dest_y - center_y)
        while x_path > 0.01 or y_path > 0.01:
            if center_x == -1 or center_y == -1:
                print("Something is wrong, can't find robot center!")
                self.robots[robot_num].print()
                break
            res = self.move_step(robot_num, center_x, center_y, dest_x, dest_y)
            if res == -1:
                break
            print("========================")
            center_x, center_y = self.robots[robot_num].get_center()
            x_path = abs(dest_x - center_x)
            y_path = abs(dest_y - center_y)
            # return

    # --- OLD FUNCTIONS ---
    '''
    # MUST be in a thread, so it won't block other robots movement
    # рух робота, буде аналіз координат цілі і координат поточних, куди і як рухатись
    def move_robot_(self, robot_num, dest_x, dest_y):
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
    '''
    # --- END OF OLD FUNCTIONS ---

# --- OLD FUNCTIONS ---
'''
    def start_move(self, robot_num, dest_x, dest_y):
        # determine the path to the destination
        # call corresponding functions
        # self.robots[robot_num].isMoving = True
        print("---------START MOVE---------")
        self.align_robot_in_line(robot_num)
        self.show_ceil()
        # return
        center_x, center_y = self.robots[robot_num].get_center()
        # print(f"c_x: {center_x}, c_y: {center_y}")

        #  hand a - center hand
        #  hand b - right hand
        #  hand c - left hand
        a, b, c = self.get_hand_letters(robot_num)
        if (a == -1) or (b == -1) or (c == -1):
            print("SOMETHING IS WRONG, ABORT THE MOVE")
            return
        print(f"a = {a}; b = {b}; c = {c}")
        # print(f"a: {a}, b: {b}, c: {c}")

        delta_x = dest_x - center_x
        delta_y = dest_y - center_y
        x_path = abs(delta_x)
        y_path = abs(delta_y)
        print(f"x_path: {x_path}")
        print(f"y_path: {y_path}")
        x_move = False
        y_move = False
        if self.robots[robot_num].is_vertical_aligned():
            y_move = True
        elif self.robots[robot_num].is_horizontal_aligned():
            x_move = True
        else:
            # TODO move robot into aligned position
            pass

        while x_path > 100 or y_path > 100:
            if x_move:
                if x_path > 100:
                    print("IN X MOVE")
                    if self.robots[robot_num].is_vertical_aligned():
                        self.turn_robot_vr_to_hu(robot_num)

                    center_x, center_y = self.robots[robot_num].get_center()
                    a, b, c = self.get_hand_letters(robot_num)
                    if (a == -1) or (b == -1) or (c == -1):
                        print("SOMETHING IS WRONG, ABORT THE MOVE")
                        return

                    if dest_x > center_x:
                        # improve if robot head is not up / right
                        while x_path > 0.1 and self.robots[robot_num].hands[c].x + 3 * 200 < ceil_to_coordinates(
                                self.max_x):
                            self.to_right(robot_num, a, b, c)
                            self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x + 3 * 200,
                                           self.robots[robot_num].hands[c].y)
                            center_x, center_y = self.robots[robot_num].get_center()
                            a, b, c = self.get_hand_letters(robot_num)
                            if (a == -1) or (b == -1) or (c == -1):
                                print("SOMETHING IS WRONG, ABORT THE MOVE")
                                return
                            delta_x = dest_x - center_x
                            delta_y = dest_y - center_y
                            x_path = abs(delta_x)
                            y_path = abs(delta_y)
                    if dest_x < center_x:
                        while x_path > 0.1 and self.robots[robot_num].hands[b].x - 3 * 200 >= 0:
                            self.to_left(robot_num, a, b, c)
                            self.move_hand(robot_num, b, self.robots[robot_num].hands[b].x - 3 * 200,
                                           self.robots[robot_num].hands[b].y)
                            center_x, center_y = self.robots[robot_num].get_center()
                            a, b, c = self.get_hand_letters(robot_num)
                            if (a == -1) or (b == -1) or (c == -1):
                                print("SOMETHING IS WRONG, ABORT THE MOVE")
                                return
                            delta_x = dest_x - center_x
                            delta_y = dest_y - center_y
                            x_path = abs(delta_x)
                            y_path = abs(delta_y)
                x_move = False
                y_move = True
            if y_move:
                if y_path > 100:
                    print("IN Y MOVE")
                    if self.robots[robot_num].is_horizontal_aligned():
                        self.turn_robot_hu_to_vr(robot_num)

                    center_x, center_y = self.robots[robot_num].get_center()
                    a, b, c = self.get_hand_letters(robot_num)
                    if (a == -1) or (b == -1) or (c == -1):
                        print("SOMETHING IS WRONG, ABORT THE MOVE")
                        return
                    if dest_y > center_y:
                        # improve if robot head is not up / right
                        while y_path > 0.1 and self.robots[robot_num].hands[c].y + 3 * 200 < ceil_to_coordinates(
                                self.max_y):
                            print("IN Y LOOP")
                            print(self.robots[robot_num].get_real_coordinates())
                            self.to_down(robot_num, a, b, c)
                            self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x,
                                           self.robots[robot_num].hands[c].y + 3 * 200,
                                           )
                            self.show_ceil()
                            center_x, center_y = self.robots[robot_num].get_center()
                            a, b, c = self.get_hand_letters(robot_num)
                            if (a == -1) or (b == -1) or (c == -1):
                                print("SOMETHING IS WRONG, ABORT THE MOVE")
                                return
                            delta_x = dest_x - center_x
                            delta_y = dest_y - center_y
                            x_path = abs(delta_x)
                            y_path = abs(delta_y)
                    if dest_y < center_y:
                        while y_path > 0.1 and self.robots[robot_num].hands[b].y - 3 * 200 >= 0:
                            self.to_up(robot_num, a, b, c)
                            self.move_hand(robot_num, b, self.robots[robot_num].hands[c].x,
                                           self.robots[robot_num].hands[b].y - 3 * 200
                                           )
                            self.show_ceil()
                            center_x, center_y = self.robots[robot_num].get_center()
                            a, b, c = self.get_hand_letters(robot_num)
                            if (a == -1) or (b == -1) or (c == -1):
                                print("SOMETHING IS WRONG, ABORT THE MOVE")
                                return
                            delta_x = dest_x - center_x
                            delta_y = dest_y - center_y
                            x_path = abs(delta_x)
                            y_path = abs(delta_y)
                x_move = True
                y_move = False'''


'''        while x_path > 100:# or y_path > 100:
            self.show_ceil()
            if x_path > 100:
                print("IN X MOVE")
                if self.robots[robot_num].is_vertical_aligned():
                    self.turn_robot_vr_to_hu(robot_num)
                    # self.show_ceil()

                if dest_x > center_x:
                    # improve
                    while x_path > 0.1 and self.robots[robot_num].hands[c].x + 3 * 200 < ceil_to_coordinates(
                            self.max_x):
                        # print("IN X MOVE")
                        # self.move_forward(robot_num, a, b, c)
                        self.to_right(robot_num, a, b, c)
                        # new_x = ceil_to_coordinates(self.robots[robot_num].hands[c].x+3*200)
                        # print(f"c x: {self.robots[robot_num].hands[c].x} NEW c x: {self.robots[robot_num].hands[c].x + 3 * 200}")
                        self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x + 3 * 200,
                                       self.robots[robot_num].hands[c].y)
                        # self.show_ceil()
                        center_x, center_y = self.robots[robot_num].get_center()
                        a, b, c = self.get_hand_letters(robot_num)
                        if (a == -1) or (b == -1) or (c == -1):
                            print("SOMETHING IS WRONG, ABORT THE MOVE")
                            return
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
                        # self.show_ceil()
                        center_x, center_y = self.robots[robot_num].get_center()
                        a, b, c = self.get_hand_letters(robot_num)
                        if (a == -1) or (b == -1) or (c == -1):
                            print("SOMETHING IS WRONG, ABORT THE MOVE")
                            return
                        # print(f"a: {a}, b: {b}, c: {c}")
                        # print(f"a: {a}, b: {b}, c: {c}")
                        delta_x = dest_x - center_x
                        delta_y = dest_y - center_y
                        x_path = abs(delta_x)
                        # print(f"x_path: {x_path}")
                        y_path = abs(delta_y)
            # if y_path > 100:
            #     if self.robots[robot_num].is_horizontal_aligned():
            #         self.turn_robot(robot_num)
            #     # move
            #     pass
        while y_path > 100:
            self.show_ceil()
            print("IN Y MOVE")
            if self.robots[robot_num].is_horizontal_aligned():
                self.turn_robot_hu_to_vr(robot_num)
                # self.show_ceil()

            # print("ROBOT TURN")
            center_x, center_y = self.robots[robot_num].get_center()
            a, b, c = self.get_hand_letters(robot_num)
            if (a == -1) or (b == -1) or (c == -1):
                print("SOMETHING IS WRONG, ABORT THE MOVE")
                return
            if dest_y > center_y:
                # print("IN Y IF")
                # improve
                while y_path > 0.1 and self.robots[robot_num].hands[c].y + 3 * 200 < ceil_to_coordinates(self.max_y):
                    print("IN Y LOOP")
                    print(self.robots[robot_num].get_real_coordinates())
                    # self.move_forward(robot_num, a, b, c)
                    # print("BEFORE TO_RIGHT")
                    self.to_down(robot_num, a, b, c)
                    # print("AFTER TO_RIGHT")
                    # new_x = ceil_to_coordinates(self.robots[robot_num].hands[c].x+3*200)
                    self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x,
                                   self.robots[robot_num].hands[c].y + 3 * 200,
                                   )
                    self.show_ceil()
                    center_x, center_y = self.robots[robot_num].get_center()
                    a, b, c = self.get_hand_letters(robot_num)
                    if (a == -1) or (b == -1) or (c == -1):
                        print("SOMETHING IS WRONG, ABORT THE MOVE")
                        return
                    # print(f"a: {a}, b: {b}, c: {c}")
                    delta_x = dest_x - center_x
                    delta_y = dest_y - center_y
                    x_path = abs(delta_x)
                    # print(f"x_path: {x_path}")
                    y_path = abs(delta_y)
            if dest_y < center_y:
                while y_path > 0.1 and self.robots[robot_num].hands[b].y - 3 * 200 >= 0:
                    self.to_up(robot_num, a, b, c)
                    self.move_hand(robot_num, b, self.robots[robot_num].hands[c].x,
                                   self.robots[robot_num].hands[b].y - 3 * 200
                                   )
                    self.show_ceil()
                    center_x, center_y = self.robots[robot_num].get_center()
                    a, b, c = self.get_hand_letters(robot_num)
                    if (a == -1) or (b == -1) or (c == -1):
                        print("SOMETHING IS WRONG, ABORT THE MOVE")
                        return
                    # print(f"a: {a}, b: {b}, c: {c}")
                    # print(f"a: {a}, b: {b}, c: {c}")
                    delta_x = dest_x - center_x
                    delta_y = dest_y - center_y
                    x_path = abs(delta_x)
                    # print(f"x_path: {x_path}")
                    y_path = abs(delta_y)'''
# --- END OF OLD FUNCTIONS ---

# --- OLD FUNCTIONS ---
'''
    def turn_robot_hu_to_vr(self, robot_num):
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
        self.move_hand(robot_num, b, self.robots[robot_num].hands[b].x - 1 * 200,
                       self.robots[robot_num].hands[b].y + 1 * 200)
        self.show_ceil()


        # res = self.move_forward(robot_num, 1, 2, 0)
        # if res == -1:
        #     print("oups")
        #     return -1
        # self.move_hand(robot_num, 0, self.robots[robot_num].hands[0].x + 3, self.robots[robot_num].hands[0].y)
        # return 1

    def turn_robot_vr_to_hu(self, robot_num):
        center_x, center_y = self.robots[robot_num].get_center()
        # print(f"c_x: {center_x}, c_y: {center_y}")

        #  hand a - center hand
        #  hand b - right hand
        #  hand c - left hand
        a, b, c = self.get_hand_letters(robot_num)

        self.Vr_to_L1(robot_num, a, b, c)
        self.move_hand(robot_num, b, self.robots[robot_num].hands[b].x + 1 * 200,
                       self.robots[robot_num].hands[b].y - 1 * 200)
        self.show_ceil()
        center_x, center_y = self.robots[robot_num].get_center()
        a, b, c = self.get_hand_letters(robot_num)
        self.L1_to_Hu(robot_num, a, b, c)
        self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x - 1 * 200,
                       self.robots[robot_num].hands[c].y + 1 * 200)
        self.show_ceil()

    def align_robot_in_line(self, robot_num):
        if not (self.robots[robot_num].is_horizontal_aligned() or self.robots[robot_num].is_vertical_aligned()):
            # TODO check if L position and nothing else
            a, b, c = self.get_L_hand_letters(robot_num)
            if self.is_point_free(robot_num,
                                  self.robots[robot_num].hands[c].x - 1 * 200,
                                  self.robots[robot_num].hands[c].y + 1 * 200):
                self.L1_to_Hu(robot_num, a, b, c)
                self.move_hand(robot_num, c, self.robots[robot_num].hands[c].x - 1 * 200,
                               self.robots[robot_num].hands[c].y + 1 * 200)
            elif self.is_point_free(robot_num,
                                    self.robots[robot_num].hands[b].x - 1 * 200,
                                    self.robots[robot_num].hands[b].y + 1 * 200):
                self.L1_to_Vr(robot_num, a, b, c)
                self.move_hand(robot_num, b, self.robots[robot_num].hands[b].x - 1 * 200,
                               self.robots[robot_num].hands[b].y + 1 * 200)
            self.show_ceil()
        # align the robot
        a, b, c = self.get_hand_letters(robot_num)
        self.align(robot_num, a, b, c)

    def align(self, robot_num, hand_a, hand_b, hand_c):
        # Параметри рук
        l = 48
        L = size["netStep"]  # 200.0

        BASE = 0 # TODO

        print(f"hand_a = {hand_a}; hand_b = {hand_b}; hand_c = {hand_c}")

        robot_head = self.robots[robot_num].hands[hand_a].ang - BASE

        ha = self.robots[robot_num].hands[hand_a].hold
        hb = self.robots[robot_num].hands[hand_b].hold
        hc = self.robots[robot_num].hands[hand_c].hold

        sa = l
        sb = sc = math.sqrt(L ** 2 + l ** 2)

        # кути рахуються проти годинникової стрілки
        aa = BASE
        ab = BASE + darctan(L / l)
        ac = BASE - darctan(L / l)

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
        holds[hand_c] = 1

        p = pack('@ffiffiffi',
                 shifts[0], angs[0], holds[0],
                 shifts[1], angs[1], holds[1],
                 shifts[2], angs[2], holds[2])
        self.robots[robot_num].isMoving = True
        self.robots[robot_num].out_buffer = p
        print(f"Shifts {shifts}, Angs: {angs}")
        self.get_real_coordinates(robot_num, hand_a, hand_b, hand_c, shifts, angs, robot_head)
        wait(lambda: self.robots[robot_num].is_finished_move(), timeout_seconds=120,
             waiting_for="waiting for robot to finish move")

        return 1
'''
# --- END OF OLD FUNCTIONS ---
