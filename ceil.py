# import math
# import select
# import sys
# import time
import time
from struct import pack
from waiting import wait

# import arm_geometry_test
# from arm_geometry_test import *
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

        self.coef = 1.07

    # додавання роботу
    def add_robot(self, ip):
        """

        :param ip: IP address of the robot
        :return:
        """
        r = Robot()
        r.set_ip(ip)
        # set default coordinates
        r.set_coordinates(self.default_coordinates["x1"], self.default_coordinates["y1"],
                          self.default_coordinates["x2"], self.default_coordinates["y2"],
                          self.default_coordinates["x3"], self.default_coordinates["y3"])

        y1 =  int((self.default_coordinates["y1"] - 100) / 200)
        x1 = int((self.default_coordinates["x1"] - 100) / 200)
        y2 = int((self.default_coordinates["y2"] - 100) / 200)
        x2 = int((self.default_coordinates["x2"] - 100) / 200)
        y3 = int((self.default_coordinates["y3"] - 100) / 200)
        x3 = int((self.default_coordinates["x3"] - 100) / 200)

        # mark default coordinates as occupied in ceil array
        self.ceil_arr[y1][x1] = 1
        self.ceil_arr[y2][x2] = 1
        self.ceil_arr[y3][x3] = 1

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
        ceil_x, ceil_y = coordinates_to_ceil(x, y)
        # print(f"CEIL x: {ceil_x}, y: {ceil_y}")
        if self.ceil_arr[ceil_y][ceil_x] == 0:
            old_x, old_y = coordinates_to_ceil(self.robots[robot_num].hands[hand_num].x,
                                               self.robots[robot_num].hands[hand_num].y)
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
        # print(f"Angle A: {ang_0}")
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

        # print(f"GET VECTOR ABS a: {a}, x0: {x0}, y0: {y0}")

        # base vector is vertical vector from which the angles and offset will be counted
        base_vector_x = 0
        base_vector_y = -5

        base_to_0 = angle_between_vectors(base_vector_x, base_vector_y, x0, y0)
        shift = normalize(ang_0 - base_to_0)
        # shift = 4
        # print(f"BASE TO A: {base_to_0} SHIFT: {shift}")

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

        # print(f"GET NEW VECTOR COORDS a: ({new_x0}, {new_y0}) b: ({new_x1}, {new_y1}) c: ({new_x2}, {new_y2})")

        new_0 = get_abs_vector(new_x0, new_y0)
        new_1 = get_abs_vector(new_x1, new_y1)
        new_2 = get_abs_vector(new_x2, new_y2)

        # print(f"GET NEW VECTOR ABS a: {new_0} b: {new_1} c: {new_2}")

        '''new_ang_a = angle_between_vectors(x_head, y_head, new_xa, new_ya)
        new_ang_b = angle_between_vectors(x_head, y_head, new_xb, new_yb)
        new_ang_c = angle_between_vectors(x_head, y_head, new_xc, new_yc)'''

        new_ang_0 = angle_between_vectors(base_vector_x, base_vector_y, new_x0, new_y0)
        new_ang_1 = angle_between_vectors(base_vector_x, base_vector_y, new_x1, new_y1)
        new_ang_2 = angle_between_vectors(base_vector_x, base_vector_y, new_x2, new_y2)

        # print(f"ANGS BEFORE SHIFT a: {new_ang_0} b: {new_ang_1} c: {new_ang_2}")

        new_ang_0 = normalize(new_ang_0 + shift)
        new_ang_1 = normalize(new_ang_1 + shift)
        new_ang_2 = normalize(new_ang_2 + shift)

        # print(f"GET ANGS a: {new_ang_0} b: {new_ang_1} c: {new_ang_2}")

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
            print("---------")
            # print(f"s X: {xo_s} Y: {yo_s}")
            print(f"n X: {xo_n} Y: {yo_n}")
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
            # print(f"Coords: {hand_coords}; Conditions are: pose: {is_possible}, move: {is_move_possible}, mirroring: {is_correct_hand_order}")
            if not is_possible or not is_move_possible or not is_correct_hand_order:
                return False
            return True
        return False

    # finds the center for the robot; TODO change brute force search to smth more effective
    def find_pos_by_shifts(self, robot_num, xo_s, yo_s, hand_coords, start_shifts, hand_c = -1):
        """
        The function is searching for an available center coordinates to move to by checking shifts from
        start_shifts - size["innerRadLimit"] to start_shifts + size["innerRadLimit"]

        :param robot_num: robot number
        :param xo_s: X coordinate of Os
        :param yo_s: Y coordinate of Os
        :param hand_coords: coordinates of robot holders
        :param start_shifts: start shifts of robot
        :param hand_c: hand that will move from one coordinate to another during this movement
        :return: new coordinates for the robot
        """
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
                    # print(f"Searching pos, {shift_1}; {shift_2}; {shift_3}")
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

    def check_clockwise(self, robot_num, xo_s, yo_s, xo_t, yo_t, hand_coords, old_shift, old_ang, new_shift, new_ang, move_hand):
        N = 10
        # print(f"IN FUNC N = {N}; move_hand is {move_hand}; old_shift: {old_shift}, old_ang: {old_ang};"
        #       f"new_shift: {new_shift}, new_ang: {new_ang}")
        hands = [0, 1, 2]
        hands.remove(move_hand)
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
            delta_shift = (new_shift - old_shift) / N

            if move_hand != -1 and n < N:
                # print(f"Hold 0: {n}")
                holds[move_hand] = 0
                shifts[move_hand] = old_shift + delta_shift * n
                angs[move_hand] = normalize(old_ang + clockwise(new_ang - old_ang) * n / N)
            # print(f"n = {n}, shifts: {shifts}; angs: {angs}")

            mirror = mirroring_check(angs[0], angs[1], angs[2])
            in_reach_zone = is_in_two_hands_area(hand_coords[hands[0]][0], hand_coords[hands[0]][1],
                                                 hand_coords[hands[1]][0], hand_coords[hands[1]][1],
                                                 xo_n, yo_n)
            if not mirror or not in_reach_zone:
                # print("mirror false")
                return False
            # else:
                # print("mirror true")
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
        # print(f"t_shifts: {t_shifts}; t_angs: {t_angs}")
        delta_ang = -1.0
        delta_shift = -1
        old_ang = -1.0
        old_shift = -1
        is_clockwise = -1

        print(f"move hand: {move_hand}")

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
                                                t_shifts[move_hand], t_angs[move_hand], move_hand)
        # print(f"move_hand is {move_hand}; old_shift: {old_shift}, old_ang: {old_ang}; delta_shift: {delta_shift}, delta_ang: {delta_ang}")

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
            # print(f"n = {n}; N = {self.N}")
            # print(f"t_ang: {t_angs[move_hand]}, t_shift: {t_shifts[move_hand]}")

            # print(f"1 Shifts {shifts}, Angs: {angs}")
            if move_hand != -1 and n < self.N:
                # print(f"Hold 0: {n}")
                holds[move_hand] = 0
                shifts[move_hand] = old_shift + delta_shift * n
                if is_clockwise:
                    # print("clockwise")
                    # print(f"delta: {(t_angs[move_hand] - old_ang) / self.N}")
                    # print(f"clockwise: {clockwise(t_angs[move_hand] - old_ang)}")
                    # print(f"old_ang: {old_ang}")
                    # print(f"new ang: {old_ang + clockwise(t_angs[move_hand] - old_ang) * n / self.N}")
                    angs[move_hand] = normalize(old_ang + clockwise(t_angs[move_hand] - old_ang) * n / self.N)
                else:
                    # print("counterclockwise")
                    # print(f"delta: {(t_angs[move_hand] - old_ang) / self.N}")
                    # print(f"counterclockwise: {counterclockwise(t_angs[move_hand] - old_ang) * n / self.N}")
                    # print(f"old_ang: {old_ang}")
                    # print(f"new ang: {old_ang + counterclockwise(t_angs[move_hand] - old_ang) * n / self.N}")
                    angs[move_hand] = normalize(old_ang + counterclockwise(t_angs[move_hand] - old_ang) * n / self.N)

            mirror = mirroring_check(angs[0], angs[1], angs[2])
            # print(f"2 Shifts {shifts}, Angs: {angs}")
            if not mirror:
                print("Critical error with angles, abort!")
                return -1

            # time.sleep(2)

            if sum(holds) < 2:
                print("Tried to unhold more than two hands, abort the move")
                return -1

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
            if self.robots[robot_num].hands[0].hold != holds[0] or self.robots[robot_num].hands[1].hold != holds[1] or \
                self.robots[robot_num].hands[2].hold != holds[2]:
                print("Something is wrong with holders, abort!")
                return -1
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

        min_x, min_y = coordinates_to_ceil(
            min(hand_coords[0][0], hand_coords[1][0], hand_coords[2][0]) - 2 * size["outerRadLimit"],
            min(hand_coords[0][1], hand_coords[1][1], hand_coords[2][1]) - 2 * size["outerRadLimit"])
        max_x, max_y = coordinates_to_ceil(
            max(hand_coords[0][0], hand_coords[1][0], hand_coords[2][0]) + 2 * size["outerRadLimit"],
            max(hand_coords[0][1], hand_coords[1][1], hand_coords[2][1]) + 2 * size["outerRadLimit"])

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

                    is_line_L = is_aligned_stable(temp_hand_coords)
                    if not is_line_L:
                        continue

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
        if is_aligned(temp_hand_coords) and is_aligned_stable(hand_coords):
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
        # if is_correct_hand_order:
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
        self.robots[robot_num].isMovingPath = True
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
            self.robots[robot_num].isMovingPath = False
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

        center_x, center_y = center_by_params(hand_coords, robot_shifts[0], robot_shifts[1], robot_shifts[2])

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
                    # centers_for_hand_moves = [(-1, -1), (-1, -1), (-1, -1)]
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
                                # centers_for_hand_moves[j] = (new_x, new_y)
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
        self.robots[robot_num].isMovingPath = False

    def check_if_ot_possible(self, xo_t, yo_t):
        """
        :param xo_t: X coordinate of Ot
        :param yo_t: Y coordinate of Ot
        :return: True if robot is able to position himself for Ot, False otherwise
        """
        # min and max x and y for potentially available holes
        min_x = max(math.floor((((xo_t - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        max_x = max(math.floor((((xo_t + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        min_y = max(math.floor((((yo_t - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        max_y = max(math.floor((((yo_t + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)

        print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

        available_points = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                # print("---")
                # print(f"IN LOOP x: {x}, y: {y}")
                x_ceil = ceil_to_coordinates(x)
                y_ceil = ceil_to_coordinates(y)
                # print(f"TRUE COORDS x: {x_ceil}, y: {y_ceil}")
                # check if the point is inside the circle
                if (x_ceil - xo_t) ** 2 + (-y_ceil + yo_t) ** 2 <= size["outerRadLimit"] ** 2:
                    available_points.append((x_ceil, y_ceil))
        for p1 in available_points:
            for p2 in available_points:
                if p2[0] == p1[0] and p2[1] == p1[1]:
                    continue
                for p3 in available_points:
                    if p3[0] == p2[0] and p3[1] == p2[1]:
                        continue
                    is_pos_possible = is_in_three_hands_area(p1[0], p1[1],
                                                             p2[0], p2[1],
                                                             p3[0], p3[1],
                                                             xo_t, yo_t)
                    if is_pos_possible:
                        return True
        return False

    def find_ot_possible(self, xo_t, yo_t):
        """
        :param xo_t: X coordinate of Ot
        :param yo_t: Y coordinate of Ot
        :return: new Ot coordinates
        """
        # min and max x and y for potentially available holes
        min_x = max(math.floor((((xo_t - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        max_x = max(math.floor((((xo_t + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        min_y = max(math.floor((((yo_t - size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)
        max_y = max(math.floor((((yo_t + size["outerRadLimit"]) - size["netBorder"]) / size["netStep"])), 0)

        print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

        available_points = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                # print("---")
                # print(f"IN LOOP x: {x}, y: {y}")
                x_ceil = ceil_to_coordinates(x)
                y_ceil = ceil_to_coordinates(y)
                # print(f"TRUE COORDS x: {x_ceil}, y: {y_ceil}")
                # check if the point is inside the circle
                if (x_ceil - xo_t) ** 2 + (-y_ceil + yo_t) ** 2 <= size["outerRadLimit"] ** 2:
                    available_points.append((x_ceil, y_ceil))
        for p1 in available_points:
            for p2 in available_points:
                if p2[0] == p1[0] and p2[1] == p1[1]:
                    continue
                for p3 in available_points:
                    if p3[0] == p2[0] and p3[1] == p2[1]:
                        continue
                    '''is_pos_possible = is_in_three_hands_area(p1[0], p1[1],
                                                             p2[0], p2[1],
                                                             p3[0], p3[1],
                                                             xo_t, yo_t)
                    if is_pos_possible:
                        return True'''
        return False

    def build_path_lines(self, robot_num, xo_s, yo_s, xo_t, yo_t):
        is_ot_possible = self.check_if_ot_possible(xo_t, yo_t)

        self.robots[robot_num].isMovingPath = True
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
            self.robots[robot_num].isMovingPath = False
            return

        robot_shifts = [self.robots[robot_num].hands[0].lin,
                        self.robots[robot_num].hands[1].lin,
                        self.robots[robot_num].hands[2].lin]
        robot_angs = [self.robots[robot_num].hands[0].ang,
                      self.robots[robot_num].hands[1].ang,
                      self.robots[robot_num].hands[2].ang]

        center_x, center_y = center_by_params(hand_coords, robot_shifts[0], robot_shifts[1], robot_shifts[2])

        # TODO protect from dead-end positions
        move_finished = False
        counter = -1
        while not move_finished and counter <= 2000:
            print(f"Is move finished? {move_finished}")
            print(f"Path in loop: {path}")
            counter += 1
            pos_conditions = self.check_conditions_pos(robot_num, xo_t, yo_t, center_x, center_y, hand_coords)
            current_dist = dist(center_x, center_y, xo_t, yo_t)
            if pos_conditions:
                # the point Ot is within robot's reach, no need to move hands or adjust position
                print("move possible")
                path.append(hand_coords)
                centers.append((xo_t, yo_t))
                move_finished = True
            elif current_dist <= 0.5 * size["netStep"]:
                move_finished = True
                # print("IN ADDITIONAL CONDITION")
                # pos_conditions = self.check_conditions_pos(robot_num, xo_t, yo_t, center_x, center_y, hand_coords)
                # if pos_conditions:
                #     # the point Ot is within robot's reach, no need to move hands or adjust position
                #     print("move possible")
                #     path.append(hand_coords)
                #     centers.append((xo_t, yo_t))
            else:
                # TODO check if we can move ONE hand to get the needed position
                neighbours = self.get_neighbours(hand_coords)
                sorted_neighbours = sorted(neighbours, key=lambda p: dist(p[0], p[1], xo_t, yo_t))
                print(f"Sorted neighbours: {sorted_neighbours}")

                potential_pos = self.adjust_robot(robot_num, center_x, center_y, xo_t, yo_t, hand_coords)
                print(f"Potential pos: {potential_pos}")
                # if potential_pos[0][0] != -1:
                #     path.append(potential_pos)
                #     centers.append((xo_t, yo_t))
                #     move_finished = True
                #     print("Move finished!")
                #     break
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
                    # centers_for_hand_moves = [(-1, -1), (-1, -1), (-1, -1)]
                    for j in range(3):
                        # print(f"IN LOOP Hand coords: {hand_coords}")
                        temp_coords = hand_coords[:]
                        temp_coords[j] = point
                        print("---")
                        print(f"IN LOOP Temp coords: {temp_coords}")
                        new_x, new_y = self.check_point(robot_num, temp_coords, j, center_x, center_y, point, opt_points)
                        is_line_L = is_aligned_stable(temp_coords)
                        is_close = dist(center_x, center_y, xo_t, yo_t) < 0.5 * size["netStep"]
                        print(f"Hand {j}: ({new_x}, {new_y}); is stable? {is_line_L}")
                        # print(f"Temp coords: {temp_hand_coords}")
                        # print(f"Loop optimal: {opt_points}")
                        if (new_x != -1 and new_y != -1) and is_line_L:
                            print(f"ADDING {point} FOR {j}")
                            if temp_coords in path:
                                print("There is already such position in path, aborting the loop!")
                                temp_coords = hand_coords[:]
                                # move_finished = True
                                # print(f"Is move finished? (pos exist): {move_finished}")
                                # break
                            else:
                                print(f"Adding the position: {temp_coords}")
                                # centers_for_hand_moves[j] = (new_x, new_y)
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
        self.robots[robot_num].isMovingPath = False

    def build_path_lines_2(self, robot_num, xo_s, yo_s, xo_t, yo_t):
        is_ot_possible = self.check_if_ot_possible(xo_t, yo_t)

        self.robots[robot_num].isMovingPath = True
        self.robots[robot_num].curr_index = -1
        a, b, c = get_line_equation(xo_s, yo_s, xo_t, yo_t)
        opt_points = optimal_points(a, b, c)
        self.robots[robot_num].opt_points = opt_points[:]
        # print(f"Start optimal: {opt_points}")

        # since we are not actually moving robot yet, we need to store it's params for position evaluation
        hand_coords = [(self.robots[robot_num].hands[0].x, self.robots[robot_num].hands[0].y),
                       (self.robots[robot_num].hands[1].x, self.robots[robot_num].hands[1].y),
                       (self.robots[robot_num].hands[2].x, self.robots[robot_num].hands[2].y)]

        start = time.time()
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
            self.robots[robot_num].isMovingPath = False
            return

        robot_shifts = [self.robots[robot_num].hands[0].lin,
                        self.robots[robot_num].hands[1].lin,
                        self.robots[robot_num].hands[2].lin]
        robot_angs = [self.robots[robot_num].hands[0].ang,
                      self.robots[robot_num].hands[1].ang,
                      self.robots[robot_num].hands[2].ang]

        center_x, center_y = center_by_params(hand_coords, robot_shifts[0], robot_shifts[1], robot_shifts[2])

        # TODO protect from dead-end positions
        move_finished = False
        counter = -1
        while not move_finished and counter <= 2000:
            print(f"Is move finished? {move_finished}")
            print(f"Path in loop: {path}")
            counter += 1
            pos_conditions = self.check_conditions_pos(robot_num, xo_t, yo_t, center_x, center_y, hand_coords)
            current_dist = dist(center_x, center_y, xo_t, yo_t)
            if pos_conditions:
                # the point Ot is within robot's reach, no need to move hands or adjust position
                print("move possible")
                path.append(hand_coords)
                centers.append((xo_t, yo_t))
                move_finished = True
            elif current_dist <= 0.5 * size["netStep"]:
                move_finished = True
            else:
                # TODO check if we can move ONE hand to get the needed position
                neighbours = self.get_neighbours(hand_coords)
                sorted_neighbours = sorted(neighbours, key=lambda p: dist(p[0], p[1], xo_t, yo_t))
                print(f"Sorted neighbours: {sorted_neighbours}")

                # potential_pos = self.adjust_robot(robot_num, center_x, center_y, xo_t, yo_t, hand_coords)
                # print(f"Potential pos: {potential_pos}")
                # if potential_pos[0][0] != -1:
                #     path.append(potential_pos)
                #     centers.append((xo_t, yo_t))
                #     move_finished = True
                #     print("Move finished!")
                #     break
                    # continue
                # print(f"Move finished? {move_finished}")

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
                    # centers_for_hand_moves = [(-1, -1), (-1, -1), (-1, -1)]
                    for j in range(3):
                        # print(f"IN LOOP Hand coords: {hand_coords}")
                        temp_coords = hand_coords[:]
                        temp_coords[j] = point
                        print("---")
                        print(f"IN LOOP Temp coords: {temp_coords}")
                        new_x, new_y = self.check_point(robot_num, temp_coords, j, center_x, center_y, point, opt_points)
                        is_line_L = is_aligned_stable(temp_coords)
                        is_close = dist(center_x, center_y, xo_t, yo_t) < 0.5 * size["netStep"]
                        print(f"Hand {j}: ({new_x}, {new_y}); is stable? {is_line_L}")
                        # print(f"Temp coords: {temp_hand_coords}")
                        # print(f"Loop optimal: {opt_points}")
                        if (new_x != -1 and new_y != -1) and is_line_L:
                            print(f"ADDING {point} FOR {j}")
                            if temp_coords in path:
                                print("There is already such position in path, aborting the loop!")
                                temp_coords = hand_coords[:]
                                # move_finished = True
                                # print(f"Is move finished? (pos exist): {move_finished}")
                                # break
                            else:
                                print(f"Adding the position: {temp_coords}")
                                # centers_for_hand_moves[j] = (new_x, new_y)
                                move_hand_prev = -1
                                move_hand_now = -1
                                if len(path) >= 2:
                                    for j in range(3):
                                        if (path[len(path) - 2][j][0] != path[len(path) - 1][j][0] or
                                                path[len(path) - 2][j][1] != path[len(path) - 1][j][1]):
                                            if move_hand_prev != -1:
                                                print("Need to move two hands at the same time, impossible!")
                                                return -1
                                            else:
                                                move_hand_prev = j
                                    for j in range(3):
                                        if (path[len(path) - 1][j][0] != temp_coords[j][0] or
                                                path[len(path) - 1][j][1] != temp_coords[j][1]):
                                            if move_hand_now != -1:
                                                print("Need to move two hands at the same time, impossible!")
                                                return -1
                                            else:
                                                move_hand_now = j

                                print(f"Move hand prev: {move_hand_prev} and now: {move_hand_now}")
                                if move_hand_prev == move_hand_now and move_hand_now != -1:
                                    print("Pop the last pos")
                                    last = len(path) - 1
                                    path.pop(last)
                                    centers.pop(last)

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

        end = time.time()
        print(f"Time for path building: {end - start}")
        print(f"AFTER Is move finished? {move_finished}")
        self.robots[robot_num].path = path[:]
        self.robots[robot_num].centers = centers[:]
        print(path)
        print(centers)
        self.robots[robot_num].isMovingPath = False

    def get_allowed_poses(self, robot_num, xo=-1, yo=-1, x_center_hand=-1, y_center_hand=-1):
        if x_center_hand == -1:
            hand_coords = self.robots[robot_num].get_all_points()
            middle = middle_point((hand_coords[0][0], hand_coords[0][1]),
                                  (hand_coords[1][0], hand_coords[1][1]),
                                  (hand_coords[2][0], hand_coords[2][1]))
            xo = hand_coords[3][0]
            yo = hand_coords[3][1]
            x_center_hand = hand_coords[middle][0]
            y_center_hand = hand_coords[middle][1]
        x, y = x_center_hand, y_center_hand
        allowed_positions = [[(x - size["netStep"], y), (x, y), (x + size["netStep"], y)],
                             # horizontal
                             [(x, y - size["netStep"]), (x, y), (x, y + size["netStep"])]]  # vertical
        print(f"allowed_positions:\n{allowed_positions[0]}\n{allowed_positions[1]}")
        return allowed_positions

    def current_pos(self, robot_num, points):
        current_pose = -1  # 0 - horizontal, 1 - vertical, 2 - unaligned, needs improving
        Tol = 2
        # print(f"Points: {points}")
        # print(f"difs: {abs(points[1][0] - (points[0][0] + size['d2'] / 2)) < Tol} {abs(points[1][0] - (points[2][0] - size['d2'] / 2)) < Tol} {abs(points[1][1] - (points[0][1] + size['D2'] / 4)) < Tol} {abs(points[1][1] - (points[2][1] - size['D2'] / 4)) < Tol}")
        # print(f'Condition: {(abs(points[1][0] - (points[0][0] + size["d2"]) / 2) < Tol) and (abs(points[1][0] - (points[2][0] - size["d2"] / 2)) < Tol) and (abs(points[1][1] - (points[0][1] + size["D2"] / 4)) < Tol) and (abs(points[1][1] - (points[2][1] - size["D2"] / 4)) < Tol)}')

        if (abs(points[1][0] - (points[0][0] + size["netStep"])) < Tol) and (
                abs(points[1][0] - (points[2][0] - size["netStep"])) < Tol) and (
                abs(points[1][1] - points[0][1]) < Tol) and (
                abs(points[1][1] - points[2][1]) < Tol):
            print("0")
            current_pose = 0  # 0 - horizontal

        elif (abs(points[1][0] - points[0][0]) < Tol) and (
                abs(points[1][0] - points[2][0]) < Tol) and (
                abs(points[1][1] - (points[0][1] + size["netStep"])) < Tol) and (
                abs(points[1][1] - (points[2][1] - size["netStep"])) < Tol):
            print("1")
            current_pose = 1  # 1 - vertical
        else:
            print("2")
            current_pose = 2  # 2 - unaligned, needs improving
        return current_pose

    def align_to_allowed(self, robot_num):
        # hand_coords = self.robots[robot_num].get_all_points()
        # print(f"Hand coords: {hand_coords}")
        # x1, y1 = (hand_coords[0][0], hand_coords[0][1])
        # x2, y2 = (hand_coords[1][0], hand_coords[1][1])
        # x3, y3 = (hand_coords[2][0], hand_coords[2][1])
        # points = [(float("%.4f" % x1), float("%.4f" % y1)),
        #           (float("%.4f" % x2), float("%.4f" % y2)),
        #           (float("%.4f" % x3), float("%.4f" % y3))]
        # # points = [(x1, y1),
        # #           (x2, y2),
        # #           (x3, y3)]
        # points.sort(key=lambda point: (point[0], point[1]))
        # allowed_poses = self.get_allowed_poses(robot_num)
        # for pose in allowed_poses:
        #     pass
        pass

    def turn_clock(self, robot_num, clockwise=True):
        self.robots[robot_num].isMoving = True
        theta = 90
        if not clockwise:
            theta = -90
        hand_coords = self.robots[robot_num].get_all_points()
        print(f"Hand coords: {hand_coords}")
        middle = middle_point((hand_coords[0][0], hand_coords[0][1]),
                              (hand_coords[1][0], hand_coords[1][1]),
                              (hand_coords[2][0], hand_coords[2][1]))
        non_middle = [0, 1, 2]
        non_middle.remove(middle)
        xo = hand_coords[3][0]
        yo = hand_coords[3][1]
        x_center_hand = hand_coords[middle][0]
        y_center_hand = hand_coords[middle][1]

        hand_a = non_middle[0]
        hand_c = non_middle[1]

        new_x_a, new_y_a = rotate_point(hand_coords[hand_a][0], hand_coords[hand_a][1],
                                        x_center_hand, y_center_hand, theta)
        new_x_c, new_y_c = rotate_point(hand_coords[hand_c][0], hand_coords[hand_c][1],
                                        x_center_hand, y_center_hand, theta)

        # x1, y1 = rotate_point(point1[0], point1[1], center_point[0], center_point[1], 60)

        # these are possible positions for the first turn move
        possible_first_move = [[(-1, -1), (-1, -1), (-1, -1)],
                               [(-1, -1), (-1, -1), (-1, -1)]]
        move_hands = [hand_a, hand_c]

        possible_first_move[0][hand_a] = (new_x_a, new_y_a)
        possible_first_move[0][hand_c] = hand_coords[hand_c]
        possible_first_move[0][middle] = hand_coords[middle]

        possible_first_move[1][hand_a] = hand_coords[hand_a]
        possible_first_move[1][hand_c] = (new_x_c, new_y_c)
        possible_first_move[1][middle] = hand_coords[middle]

        print(
            f"Possible first:\n{possible_first_move[0]}\n{possible_first_move[1]}")
        print(f"Move hands: {move_hands}")

        is_start_inside_triangle = isInside(hand_coords[0][0], hand_coords[0][1],
                                            hand_coords[1][0], hand_coords[1][1],
                                            hand_coords[2][0], hand_coords[2][1],
                                            hand_coords[3][0], hand_coords[3][1])

        # is_move_possible = [-1, -1, -1, -1]
        chosen_pos = -1
        new_x, new_y = -1, -1
        for i in range(len(possible_first_move)):
            print("---")
            print(f"Pos: {possible_first_move[i]}")
            new_center_x = (possible_first_move[i][0][0] + possible_first_move[i][1][0] + possible_first_move[i][2][
                0]) / 3
            new_center_y = (possible_first_move[i][0][1] + possible_first_move[i][1][1] + possible_first_move[i][2][
                1]) / 3

            check1 = do_intersect(hand_coords[3],
                                  (new_center_x, new_center_y),
                                  hand_coords[hand_a],
                                  hand_coords[middle])
            check2 = do_intersect(hand_coords[3],
                                  (new_center_x, new_center_y),
                                  hand_coords[hand_c],
                                  hand_coords[middle])
            print(f"New Center: ({new_center_x}, {new_center_y})")
            print(f"Center: ({hand_coords[3][0]}, {hand_coords[3][1]})")
            print(f"Check: {check1}  {check2}")
            if check1 or check2:
                continue

            can_move = self.is_move_possible_two_holds(robot_num, xo, yo,
                                                       new_center_x, new_center_y,
                                                       possible_first_move[i], move_hands[i])
            is_possible = is_in_three_hands_area(possible_first_move[i][0][0], possible_first_move[i][0][1],
                                                 possible_first_move[i][1][0], possible_first_move[i][1][1],
                                                 possible_first_move[i][2][0], possible_first_move[i][2][1],
                                                 new_center_x, new_center_y)
            new_0, new_1, new_2, ang_0, ang_1, ang_2, rh = self.get_new_params_by_vector(robot_num,
                                                                                         xo, yo,
                                                                                         new_center_x, new_center_y,
                                                                                         possible_first_move[i])
            is_correct_hand_order = mirroring_check(ang_0, ang_1, ang_2)
            # is_move_possible[i] = can_move
            print(f"1 Can move? {can_move} Is possible? {is_possible}")
            if can_move and is_correct_hand_order and is_possible:
                chosen_pos = i
                new_x, new_y = new_center_x, new_center_y
                break

        print(f"Chosen pos: {possible_first_move[chosen_pos]}")
        last_pos = possible_first_move[chosen_pos][:]
        print(f"Last pos 1: {last_pos}")
        non_middle.remove(move_hands[chosen_pos])
        print(f"Non-middle: {non_middle[0]}")
        print(f"Chosen: {chosen_pos}")
        # return -1
        if chosen_pos == 0:
            last_pos[hand_c] = (new_x_c, new_y_c)
        else:
            last_pos[hand_a] = (new_x_a, new_y_a)
        print(f"Last pos 2: {last_pos}")

        shifts = [-1, -1, -1]
        shifts[middle] = self.coef * size["innerRadLimit"]
        shifts[non_middle[0]] = shifts[move_hands[chosen_pos]] = math.sqrt(
            (self.coef * size["innerRadLimit"]) ** 2 + size["netStep"] ** 2)
        print(f"Shifts: {shifts}")
        last_center_x, last_center_y = center_by_params(last_pos, shifts[0], shifts[1], shifts[2])
        print(f"Temp center: ({new_x}, {new_y})")
        print(f"Last center (first): ({last_center_x}, {last_center_y})")
        can_move = self.is_move_possible_two_holds(robot_num, new_x, new_y,
                                                   last_center_x, last_center_y,
                                                   last_pos, non_middle[0])
        is_possible = is_in_three_hands_area(last_pos[0][0], last_pos[0][1],
                                             last_pos[1][0], last_pos[1][1],
                                             last_pos[2][0], last_pos[2][1],
                                             last_center_x, last_center_y)
        print(f"Can move? {can_move} Is possible? {is_possible}")
        if not (can_move and is_possible):
            return -1
            # last_center_x, last_center_y = self.find_pos_by_shifts(robot_num, new_x, new_y,
            #                                                        last_pos, shifts, non_middle[0])

        if last_center_x == -1 or last_center_y == -1:
            return -1
        path = [hand_coords[:3], possible_first_move[chosen_pos], last_pos]
        centers = [(xo, yo), (new_x, new_y), (last_center_x, last_center_y)]
        print(f"Path: {path}")
        print(f"Centers: {centers}")

        print("--- TURN BY PATH ---")
        self.turn_by_path(robot_num, path, centers)
        print("--- END TURN BY PATH ---")
        self.robots[robot_num].isMoving = False
        return 1

    def turn(self, robot_num, allowed_poses, pos_num):
        hand_coords = self.robots[robot_num].get_all_points()
        middle = middle_point((hand_coords[0][0], hand_coords[0][1]),
                              (hand_coords[1][0], hand_coords[1][1]),
                              (hand_coords[2][0], hand_coords[2][1]))
        non_middle = [0, 1, 2]
        non_middle.remove(middle)
        xo = hand_coords[3][0]
        yo = hand_coords[3][1]
        x_center_hand = hand_coords[middle][0]
        y_center_hand = hand_coords[middle][1]

        left_hand = allowed_poses[pos_num][0]
        right_hand = allowed_poses[pos_num][2]

        # these are possible positions for the first turn move
        possible_first_move = [[(-1, -1), (-1, -1), (-1, -1)],
                               [(-1, -1), (-1, -1), (-1, -1)],
                               [(-1, -1), (-1, -1), (-1, -1)],
                               [(-1, -1), (-1, -1), (-1, -1)]]
        move_hands = [non_middle[1], non_middle[0], non_middle[1], non_middle[0]]

        possible_first_move[0][non_middle[0]] = hand_coords[non_middle[0]]
        possible_first_move[0][non_middle[1]] = left_hand
        possible_first_move[0][middle] = hand_coords[middle]

        possible_first_move[1][non_middle[1]] = hand_coords[non_middle[1]]
        possible_first_move[1][non_middle[0]] = left_hand
        possible_first_move[1][middle] = hand_coords[middle]

        possible_first_move[2][non_middle[0]] = hand_coords[non_middle[0]]
        possible_first_move[2][non_middle[1]] = right_hand
        possible_first_move[2][middle] = hand_coords[middle]

        possible_first_move[3][non_middle[1]] = hand_coords[non_middle[1]]
        possible_first_move[3][non_middle[0]] = right_hand
        possible_first_move[3][middle] = hand_coords[middle]
        print(
            f"Possible first:\n{possible_first_move[0]}\n{possible_first_move[1]}\n{possible_first_move[2]}\n{possible_first_move[3]}")
        print(f"Move hands: {move_hands}")

        is_start_inside_triangle = isInside(hand_coords[0][0], hand_coords[0][1],
                                            hand_coords[1][0], hand_coords[1][1],
                                            hand_coords[2][0], hand_coords[2][1],
                                            hand_coords[3][0], hand_coords[3][1])

        # is_move_possible = [-1, -1, -1, -1]
        chosen_pos = -1
        new_x, new_y = -1, -1
        for i in range(len(possible_first_move)):
            new_center_x = (possible_first_move[i][0][0] + possible_first_move[i][1][0] + possible_first_move[i][2][
                0]) / 3
            new_center_y = (possible_first_move[i][0][1] + possible_first_move[i][1][1] + possible_first_move[i][2][
                1]) / 3
            # new_center_x = (possible_first_move[i][non_middle[0]][0] + possible_first_move[i][non_middle[1]][0]) / 2
            # new_center_y = (possible_first_move[i][non_middle[0]][1] + possible_first_move[i][non_middle[1]][1]) / 2
            is_curr_inside_triangle = isInside(hand_coords[0][0], hand_coords[0][1],
                                               hand_coords[1][0], hand_coords[1][1],
                                               hand_coords[2][0], hand_coords[2][1],
                                               new_center_x, new_center_y)
            if is_start_inside_triangle != is_curr_inside_triangle:
                continue

            print(f"NewCenter: ({new_center_x}, {new_center_y})")
            can_move = self.is_move_possible_two_holds(robot_num, xo, yo,
                                                       new_center_x, new_center_y,
                                                       possible_first_move[i], move_hands[i])
            is_possible = is_in_three_hands_area(possible_first_move[i][0][0], possible_first_move[i][0][1],
                                                 possible_first_move[i][1][0], possible_first_move[i][1][1],
                                                 possible_first_move[i][2][0], possible_first_move[i][2][1],
                                                 new_center_x, new_center_y)
            new_0, new_1, new_2, ang_0, ang_1, ang_2, rh = self.get_new_params_by_vector(robot_num,
                                                                                         xo, yo,
                                                                                         new_center_x, new_center_y,
                                                                                         possible_first_move[i])
            is_correct_hand_order = mirroring_check(ang_0, ang_1, ang_2)
            # is_move_possible[i] = can_move
            if can_move and is_correct_hand_order and is_possible:
                chosen_pos = i
                new_x, new_y = new_center_x, new_center_y
                break
            # else:
            #     shifts = [new_0, new_1, new_2]
            #     new_center_x, new_center_y = self.find_pos_by_shifts(robot_num, xo, yo,
            #                                                          possible_first_move[i], shifts, move_hands[i])
            #     if new_center_x != -1 and new_center_y != -1:
            #         chosen_pos = i
            #         new_x, new_y = new_center_x, new_center_y
            #         break

        print(f"Chosen pos: {possible_first_move[chosen_pos]}")
        last_pos = possible_first_move[chosen_pos][:]
        print(f"Last pos 1: {last_pos}")
        non_middle.remove(move_hands[chosen_pos])
        print(f"Non-middle: {non_middle[0]}")
        print(f"Chosen: {chosen_pos}")
        # return -1
        if chosen_pos < 2:
            # the left_hand was chosen for possible_first_move
            print("right")
            last_pos[non_middle[0]] = right_hand
        else:
            print("left")
            last_pos[non_middle[0]] = left_hand
        print(f"Last pos 2: {last_pos}")

        shifts = [-1, -1, -1]
        shifts[middle] = self.coef * size["innerRadLimit"]
        shifts[non_middle[0]] = shifts[move_hands[chosen_pos]] = math.sqrt(
            (self.coef * size["innerRadLimit"]) ** 2 + size["netStep"] ** 2)
        print(f"Shifts: {shifts}")
        last_center_x, last_center_y = center_by_params(last_pos, shifts[0], shifts[1], shifts[2])
        print(f"Temp center: ({new_x}, {new_y})")
        print(f"Last center (first): ({last_center_x}, {last_center_y})")
        can_move = self.is_move_possible_two_holds(robot_num, new_x, new_y,
                                                   last_center_x, last_center_y,
                                                   last_pos, non_middle[0])
        is_possible = is_in_three_hands_area(last_pos[0][0], last_pos[0][1],
                                             last_pos[1][0], last_pos[1][1],
                                             last_pos[2][0], last_pos[2][1],
                                             last_center_x, last_center_y)
        print(f"Can move? {can_move} Is possible? {is_possible}")
        if not (can_move and is_possible):
            return -1
            # last_center_x, last_center_y = self.find_pos_by_shifts(robot_num, new_x, new_y,
            #                                                        last_pos, shifts, non_middle[0])

        if last_center_x == -1 or last_center_y == -1:
            return -1
        path = [hand_coords[:3], possible_first_move[chosen_pos], last_pos]
        centers = [(xo, yo), (new_x, new_y), (last_center_x, last_center_y)]
        print(f"Path: {path}")
        print(f"Centers: {centers}")

        self.turn_by_path(robot_num, path, centers)
        return 1

    def path_manual(self, robot_num, direction):
        '''
        :param direction: 0 - left, 1 - right, 2 - up, 3 - down
        :return:
        '''
        hand_coords = self.robots[robot_num].get_all_points()
        print(f"Hand coords: {hand_coords}")
        x1, y1 = (hand_coords[0][0], hand_coords[0][1])
        x2, y2 = (hand_coords[1][0], hand_coords[1][1])
        x3, y3 = (hand_coords[2][0], hand_coords[2][1])
        points = [(float("%.4f" % x1), float("%.4f" % y1)),
                  (float("%.4f" % x2), float("%.4f" % y2)),
                  (float("%.4f" % x3), float("%.4f" % y3))]
        # points = [(x1, y1),
        #           (x2, y2),
        #           (x3, y3)]
        points.sort(key=lambda point: (point[0], point[1]))
        allowed_poses = self.get_allowed_poses(robot_num)
        print(f"Allowed: {allowed_poses}")
        current_pose = self.current_pos(robot_num, points)
        print(f"Current pose: {current_pose}")
        print(f"Direction: {direction}")

        if current_pose == 2:
            # align the robot to allowed pos
            pass

        res = 0
        if (direction == 0 or direction == 1) and current_pose != 0:
            print("Wrong position of robot!")
            return -1
            # res = self.turn(robot_num, allowed_poses, 0)
        elif (direction == 2 or direction == 3) and current_pose != 1:
            print("Wrong position of robot!")
            return -1
            # res = self.turn(robot_num, allowed_poses, 1)
        if res == -1:
            return -1

        hand_coords = self.robots[robot_num].get_all_points()
        points = [coordinates_to_ceil(hand_coords[0][0], hand_coords[0][1]),
                  coordinates_to_ceil(hand_coords[1][0], hand_coords[1][1]),
                  coordinates_to_ceil(hand_coords[2][0], hand_coords[2][1])]
        sorted_points = points
        sorted_points.sort(key=lambda point: (point[0], point[1]))
        new_coords = [(hand_coords[0][0], hand_coords[0][1]),
                      (hand_coords[1][0], hand_coords[1][1]),
                      (hand_coords[2][0], hand_coords[2][1])]

        if direction == 0:
            print("left")
            new_middle = sorted_points[0]
            new_right = sorted_points[1]
            mid_x_ceil, mid_y_ceil = ceil_to_coordinates(new_middle[0], new_middle[1])
            print(f"Mid: {mid_x_ceil}, {mid_y_ceil}")
            left_x_ceil = mid_x_ceil - size["netStep"]
            left_y_ceil = mid_y_ceil
            print(f"Left: {left_x_ceil}, {left_y_ceil}")
            new_left = coordinates_to_ceil(left_x_ceil, left_y_ceil)
            print(f"Mid: {new_middle} Left: {new_left} Right: {new_right}")
            # new_left = (new_middle[0] - 1, new_middle[1] - 1)
            if new_left[0] < 0 or new_left[1] < 0:
                print("Move impossible!")
                return -1
            mid_coord = ceil_to_coordinates(new_middle[0], new_middle[1])
            right_coord = ceil_to_coordinates(new_right[0], new_right[1])
            left_coord = ceil_to_coordinates(new_left[0], new_left[1])
            left_hand = [0, 1, 2]
            mid_hand = -1
            right_hand = -1
            Tol = 2
            for i in range(3):
                if (abs(mid_coord[0] - hand_coords[i][0]) < Tol) and (abs(mid_coord[1] - hand_coords[i][1]) < Tol):
                    left_hand.remove(i)
                    mid_hand = i
                if (abs(right_coord[0] - hand_coords[i][0]) < Tol) and (abs(right_coord[1] - hand_coords[i][1]) < Tol):
                    left_hand.remove(i)
                    right_hand = i
            if len(left_hand) != 1:
                print("Something went wrong, abort!")
                return -1
            new_coords[left_hand[0]] = (left_coord[0], left_coord[1])
            # calc center
            shifts = [-1, -1, -1]
            shifts[mid_hand] = self.coef * size["innerRadLimit"]
            shifts[left_hand[0]] = shifts[right_hand] = math.sqrt(
                (self.coef * size["innerRadLimit"]) ** 2 + size["netStep"] ** 2)
            new_center_x, new_center_y = center_by_params(new_coords, shifts[0], shifts[1], shifts[2])
            print(f"New coords: {new_coords} New center: ({new_center_x}, {new_center_y})")
            res = self.move_vector(robot_num, hand_coords[3][0], hand_coords[3][1],
                                   new_center_x, new_center_y, new_coords, left_hand[0])
            # print(f"res: {res}")
            if res == -1:
                print("Critical error, return")
            return -1

        elif direction == 1:
            print("right")
            new_middle = sorted_points[2]
            new_right = sorted_points[1]
            mid_x_ceil, mid_y_ceil = ceil_to_coordinates(new_middle[0], new_middle[1])
            print(f"Mid: {mid_x_ceil}, {mid_y_ceil}")
            left_x_ceil = mid_x_ceil + size["netStep"]
            left_y_ceil = mid_y_ceil
            print(f"Left: {left_x_ceil}, {left_y_ceil}")
            new_left = coordinates_to_ceil(left_x_ceil, left_y_ceil)
            print(f"Mid: {new_middle} Left: {new_left} Right: {new_right}")
            # new_left = (new_middle[0] - 1, new_middle[1] - 1)
            if new_left[0] < 0 or new_left[1] < 0:
                print("Move impossible!")
                return -1
            mid_coord = ceil_to_coordinates(new_middle[0], new_middle[1])
            right_coord = ceil_to_coordinates(new_right[0], new_right[1])
            left_coord = ceil_to_coordinates(new_left[0], new_left[1])
            left_hand = [0, 1, 2]
            mid_hand = -1
            right_hand = -1
            Tol = 2
            for i in range(3):
                if (abs(mid_coord[0] - hand_coords[i][0]) < Tol) and (abs(mid_coord[1] - hand_coords[i][1]) < Tol):
                    left_hand.remove(i)
                    mid_hand = i
                if (abs(right_coord[0] - hand_coords[i][0]) < Tol) and (abs(right_coord[1] - hand_coords[i][1]) < Tol):
                    left_hand.remove(i)
                    right_hand = i
            if len(left_hand) != 1:
                print("Something went wrong, abort!")
                return -1
            new_coords[left_hand[0]] = (left_coord[0], left_coord[1])

            # calc center
            shifts = [-1, -1, -1]
            shifts[mid_hand] = self.coef * size["innerRadLimit"]
            shifts[left_hand[0]] = shifts[right_hand] = math.sqrt(
                (self.coef * size["innerRadLimit"]) ** 2 + size["netStep"] ** 2)
            new_center_x, new_center_y = center_by_params(new_coords, shifts[0], shifts[1], shifts[2])
            print(f"New coords: {new_coords} New center: ({new_center_x}, {new_center_y})")
            res = self.move_vector(robot_num, hand_coords[3][0], hand_coords[3][1],
                                   new_center_x, new_center_y, new_coords, left_hand[0])
            # print(f"res: {res}")
            if res == -1:
                print("Critical error, return")
                return -1
        elif direction == 2:
            print("up")
            new_middle = sorted_points[0]
            new_right = sorted_points[1]
            mid_x_ceil, mid_y_ceil = ceil_to_coordinates(new_middle[0], new_middle[1])
            print(f"Mid: {mid_x_ceil}, {mid_y_ceil}")
            left_x_ceil = mid_x_ceil
            left_y_ceil = mid_y_ceil - size["netStep"]
            print(f"Left: {left_x_ceil}, {left_y_ceil}")
            new_left = coordinates_to_ceil(left_x_ceil, left_y_ceil)
            print(f"Mid: {new_middle} Left: {new_left} Right: {new_right}")
            # new_left = (new_middle[0] - 1, new_middle[1] - 1)
            if new_left[0] < 0 or new_left[1] < 0:
                print("Move impossible!")
                return -1
            mid_coord = ceil_to_coordinates(new_middle[0], new_middle[1])
            right_coord = ceil_to_coordinates(new_right[0], new_right[1])
            left_coord = ceil_to_coordinates(new_left[0], new_left[1])
            left_hand = [0, 1, 2]
            mid_hand = -1
            right_hand = -1
            Tol = 2
            for i in range(3):
                if (abs(mid_coord[0] - hand_coords[i][0]) < Tol) and (abs(mid_coord[1] - hand_coords[i][1]) < Tol):
                    left_hand.remove(i)
                    mid_hand = i
                if (abs(right_coord[0] - hand_coords[i][0]) < Tol) and (abs(right_coord[1] - hand_coords[i][1]) < Tol):
                    left_hand.remove(i)
                    right_hand = i
            if len(left_hand) != 1:
                print("Something went wrong, abort!")
                return -1
            new_coords[left_hand[0]] = (left_coord[0], left_coord[1])

            # calc center
            shifts = [-1, -1, -1]
            shifts[mid_hand] = self.coef * size["innerRadLimit"]
            shifts[left_hand[0]] = shifts[right_hand] = math.sqrt(
                (self.coef * size["innerRadLimit"]) ** 2 + size["netStep"] ** 2)
            new_center_x, new_center_y = center_by_params(new_coords, shifts[0], shifts[1], shifts[2])
            print(f"New coords: {new_coords} New center: ({new_center_x}, {new_center_y})")
            res = self.move_vector(robot_num, hand_coords[3][0], hand_coords[3][1],
                                   new_center_x, new_center_y, new_coords, left_hand[0])
            # print(f"res: {res}")
            if res == -1:
                print("Critical error, return")
                return -1

        elif direction == 3:
            print("down")
            print(f"In down: {sorted_points}")
            new_middle = sorted_points[2]
            new_left = sorted_points[1]
            mid_x_ceil, mid_y_ceil = ceil_to_coordinates(new_middle[0], new_middle[1])
            right_x_ceil = mid_x_ceil
            right_y_ceil = mid_y_ceil + size["netStep"]
            new_right = coordinates_to_ceil(right_x_ceil, right_y_ceil)
            # new_right = (new_middle[0] + 1, new_middle[1])
            print(f"Mid: {new_middle} Left: {new_left} Right: {new_right}")
            if new_right[0] >= self.max_x:  # or new_right[1] < 0:
                print("Move impossible!")
                return -1
            mid_coord = ceil_to_coordinates(new_middle[0], new_middle[1])
            right_coord = ceil_to_coordinates(new_right[0], new_right[1])
            left_coord = ceil_to_coordinates(new_left[0], new_left[1])
            right_hand = [0, 1, 2]
            mid_hand = -1
            left_hand = -1
            Tol = 2
            for i in range(3):
                if (abs(mid_coord[0] - hand_coords[i][0]) < Tol) and (abs(mid_coord[1] - hand_coords[i][1]) < Tol):
                    right_hand.remove(i)
                    mid_hand = i
                if (abs(left_coord[0] - hand_coords[i][0]) < Tol) and (abs(left_coord[1] - hand_coords[i][1]) < Tol):
                    right_hand.remove(i)
                    left_hand = i
            if len(right_hand) != 1:
                print("Something went wrong, abort!")
                return -1
            new_coords[right_hand[0]] = (right_coord[0], right_coord[1])

            # calc center
            shifts = [-1, -1, -1]
            shifts[mid_hand] = self.coef * size["innerRadLimit"]
            shifts[right_hand[0]] = shifts[left_hand] = math.sqrt(
                (self.coef * size["innerRadLimit"]) ** 2 + size["netStep"] ** 2)
            new_center_x, new_center_y = center_by_params(new_coords, shifts[0], shifts[1], shifts[2])
            print(f"New coords: {new_coords} New center: ({new_center_x}, {new_center_y})")
            res = self.move_vector(robot_num, hand_coords[3][0], hand_coords[3][1],
                                   new_center_x, new_center_y, new_coords, right_hand[0])
            # print(f"res: {res}")
            if res == -1:
                print("Critical error, return")
                return -1

    def turn_by_path(self, robot_num, path, centers):
        for i in range(1, len(path)):
            print(f"i: {i}, len: {len(path)}, path: {path}, centers: {centers}")
            x_t, y_t = centers[i]
            x_s, y_s = self.robots[robot_num].get_center()
            print(f"Iteration No.{i}: Os = ({x_s}, {y_s}); Ot = ({x_t}, {y_t})")
            pos = path[i]
            print(f"Position: {pos}")
            move_hand = -1
            Tol = 5
            for j in range(3):
                print(f"j: {j}")
                print(f"Hand: ({self.robots[robot_num].hands[j].x}, {self.robots[robot_num].hands[j].y}) to ({pos[j][0]}, {pos[j][1]})")
                # print(f"pos[j][0] - self.robots[robot_num].hands[j].x = {pos[j][0] - self.robots[robot_num].hands[j].x}\n"
                #       f"pos[j][1] - self.robots[robot_num].hands[j].y = {pos[j][1] - self.robots[robot_num].hands[j].y}")
                if (abs(pos[j][0] - self.robots[robot_num].hands[j].x) > Tol) or (
                        abs(pos[j][1] - self.robots[robot_num].hands[j].y) > Tol):
                    if move_hand != -1:
                        print("Need to move two hands at the same time, impossible!")
                        return -1
                    else:
                        move_hand = j

            # sleep(10.0)
            print(f"Move hand: {move_hand}")
            self.robots[robot_num].get_robot_params()
            # sleep(10.0)
            res = self.move_vector(robot_num, x_s, y_s, x_t, y_t, pos, move_hand)
            # print(f"res: {res}")
            if res == -1:
                print("Critical error, return")
                return -1
        return 1

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
            self.robots[robot_num].get_robot_params()
            res = self.move_vector(robot_num, x_s, y_s, x_t, y_t, pos, move_hand)
            if res == -1:
                print("Critical error, return")
                return
        return 1

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
