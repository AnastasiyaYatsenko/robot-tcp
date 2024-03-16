import math

RAD2DEG = 180 / math.pi


def get_arm_angle_by_y(x, y):
    return math.asin(y / math.sqrt(x ** 2 + y ** 2)) * RAD2DEG


def get_arm_shift_by_y(x, y):
    return math.sqrt(x ** 2 + y ** 2)


def get_arm_state_by_pos(pos, size, id=''):
    # here will be result of arm state:
    # a - angle
    # s - shift
    # h - hook state 0..1, 1 is fully connected
    res = {"a": 0, "s": 0, "h": 0}

    # here we transform pos (which could be negative) to abs_pos (only positive) and direction (is leg in front or behind) to unify calculation no matter where...
    direction = 1 if pos > 0 else -1
    oposit_pos = size['netStep'] * 1.5
    abs_pos = abs(pos)
    if abs_pos > oposit_pos:
        abs_pos = 2 * oposit_pos - abs_pos
        direction = -direction

    # print(id, " pos:", pos, " direction:", direction. " absPos:", abs_pos, " opositPos:", oposit_pos)

    # limit of position where hook could be connected
    max_pos_in_lim = math.sqrt(size['outerRadLimit'] ** 2 - size['innerRadLimit'] ** 2)

    # Calculation of hook position
    max_pos_hoock1 = size['netStep']
    max_pos_hoock0 = max_pos_in_lim
    if abs_pos <= max_pos_hoock1:
        res['h'] = 1
    elif abs_pos >= max_pos_hoock0:
        res['h'] = 0
    else:
        res['h'] = (max_pos_hoock0 - abs_pos) / (max_pos_hoock1)

    # Calculation of angle and shift:
    if abs_pos < max_pos_in_lim:
        # if hook is in connecting range
        res['a'] = get_arm_angle_by_y(size['innerRadLimit'], abs_pos)
        res['s'] = get_arm_shift_by_y(size['innerRadLimit'], abs_pos)

    if max_pos_in_lim <= abs_pos <= oposit_pos:
        # if hook is out of connecting range
        a0 = get_arm_angle_by_y(size['innerRadLimit'], max_pos_in_lim)
        a1 = 180
        res['a'] = a0 + (a1 - a0) * ((abs_pos - max_pos_in_lim) / (oposit_pos - max_pos_in_lim))
        res['s'] = get_arm_shift_by_y(size['innerRadLimit'], max_pos_in_lim)

    # to unify angle reference system
    if direction < 0:
        res['a'] = 360 - res['a']

    # normalizes the value within the range [0, maximum]
    res['a'] = res['a'] % 360

    return res


# calculate center when all holders are aligned on one line
def calculate_center(x1, y1, x2, y2, x3, y3, r1, r2, r3):
    x1 = size["netBorder"] + x1 * size["netStep"]
    y1 = size["netBorder"] + y1 * size["netStep"]

    x2 = size["netBorder"] + x2 * size["netStep"]
    y2 = size["netBorder"] + y2 * size["netStep"]

    x3 = size["netBorder"] + x3 * size["netStep"]
    y3 = size["netBorder"] + y3 * size["netStep"]

    l = (r1**2 - r2**2) / (2 * 200) - (200 / 2)
    h = math.sqrt(r2**2-l**2)
    y = 0
    x = 0
    if (y1 == y2) and (y2 == y3):
        if (x1 < x2) and (x2 < x3):
            y = y1 - h
            x = x2 + l
        if (x2 < x3) and (x3 < x1):
            y = y1 - h
            x = x3 + l
        if (x3 < x1) and (x1 < x2):
            y = y1 - h
            x = x1 + l

        if (x3 < x2) and (x2 < x1):
            y = y1 + h
            x = x2 + l
        if (x2 < x1) and (x1 < x3):
            y = y1 + h
            x = x1 + l
        if (x1 < x3) and (x3 < x2):
            y = y1 + h
            x = x3 + l
        print(f"x: {x}, y: {y}")
    elif (x1 == x2) and (x2 == x3):
        if (y3 < y2) and (y2 < y1):
            y = y2 + l
            x = x1 - h
        if (y2 < y1) and (y1 < y3):
            y = y1 + l
            x = x1 - h
        if (y1 < y3) and (y3 < y2):
            y = y3 + l
            x = x1 - h

        if (y1 < y2) and (y2 < y3):
            y = y2 + l
            x = x1 + h
        if (y3 < y1) and (y1 < y2):
            y = y1 + l
            x = x1 + h
        if (y2 < y3) and (y3 < y1):
            y = y3 + l
            x = x1 + h
        print(f"x: {x}, y: {y}")
    else:
        x, y = calculate_center_three_points(x1, y1, x2, y2, x3, y3, r1, r2, r3)
    return x, y


# for when holders are NOT on one line
def calculate_center_three_points(x1, y1, x2, y2, x3, y3, r1, r2, r3):
    eps = 1e-6

    # x1 = size["netBorder"] + x1 * size["netStep"]
    # y1 = size["netBorder"] + y1 * size["netStep"]
    #
    # x2 = size["netBorder"] + x2 * size["netStep"]
    # y2 = size["netBorder"] + y2 * size["netStep"]
    #
    # x3 = size["netBorder"] + x3 * size["netStep"]
    # y3 = size["netBorder"] + y3 * size["netStep"]
    #
    # r1 = math.sqrt(10.0)
    # r2 = math.sqrt(10.0)
    # r3 = math.sqrt(5.0)

    x = (((y2 - y1) * (r2 * r2 - r3 * r3 - y2 * y2 + y3 * y3 - x2 * x2 + x3 * x3) - (y3 - y2) *
          (r1 * r1 - r2 * r2 - y1 * y1 + y2 * y2 - x1 * x1 + x2 * x2)) /
         (2 * ((y3 - y2) * (x1 - x2) - (y2 - y1) * (x2 - x3))))
    y = (((x2 - x1) * (r2 * r2 - r3 * r3 - x2 * x2 + x3 * x3 - y2 * y2 + y3 * y3) - (x3 - x2) *
          (r1 * r1 - r2 * r2 - x1 * x1 + x2 * x2 - y1 * y1 + y2 * y2)) /
         (2 * ((x3 - x2) * (y1 - y2) - (x2 - x1) * (y2 - y3))))
    if abs((x1 - x) * (x1 - x) + (y1 - y) * (y1 - y) - r1 * r1) < eps:
        print("x=" + str(x) + " y=" + str(y))
        return x, y
    else:
        print("Impossible")
    return -1, -1


def get_line_equation(x1, y1, x2, y2):
    a = y1 - y2
    b = x2 - x1
    c = x1*y2 - x2*y1
    return a, b, c


def get_dist_point_line(x, y, a, b, c):
    d = abs(a*x + b*y + c)/math.sqrt(a**2 + b**2)
    return d


def get_ang(x1, y1, xc, yc):
    ax = x1 - xc
    ay = y1 - yc
    # bx = 10 # b is calculated from point on the line of the center
    # by = 0

    # ang = math.acos((ax*bx + ay*by)/(math.sqrt(ax**2+ay**2)*math.sqrt(bx**2+by**2)))
    ang = math.acos((ax * 10) / (math.sqrt(ax ** 2 + ay ** 2) * 10))
    if y1 > yc:
        ang = 360 - ang

    return ang


# xn, yn - hand coordinates; a,b,c - line equation for robot movement (can be replaced with desired_center)
def calculate_new_shifts(x1, y1, x2, y2, x3, y3, a, b, c, min_shift, max_shift):
    # eps = 1e-6
    eps = 1

    x1 = size["netBorder"] + x1 * size["netStep"]
    y1 = size["netBorder"] + y1 * size["netStep"]

    x2 = size["netBorder"] + x2 * size["netStep"]
    y2 = size["netBorder"] + y2 * size["netStep"]

    x3 = size["netBorder"] + x3 * size["netStep"]
    y3 = size["netBorder"] + y3 * size["netStep"]

    new_shift1 = 0
    new_shift2 = 0
    new_shift3 = 0
    new_center_x = 0
    new_center_y = 0

    # простий перебір, поки підібраний центр не потрапить у прийнятний інтервал значень
    for shift1 in range(min_shift, max_shift, 0.1):
        for shift2 in range(min_shift, max_shift, 0.1):
            for shift3 in range(min_shift, max_shift, 0.1):
                center_x, center_y = calculate_center(x1, y1, x2, y2, x3, y3, shift1, shift2, shift3)
                if get_dist_point_line(center_x, center_y, a, b, c) <= eps:
                    new_shift1 = shift1
                    new_shift2 = shift2
                    new_shift3 = shift3
                    new_center_x = center_x
                    new_center_y = center_y
                    break
            if new_shift1 != 0:
                break
        if new_shift1 != 0:
            break
    new_ang1 = get_ang(x1, y1, new_center_x, new_center_y)
    new_ang2 = get_ang(x2, y2, new_center_x, new_center_y)
    new_ang3 = get_ang(x3, y3, new_center_x, new_center_y)
    return {new_shift1, new_ang1, new_shift2, new_ang2, new_shift3, new_ang3}


size = {
    "innerRadLimit": 48,  # min shift pos
    "outerRadLimit": 210,  # max shift pos
    "netStep": 200,
    "netBorder": 100
}

# arm_state = get_arm_state_by_pos(7, size, 'b')
# print(arm_state)

# arm_state = get_arm_state_by_pos(200, size, 'g')
# print(arm_state)
#
# arm_state = get_arm_state_by_pos(-200, size, 'b')
# print(arm_state)
