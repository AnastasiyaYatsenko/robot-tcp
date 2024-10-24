import socket
from struct import pack
from typing import NamedTuple
from arm_geometry_test import *
from waiting import wait


class Params(NamedTuple):
    lin: float
    ang: float
    hold: int

    x: int
    y: int

# class syntax

class Robot:
    def __init__(self):
        self.hands = [Params(0, 0, 0, 0, 0), Params(1, 1, 1, 0, 0), Params(2, 2, 2, 0, 0)]
        # self.move_dir = 0
        # self.hand_i = 0
        self.isMoving = False
        self.isMovingPath = False
        self.os = (-1, -1)
        self.ot = (-1, -1)
        self.curr_index = -1
        self.robot_ip = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isAlive = False
        self.out_buffer = b''
        self.path = []
        self.centers = []
        self.opt_points = []
        self.params_updated = False

                                # x       y
        # self.real_coordinates = [(300, 300),  # hand 0
        #                          (100, 300),  # hand 1
        #                          (500, 300),  # hand 2
        #                          (300, 252)]  # center
        #
        # self.real_coordinates_hand = [(300, 300),  # hand 0
        #                               (100, 300),  # hand 1
        #                               (500, 300),  # hand 2
        #                               (300, 252)]  # center

        self.real_coordinates = [(300, 300),  # hand 0
                                 (500, 300),  # hand 1
                                 (100, 300),  # hand 2
                                 (300, 252)]  # center

        self.real_coordinates_hand = [(300, 300),  # hand 0
                                      (500, 300),  # hand 1
                                      (100, 300),  # hand 2
                                      (300, 252)]  # center

    def set_socket(self, new_socket):
        print(new_socket)
        self.socket = new_socket

    def set_ip(self, ip):
        self.robot_ip = ip

    def get_ip(self):
        return self.robot_ip

    def get_robot_params(self):
        p = pack('@ffiffiffi',
                 0, 0, 50,
                 0, 0, 50,
                 0, 0, 50)
        # print(f"PACKAGE: {p}")
        # self.isMoving = True
        self.params_updated = False
        self.out_buffer = p
        wait(lambda: self.is_params_recieved(), timeout_seconds=120,
             waiting_for="waiting for robot to return params")

    def set_robot_params_hands(self, hand1, hand2, hand3):
        self.hands[0] = Params(hand1.lin, hand1.ang, hand1.hold, hand1.x, hand1.y)
        self.hands[1] = Params(hand2.lin, hand2.ang, hand2.hold, hand1.x, hand1.y)
        self.hands[2] = Params(hand3.lin, hand3.ang, hand3.hold, hand1.x, hand1.y)

    def set_robot_params(self, lin1, ang1, hold1, lin2, ang2, hold2, lin3, ang3, hold3):
        self.hands[0] = Params(lin1, ang1, hold1, self.hands[0].x, self.hands[0].y)
        self.hands[1] = Params(lin2, ang2, hold2, self.hands[1].x, self.hands[1].y)
        self.hands[2] = Params(lin3, ang3, hold3, self.hands[2].x, self.hands[2].y)

    def set_coordinates(self, x1, y1, x2, y2, x3, y3):
        self.hands[0] = Params(self.hands[0].lin, self.hands[0].ang, self.hands[0].hold, x1, y1)
        self.hands[1] = Params(self.hands[1].lin, self.hands[1].ang, self.hands[1].hold, x2, y2)
        self.hands[2] = Params(self.hands[2].lin, self.hands[2].ang, self.hands[2].hold, x3, y3)
        # self.place_ceil_coordinates()

    def set_hand_coordinates(self, i, x, y):
        self.hands[i] = Params(self.hands[i].lin, self.hands[i].ang, self.hands[i].hold, x, y)

    def set_hand_x(self, i, x):
        self.hands[i] = Params(self.hands[i].lin, self.hands[i].ang, self.hands[i].hold, x, self.hands[i].y)

    def set_hand_y(self, i, y):
        self.hands[i] = Params(self.hands[i].lin, self.hands[i].ang, self.hands[i].hold, self.hands[i].x, y)

    # def place_ceil_coordinates(self):
    #     self.move_hand(0, self.hands[0].x, self.hands[0].y)
    #     self.move_hand(1, self.hands[1].x, self.hands[1].y)
    #     self.move_hand(2, self.hands[2].x, self.hands[2].y)

    # def move_hand(self, hand_num, x, y):
    #     if ceil_arr[y][x] == 0:
    #         self.hand_unhold_point(hand_num)
    #         self.hand_hold_point(hand_num, x, y)
    #
    # def hand_unhold_point(self, hand_num):
    #     old_x = self.hands[hand_num].x
    #     old_y = self.hands[hand_num].y
    #     ceil_arr[old_y][old_x] = 0
    #
    # def hand_hold_point(self, hand_num, x, y):
    #     if ceil_arr[y][x] == 0:
    #         ceil_arr[y][x] = 1
    #         self.set_hand_x(hand_num, x)
    #         self.set_hand_y(hand_num, y)
    #     else:
    #         print("Point occupied!")

    def get_all_points(self):
        center_x, center_y = self.get_center()
        return [(self.hands[0].x, self.hands[0].y),
                (self.hands[1].x, self.hands[1].y),
                (self.hands[2].x, self.hands[2].y),
                (center_x, center_y)]

    def set_real_coordinates(self, c1, c2, c3, co):
        self.real_coordinates[0] = c1
        self.real_coordinates[1] = c2
        self.real_coordinates[2] = c3
        self.real_coordinates[3] = co

    def get_real_coordinates_robot(self):
        return self.real_coordinates

    def set_real_coordinates_hand(self, c1, c2, c3, co):
        self.real_coordinates_hand[0] = c1
        self.real_coordinates_hand[1] = c2
        self.real_coordinates_hand[2] = c3
        self.real_coordinates_hand[3] = co

    def get_real_coordinates_hand(self):
        return self.real_coordinates_hand

    def get_center(self):
        # print("--- get center ---")
        center_x, center_y = 0, 0
        if self.is_aligned():
            # print("aligned")
            center_x, center_y = calculate_center([(self.hands[0].x, self.hands[0].y),
                                                   (self.hands[1].x, self.hands[1].y),
                                                   (self.hands[2].x, self.hands[2].y)],
                                                  [self.hands[0].lin, self.hands[1].lin, self.hands[2].lin])
        else:
            # print("not aligned")
            center_x, center_y = calculate_center_three_points(self.hands[0].x, self.hands[0].y,
                                                               self.hands[1].x, self.hands[1].y,
                                                               self.hands[2].x, self.hands[2].y,
                                                               self.hands[0].lin, self.hands[1].lin, self.hands[2].lin)
        '''center_x, center_y = calculate_center(self.hands[0].x, self.hands[0].y,
                                              self.hands[1].x, self.hands[1].y,
                                              self.hands[2].x, self.hands[2].y,
                                              self.hands[0].lin, self.hands[1].lin, self.hands[2].lin)'''
        return center_x, center_y

    def is_finished_move(self):
        if not self.isMoving:
            return True
        return False

    def is_params_recieved(self):
        return self.params_updated

    def is_aligned(self):
        # print("---")
        # print("CHECK IF IN LINE")
        # print(f"X: {self.hands[0].x} {self.hands[1].x} {self.hands[2].x}")
        # print(f"Y: {self.hands[0].y} {self.hands[1].y} {self.hands[2].y}")
        hand_coords = [(float("%.4f" % self.hands[0].x), float("%.4f" % self.hands[0].y)),
                       (float("%.4f" % self.hands[1].x), float("%.4f" % self.hands[1].y)),
                       (float("%.4f" % self.hands[2].x), float("%.4f" % self.hands[2].y))]
        if is_horizontal_aligned(hand_coords) or is_vertical_aligned(hand_coords):
            # print("---")
            return True
        Tol = 1e-10
        if (self.hands[0].x == self.hands[2].x and self.hands[0].x != self.hands[1].x) or (
                self.hands[1].x == self.hands[2].x and self.hands[1].x != self.hands[0].x) or (
                self.hands[0].x == self.hands[1].x and self.hands[0].x != self.hands[2].x):
            return False
        if (self.hands[0].y == self.hands[2].y and self.hands[0].y != self.hands[1].y) or (
                self.hands[1].y == self.hands[2].y and self.hands[1].y != self.hands[0].y) or (
                self.hands[0].y == self.hands[1].y and self.hands[0].y != self.hands[2].y):
            return False
        if abs((self.hands[2].x - self.hands[0].x) / (self.hands[1].x - self.hands[0].x) -
               (self.hands[2].y - self.hands[0].y) / (self.hands[1].y - self.hands[0].y)) <= Tol:
            # print("---")
            return True
        # print("---")
        return False

    def is_horizontal_aligned(self):
        if (self.hands[0].y == self.hands[1].y and
                self.hands[1].y == self.hands[2].y):
            return True
        return False

    def is_vertical_aligned(self):
        if (self.hands[0].x == self.hands[1].x and
                self.hands[1].x == self.hands[2].x):
            return True
        return False


    def print(self):
        print("Robot "+self.robot_ip)
        print("Hand 1: " + str(self.hands[0]))
        print("Hand 2: " + str(self.hands[1]))
        print("Hand 3: " + str(self.hands[2]))
