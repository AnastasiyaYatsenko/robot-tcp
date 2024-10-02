import math

RAD2DEG = 180 / math.pi


def get_arm_angle_by_y(x, y):
    return math.asin(y / math.sqrt(x ** 2 + y ** 2)) * RAD2DEG


def get_arm_shift_by_y(x, y):
    return math.sqrt(x ** 2 + y ** 2)

'''
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
'''

def ceil_to_coordinates(x, y):
    x = size["netBorder"] + x * size["netStep"]
    y = size["netBorder"] + y * size["netStep"]
    return x, y

def ceil_to_coordinates_(a):
    a = size["netBorder"] + a * size["netStep"]
    return a


def ceil_to_coordinates_all(x1, y1, x2, y2, x3, y3):
    x1 = size["netBorder"] + x1 * size["netStep"]
    y1 = size["netBorder"] + y1 * size["netStep"]

    x2 = size["netBorder"] + x2 * size["netStep"]
    y2 = size["netBorder"] + y2 * size["netStep"]

    x3 = size["netBorder"] + x3 * size["netStep"]
    y3 = size["netBorder"] + y3 * size["netStep"]

    return x1, y1, x2, y2, x3, y3

def coordinates_to_ceil(x, y):
    x = (x - size["netBorder"]) / size["netStep"]
    y = (y - size["netBorder"]) / size["netStep"]
    return int(x), int(y)

def coordinates_to_ceil_(a):
    a = (a - size["netBorder"]) / size["netStep"]
    return int(a)


def coordinates_to_ceil_all(x1, y1, x2, y2, x3, y3):
    x1 = (x1 - size["netBorder"]) / size["netStep"]
    y1 = (y1 - size["netBorder"]) / size["netStep"]

    x2 = (x2 - size["netBorder"]) / size["netStep"]
    y2 = (y2 - size["netBorder"]) / size["netStep"]

    x3 = (x3 - size["netBorder"]) / size["netStep"]
    y3 = (y3 - size["netBorder"]) / size["netStep"]

    return int(x1), int(y1), int(x2), int(y2), int(x3), int(y3)

def point_in_sector(px, py, cx, cy, v1x, v1y, v2x, v2y):
    # Преобразование координат точки с инверсией оси y
    x_prime = px - cx
    y_prime = -(py - cy)

    # Углы граничных векторов с инверсией оси y
    theta1 = math.atan2(-v1y, v1x)
    theta2 = math.atan2(-v2y, v2x)

    # Угол точки
    theta_p = math.atan2(y_prime, x_prime)

    # Нормализуем углы к диапазону [0, 2π)
    theta1 = theta1 % (2 * math.pi)
    theta2 = theta2 % (2 * math.pi)
    theta_p = theta_p % (2 * math.pi)

    # Проверка попадания угла в интервал
    if theta1 <= theta2:
        return theta1 <= theta_p <= theta2
    else:
        return theta_p >= theta1 or theta_p <= theta2

def current_pos(points):
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

def calculate_center(coords, shifts):
    x1 = coords[0][0]
    y1 = coords[0][1]
    x2 = coords[1][0]
    y2 = coords[1][1]
    x3 = coords[2][0]
    y3 = coords[2][1]
    r1 = shifts[0]
    r2 = shifts[1]
    r3 = shifts[2]
    points = [(x1, y1),
              (x2, y2),
              (x3, y3)]
    sort_points = [(x1, y1),
                   (x2, y2),
                   (x3, y3)]
    sort_points.sort(key=lambda point: (point[0], point[1]))
    # print(f"Points: {points}\nSorted: {sort_points}")
    current_pose = current_pos(sort_points)
    # print(f"IN CENTER current pos: {current_pose}")

    # print(f"0: ({x1},{y1}) | 1: ({x2},{y2}) | 2: ({x3},{y3})")
    # print(f"R: {r1} | {r2} | {r3}")
    r_short = -1
    r_long = -1

    if r1 < r2 and r1 < r3:
        r_short = r1
        r_long = r2
    elif r2 < r1 and r2 < r3:
        r_short = r2
        r_long = r3
    else:
        r_short = r3
        r_long = r1

    # print(f"r_short: {r_short}; r_long: {r_long}")

    l = (r_long ** 2 - r_short ** 2) / (2 * size['netStep']) - (size['netStep'] / 2)
    h = math.sqrt(r_short ** 2 - l ** 2)
    y = 0
    x = 0
    Tol = 2

    if current_pose == 0:  # horizontal
        if ((abs(points[1][0] - (points[0][0] + size['netStep'])) < Tol) and (
                abs(points[1][0] - (points[2][0] - size['netStep'])) < Tol) and (
                    abs(points[1][1] - points[0][1]) < Tol) and (
                    abs(points[1][1] - points[2][1]) < Tol)) or (

                (abs(points[2][0] - (points[1][0] + size['netStep'])) < Tol) and (
                abs(points[2][0] - (points[0][0] - size['netStep'])) < Tol) and (
                        abs(points[2][1] - points[1][1]) < Tol) and (
                        abs(points[2][1] - points[0][1]) < Tol)) or (

                (abs(points[0][0] - (points[2][0] + size['netStep'])) < Tol) and (
                abs(points[0][0] - (points[1][0] - size['netStep'])) < Tol) and (
                        abs(points[0][1] - points[2][1]) < Tol) and (
                        abs(points[0][1] - points[1][1]) < Tol)):
            x = sort_points[1][0]
            y = sort_points[1][1] - h
        else:
            x = sort_points[1][0]
            y = sort_points[1][1] + h
        # print(f"CENTER {current_pose} x: {x}, y: {y}")

    elif current_pose == 1:
        if ((abs(points[1][0] - points[0][0]) < Tol) and (
                abs(points[1][0] - points[2][0]) < Tol) and (
                    abs(points[1][1] - (points[0][1] + size['netStep'])) < Tol) and (
                    abs(points[1][1] - (points[2][1] - size['netStep'])) < Tol)) or (

                (abs(points[2][0] - points[1][0]) < Tol) and (
                abs(points[2][0] - points[0][0]) < Tol) and (
                        abs(points[2][1] - (points[1][1] + size['netStep'])) < Tol) and (
                        abs(points[2][1] - (points[0][1] - size['netStep'])) < Tol)) or (

                (abs(points[0][0] - points[2][0]) < Tol) and (
                abs(points[0][0] - points[1][0]) < Tol) and (
                        abs(points[0][1] - (points[2][1] + size['netStep'])) < Tol) and (
                        abs(points[0][1] - (points[1][1] - size['netStep'])) < Tol)):
            x = sort_points[1][0] + h
            y = sort_points[1][1]
        else:
            x = sort_points[1][0] - h
            y = sort_points[1][1]
    # зачепи не на одній лінії
    else:
        x, y = calculate_center_three_points(x1, y1, x2, y2, x3, y3, r1, r2, r3)
    return x, y

# обчислення координат центру за наявних координат лап
# x1 y1 - coords of FIRST ROBOT hand, x2 y2 - of SECOND ROBOT hand, x3 y3 - of THIRD ROBOT hand
# OLD

def calculate_center__(x1, y1, x2, y2, x3, y3, r1, r2, r3):
    # x1 = size["netBorder"] + x1 * size["netStep"]
    # y1 = size["netBorder"] + y1 * size["netStep"]
    #
    # x2 = size["netBorder"] + x2 * size["netStep"]
    # y2 = size["netBorder"] + y2 * size["netStep"]
    #
    # x3 = size["netBorder"] + x3 * size["netStep"]
    # y3 = size["netBorder"] + y3 * size["netStep"]

    print(f"0: ({x1},{y1}) | 1: ({x2},{y2}) | 2: ({x3},{y3})")
    print(f"R: {r1} | {r2} | {r3}")
    r_short = -1
    r_long = -1

    if r1 < r2 and r1 < r3:
        r_short = r1
        r_long = r2
    elif r2 < r1 and r2 < r3:
        r_short = r2
        r_long = r3
    else:
        r_short = r3
        r_long = r1

    print(f"r_short: {r_short}; r_long: {r_long}")

    l = (r_long**2 - r_short**2) / (2 * size["netStep"]) - (size["netStep"] / 2)
    h = math.sqrt(r_short**2-l**2)
    print(f"l: {l} h: {h}")
    y = 0
    x = 0
    # зачепи на одній лінії, горизонтальне розміщення
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
            x = x2 + l
        print(f"CENTER x: {x}, y: {y}")
    # зачепи на одні лінії, вертикальне розміщення
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
        print(f"CENTER x: {x}, y: {y}")
    # зачепи не на одній лінії
    else:
        x, y = calculate_center_three_points(x1, y1, x2, y2, x3, y3, r1, r2, r3)
    return x, y


def calculate_center_(x1, y1, x2, y2, x3, y3, r1, r2, r3):
    # print("---")
    # print(f"START x1: {x1} y1: {y1} x2: {x2} y2: {y2} x3: {x3} y3: {y3}")
    #todo ensure that x1y1 and x2y2 are neighbouring
    are_12_neighbours = are_neighbours(x1, y1, x2, y2)
    are_23_neighbours = are_neighbours(x2, y2, x3, y3)
    are_13_neighbours = are_neighbours(x1, y1, x3, y3)
    l, s, h = -1, -1, -1
    if are_12_neighbours:
        l = dist(x1, y1, x2, y2)
        s = (r1 + r2 + l) / 2
        # print(f"r1: {r1} r2: {r2} l: {l} s: {s}")
        h = round((2 * math.sqrt(s * (s - r1) * (s - r2) * (s - l)) / l), 10)  # altitude
    elif are_23_neighbours:
        l = dist(x2, y2, x3, y3)
        s = (r2 + r3 + l) / 2
        # print(f"r1: {r1} r2: {r2} l: {l} s: {s}")
        h = round((2 * math.sqrt(s * (s - r2) * (s - r3) * (s - l)) / l), 10)  # altitude
    elif are_13_neighbours:
        l = dist(x1, y1, x3, y3)
        s = (r1 + r3 + l) / 2
        # print(f"r1: {r1} r2: {r2} l: {l} s: {s}")
        h = round((2 * math.sqrt(s * (s - r1) * (s - r3) * (s - l)) / l), 10)  # altitude
    else:
        print("Something is wrong, no neighbouring points")
        return -1

    # l = dist(x1, y1, x2, y2)
    # s = (r1 + r2 + l) / 2
    print(f"r1: {r1} r2: {r2} l: {l} s: {s}")
    # h = round((2 * math.sqrt(s * ( s - r1 ) * ( s - r2 ) * (s - l)) / l), 10) # altitude
    print(f"H: {h}")

    # find the right triangle where r1 - hypotenuse and h - one of the legs
    x = x1
    y = y1
    r = r1
    d = math.sqrt(r**2 - h**2) # the second leg; on the holders line
    print(f"d: {d}")

    # find the angle between the horizontal of the ceiling and the robot line
    x_r_vector, y_r_vector = get_vector_coords(x1, y1, x2, y2) # vector of robot line
    # print(f"ROBOT VECTOR x: {x_r_vector} y: {y_r_vector}")
    x_horizontal = 5 # horizontal vector
    y_horizontal = 0
    # 09.08 REMOVED "-" FOR angle_between_vectors
    shift_angle = normalize(-angle_between_vectors(x_horizontal, y_horizontal, x_r_vector, y_r_vector)) # TODO invert + ?
    print(f"shift angle: {shift_angle}")

    # if robot is facing down or left, modify the angle

    x_rotated, y_rotated = rotate_point(x, y, x2, y2, shift_angle)
    print(f"ROTATED x: {x_rotated} y: {y_rotated}")

    x_rotated_vector, y_rotated_vector = get_vector_coords(x2, y2, x_rotated, y_rotated)  # vector of robot line
    # print(f"ROTATED VECTOR x: {x_rotated_vector} y: {y_rotated_vector}")
    #hand_angle = angle_between_vectors(x_rotated_vector, y_rotated_vector, x_horizontal, y_horizontal)
    hand_angle = math.degrees(math.acos((r1**2 + l**2 - r2**2) / (2 * r1 * l)))
    print(f"HAND ANGLE: {hand_angle}")

    if hand_angle > 90:
        # print("minus")
        ox_ = x_rotated - d
    else:
        # print("plus")
        ox_ = x_rotated + d
    oy_ = y_rotated - h
    print(f"ROTATED O x: {ox_} y: {oy_}")

    ox, oy = rotate_point(ox_, oy_, x2, y2, normalize(-shift_angle))
    print(f"UNROTATED O x: {ox} y: {oy}")

    return ox, oy

def get_shift_angle(x1, y1, x2, y2, x3, y3, r1, r2, r3):

    # print("---")
    # print(f"START x1: {x1} y1: {y1} x2: {x2} y2: {y2} x3: {x3} y3: {y3}")
    l = dist(x1, y1, x2, y2)
    s = (r1 + r2 + l) / 2
    # print(f"r1: {r1} r2: {r2} l: {l} s: {s}")
    h = 2 * math.sqrt(s * (s - r1) * (s - r2) * (s - l)) / l  # altitude
    # print(f"H: {h}")

    # find the right triangle where r1 - hypotenuse and h - one of the legs
    x = x1
    y = y1
    r = r1
    d = math.sqrt(r ** 2 - h ** 2)  # the second leg; on the holders line
    # print(f"d: {d}")

    # find the angle between the horizontal of the ceiling and the robot line
    x_r_vector, y_r_vector = get_vector_coords(x1, y1, x2, y2)  # vector of robot line
    # print(f"ROBOT VECTOR x: {x_r_vector} y: {y_r_vector}")
    x_horizontal = 5  # horizontal vector
    y_horizontal = 0
    shift_angle = angle_between_vectors(x_horizontal, y_horizontal, x_r_vector, y_r_vector)
    return shift_angle

# for when holders are NOT on one line
def calculate_center_three_points(x1, y1, x2, y2, x3, y3, r1, r2, r3):
    # eps = 1e-6
    # eps = 0.003
    eps = 20 # TODO find the suitable eps
    # print(f"START x1: {x1} y1: {y1} x2: {x2} y2: {y2} x3: {x3} y3: {y3}")
    # print(f"r1: {r1} r2: {r2}")
    if (2 * ((y3 - y2) * (x1 - x2) - (y2 - y1) * (x2 - x3)) == 0) or (
            (2 * ((x3 - x2) * (y1 - y2) - (x2 - x1) * (y2 - y3))) == 0):
        return -1, -1

    x = (((y2 - y1) * (r2 * r2 - r3 * r3 - y2 * y2 + y3 * y3 - x2 * x2 + x3 * x3) - (y3 - y2) *
          (r1 * r1 - r2 * r2 - y1 * y1 + y2 * y2 - x1 * x1 + x2 * x2)) /
         (2 * ((y3 - y2) * (x1 - x2) - (y2 - y1) * (x2 - x3))))
    y = (((x2 - x1) * (r2 * r2 - r3 * r3 - x2 * x2 + x3 * x3 - y2 * y2 + y3 * y3) - (x3 - x2) *
          (r1 * r1 - r2 * r2 - x1 * x1 + x2 * x2 - y1 * y1 + y2 * y2)) /
         (2 * ((x3 - x2) * (y1 - y2) - (x2 - x1) * (y2 - y3))))
    # print("x=" + str(x) + " y=" + str(y))
    # print(f"abs = {abs((x1 - x) * (x1 - x) + (y1 - y) * (y1 - y) - r1 * r1)}")
    if abs((x1 - x) * (x1 - x) + (y1 - y) * (y1 - y) - r1 * r1) < eps:
        # print("x=" + str(x) + " y=" + str(y))
        return x, y
    # else:
        # print(f"x1: {x1} y1: {y1} | x2: {x2} y2: {y2} | x3: {x3} y3: {y3} | r1: {r1} r2: {r2} r3: {r3}")
        # print(f"x: {x} y: {y}")
        # print("Impossible")
    return -1, -1

def center_by_params(hand_coords, shift_1, shift_2, shift_3):
    center_x, center_y = -1, -1
    try:
        if is_aligned(hand_coords):
            center_x, center_y = calculate_center([(hand_coords[0][0], hand_coords[0][1]),
                                                   (hand_coords[1][0], hand_coords[1][1]),
                                                   (hand_coords[2][0], hand_coords[2][1])],
                                                  [shift_1, shift_2, shift_3])
        else:
            center_x, center_y = calculate_center_three_points(hand_coords[0][0], hand_coords[0][1],
                                                               hand_coords[1][0], hand_coords[1][1],
                                                               hand_coords[2][0], hand_coords[2][1],
                                                               shift_1, shift_2, shift_3)
        return center_x, center_y
    except:
        return -1, -1

def rotate_point(px, py, qx, qy, theta):
    # print(f"px {px} py {py} qx {qx} qy {qy}")
    px_ = px - qx
    py_ = py - qy
    # print(f"P' x: {px_} y: {py_}")
    px_rotated = px_ * dcos(theta) - py_ * dsin(theta)
    py_rotated = px_ * dsin(theta) + py_ * dcos(theta)
    # print(f"P rotated x: {px_rotated} y: {py_rotated}")
    rx = px_rotated + qx
    ry = py_rotated + qy
    # print(f"R x: {rx} y: {ry}")
    return rx, ry

def middle_point(p1, p2, p3):
    # Extract x and y coordinates
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # Check if points are collinear
    # (y2 - y1) / (x2 - x1) should be equal to (y3 - y1) / (x3 - x1)
    # To avoid division by zero, use cross multiplication
    print("outside")
    if (-y2 + y1) * (x3 - x1) == (-y3 + y1) * (x2 - x1):
        # Create a list of the points
        print("inside")
        orig_points = [p1, p2, p3]
        points = [p1, p2, p3]
        print(f"unsorted points: {points}")

        # Sort points by their x-coordinates first, and y-coordinates as tie-breaker
        points.sort(key=lambda point: (point[0], point[1]))
        print(f"sorted points: {points}")
        middle_coord = points[1]
        print(f"middle coord: {middle_coord}")
        for i in range(3):
            if middle_coord[0] == orig_points[i][0] and middle_coord[1] == orig_points[i][1]:
                print(f"middle: {i}")
                return i

        # The middle point after sorting will be the one in between
        return -1
    else:
        return -1

def dist(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y1 - y2) # TODO invert +

def dists(x1, y1, x2, y2, x3, y3, xc, yc):
    return [dist(x1, y1, xc, yc), dist(x2, y2, xc, yc), dist(x3, y3, xc, yc)]

def get_line_equation(x1, y1, x2, y2):
    a = y1 - y2
    b = x2 - x1
    c = x1*y2 - x2*y1
    return a, b, c

def get_point_on_dist(x1, y1, x2, y2, d):
    print(f"x1: {x1} y1: {y1} x2: {x2} y2: {y2} d: {d}")
    ab = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    print(f"AB: {ab}")
    if ab<=d:
        return x2, y2
    l = d / (ab - d)
    x_n = (x1 + l * x2) / (1 + l)
    y_n = (y1 + l * y2) / (1 + l)

    return x_n, y_n

def get_dist_point_line(x, y, a, b, c):
    d = abs(a*x + b*y + c)/math.sqrt(a**2 + b**2)
    return d

def get_vector_coords(x1, y1, x2, y2):
    # return x2 - x1, y1 - y2
    return x2 - x1, y1 - y2 # TODO invert +

def get_abs_vector(x, y):
    return math.sqrt(x**2 + y**2)

def get_head_vector(a, ang_a, b, ang_b, xa, ya, xb, yb):
    v = a * dcos(ang_a)
    w = b * dcos(ang_b)

    '''x_robot_head = 1
    y_robot_head = (v - xa * x_robot_head) / ya'''

    x_robot_head = 0
    y_robot_head = 0
    
    if (ya * xb - xa * yb) != 0:
        x_robot_head = (-yb * v + ya * w) / (ya * xb - xa * yb)
        y_robot_head = (-xb * v + xa * w) / (ya * xb - xa * yb)
    else:
        y_robot_head = 1
        x_robot_head = (v / xa) - (ya / xa) * y_robot_head

    return x_robot_head, y_robot_head

# computes clockwise angle between two vectors
# with inverted Y axis in calculations, this func MUST return CLOCKWISE angle;
# other option - normal Y and counterclockwise func return - for this change params to (xb, yb, xa, ya)
def angle_between_vectors(xa, ya, xb, yb):
    # print("--- get angle ---")
    dot_product = xa * xb + ya * yb
    cross_product = xa * yb - ya * xb
    # print(f"dot: {dot_product}; cross: {cross_product}")
    angle_rad = math.atan2(-cross_product, -dot_product) + math.pi
    # print(f"Angle in rad: {angle_rad}")
    angle_deg = math.degrees(angle_rad) # *-1 because of inverted y # TODO INVERTED
    # print(f"Angle in deg: {angle_deg}")
    angle_deg = normalize(angle_deg)
    # print(f"Normalized angle: {angle_deg}")
    return angle_deg

def area(x1, y1, x2, y2, x3, y3):
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)

def isInside(x1, y1, x2, y2, x3, y3, x, y):
    a = area(x1, y1, x2, y2, x3, y3)
    a1 = area(x, y, x2, y2, x3, y3)
    a2 = area(x1, y1, x, y, x3, y3)
    a3 = area(x1, y1, x2, y2, x, y)
    return a == (a1 + a2 + a3)

def mirroring_check(ang1, ang2, ang3):
    if (ang1 < ang2 < ang3) or (
            ang2 < ang3 < ang1) or (
            ang3 < ang1 < ang2):
        return True
    return False

def is_in_three_hands_area(x1, y1, x2, y2, x3, y3, xo, yo):
    # print("IN CONDITION CHECK")
    dist_arr = dists(x1, y1, x2, y2, x3, y3, xo, yo)
    # print(dist_arr)
    if (dist_arr[0] > size["outerRadLimit"] or dist_arr[0] < size["innerRadLimit"]) or (
            dist_arr[1] > size["outerRadLimit"] or dist_arr[1] < size["innerRadLimit"]) or (
            dist_arr[2] > size["outerRadLimit"] or dist_arr[2] < size["innerRadLimit"]):
        return False
    # xa, ya = get_vector_coords(x1, y1, xo, yo) # TODO invert +
    # xb, yb = get_vector_coords(x2, y2, xo, yo)
    # xc, yc = get_vector_coords(x3, y3, xo, yo)

    xa, ya = get_vector_coords(xo, yo, x1, y1) # (xo, yo) - start point, (xN, yN) - end point
    xb, yb = get_vector_coords(xo, yo, x2, y2)
    xc, yc = get_vector_coords(xo, yo, x3, y3)

    aob = angle_between_vectors(xa, ya, xb, yb)
    boc = angle_between_vectors(xb, yb, xc, yc)
    coa = angle_between_vectors(xc, yc, xa, ya)

    # print(f"ANGS FOR REACH ZONE: aob: {aob} boc: {boc} coa: {coa}")

    if (aob < size["minAngle"] or (360-aob) < size["minAngle"]) or (
            boc < size["minAngle"] or (360-boc) < size["minAngle"]) or (
            coa < size["minAngle"] or (360-coa) < size["minAngle"]):
        return False
    # TODO check if the conditions will be met while moving the center
    return True

def is_in_two_hands_area(x1, y1, x2, y2, xo, yo):
    # print("2hands: IN CONDITION CHECK")
    dist_arr = [dist(x1, y1, xo, yo), dist(x2, y2, xo, yo)]
    if (dist_arr[0] > size["outerRadLimit"] or dist_arr[0] < size["innerRadLimit"]) or (
            dist_arr[1] > size["outerRadLimit"] or dist_arr[1] < size["innerRadLimit"]):
        return False
    # xa, ya = get_vector_coords(x1, y1, xo, yo) # TODO invert +
    # xb, yb = get_vector_coords(x2, y2, xo, yo)

    xa, ya = get_vector_coords(xo, yo, x1, y1)
    xb, yb = get_vector_coords(xo, yo, x2, y2)

    aob = angle_between_vectors(xa, ya, xb, yb)

    # print(f"ANGS FOR REACH ZONE: aob: {aob}")

    if aob < size["minAngle"] or (360-aob) < size["minAngle"]:
        return False
    # TODO check if the conditions will be met while moving the center
    return True

def is_limited_by_others(x1, y1, x2, y2, x3, y3, xo, yo, hand_num):
    # print("IN LIMITATION CHECK")
    dist_arr = dists(x1, y1, x2, y2, x3, y3, xo, yo)
    # print(dist_arr)
    if (dist_arr[0] > size["outerRadLimit"] or dist_arr[0] < size["innerRadLimit"]) or (
            dist_arr[1] > size["outerRadLimit"] or dist_arr[1] < size["innerRadLimit"]) or (
            dist_arr[2] > size["outerRadLimit"] or dist_arr[2] < size["innerRadLimit"]):
        # print("false")
        return False
    # xa, ya = get_vector_coords(x1, y1, xo, yo) # TODO invert +
    # xb, yb = get_vector_coords(x2, y2, xo, yo)
    # xc, yc = get_vector_coords(x3, y3, xo, yo)

    xa, ya = get_vector_coords(xo, yo, x1, y1)
    xb, yb = get_vector_coords(xo, yo, x2, y2)
    xc, yc = get_vector_coords(xo, yo, x3, y3)

    aob = angle_between_vectors(xa, ya, xb, yb)
    boc = angle_between_vectors(xb, yb, xc, yc)
    coa = angle_between_vectors(xc, yc, xa, ya)

    limited_hand = -1
    if aob + coa <= 360 - (aob + coa):
        # print(f"hand: 0; angle: {aob + coa}")
        limited_hand = 0
    if aob + boc <= 360 - (aob + boc):
        # print(f"hand: 1; angle: {aob + boc}")
        limited_hand = 1
    if boc + coa <= 360 - (boc + coa):
        # print(f"hand: 2; angle: {boc + coa}")
        limited_hand = 2

    if limited_hand == -1:
        # print("false")
        return False

    if limited_hand == hand_num:
        # print("true")
        return True

    # print("false")
    return False

def optimal_points(a, b, c):
    x_start, y_start = 100, 100
    max_dist = size["netStep"] * math.sqrt(2) * 2
    opt_points = []
    for y_step in range(10):
        for x_step in range(10):
            x = x_start + size["netStep"] * x_step
            y = y_start + size["netStep"] * y_step
            d = abs(a * x + b * y + c) / math.sqrt(a**2 + b**2)
            if d <= max_dist:
                opt_points.append((x, y))
    return opt_points

def is_aligned(hand_coords):
    # print(f"In is_aligned: {hand_coords}")
    if is_horizontal_aligned(hand_coords) or is_vertical_aligned(hand_coords):
        # print("- horizontal or vertical -")
        return True
    Tol = 1e-10
    if (hand_coords[0][0] == hand_coords[2][0] and hand_coords[0][0] != hand_coords[1][0]) or (
            hand_coords[1][0] == hand_coords[2][0] and hand_coords[1][0] != hand_coords[0][0]) or (
            hand_coords[0][0] == hand_coords[1][0] and hand_coords[0][0] != hand_coords[2][0]):
        # print("- not aligned -")
        return False
    if (hand_coords[0][1] == hand_coords[2][1] and hand_coords[0][1] != hand_coords[1][1]) or (
            hand_coords[1][1] == hand_coords[2][1] and hand_coords[1][1] != hand_coords[0][1]) or (
            hand_coords[0][1] == hand_coords[1][1] and hand_coords[0][1] != hand_coords[2][1]):
        # print("- not aligned -")
        return False
    if abs((hand_coords[2][0] - hand_coords[0][0]) / (hand_coords[1][0] - hand_coords[0][0]) -
           (hand_coords[2][1] - hand_coords[0][1]) / (hand_coords[1][1] - hand_coords[0][1])) <= Tol:
        # print("- aligned -")
        return True
    # print("- not aligned -")
    return False

def is_aligned_stable(hand_coords):
    # Sort the dots based on their coordinates
    dots = sorted([(hand_coords[0][0], hand_coords[0][1]),
                   (hand_coords[1][0], hand_coords[1][1]),
                   (hand_coords[2][0], hand_coords[2][1])])
    (x1, y1), (x2, y2), (x3, y3) = dots

    # Check for a horizontal line with adjacent dots
    if x1 + size["netStep"] == x2 == x3 - size["netStep"] and y1 == y2 == y3:
        return True

    # Check for a vertical line with adjacent dots
    elif y1 + size["netStep"] == y2 == y3 - size["netStep"] and x1 == x2 == x3:
        return True

    # Check for L-position
    elif (x1 == x2 and y2 == y3 and x3 == x2 + size["netStep"] and y1 == y2 - size["netStep"]) or \
            (x1 == x2 and y2 == y3 and x3 == x2 - size["netStep"] and y1 == y2 + size["netStep"]) or \
            (y1 == y2 and x2 == x3 and y3 == y2 + size["netStep"] and x1 == x2 - size["netStep"]) or \
            (y1 == y2 and x2 == x3 and y3 == y2 - size["netStep"] and x1 == x2 + size["netStep"]):
        return True
    return False

def are_neighbours(x1, y1, x2, y2):
    # Sort the dots based on their coordinates
    dots = sorted([(x1, y1),
                   (x2, y2)])
    (x1, y1), (x2, y2) = dots

    # Check for a horizontal line with adjacent dots
    if (x1 + size["netStep"] == x2 and y1 == y2) or \
            (x1 - size["netStep"] == x2 and y1 == y2) or \
            (y1 + size["netStep"] == y2 and x1 == x2) or \
            (y1 - size["netStep"] == y2 and x1 == x2):
        return True
    return False

def is_horizontal_aligned(hand_coords):
    if (hand_coords[0][1] == hand_coords[1][1] and
            hand_coords[1][1] == hand_coords[2][1]):
        return True
    return False

def is_vertical_aligned(hand_coords):
    if (hand_coords[0][0] == hand_coords[1][0] and
            hand_coords[1][0] == hand_coords[2][0]):
        return True
    return False

def normalize(a):
    if 0 > a > -0.00001:
        return 0
    elif a >= 360:
        return a - 360*int(a/360)
    elif a < 0:
        return a - 360*(int(a/360)-1)
    return a

def  clockwise(delta):
    d = round(delta, 3)
    if d > 0 or d < -360:
        delta = delta - 360 * (math.floor(delta / 360) + 1)
    return delta

def counterclockwise(delta):
    d = round(delta, 3)
    if d > 360 or d < 0:
        delta = delta - 360 * math.floor(delta / 360)
    return delta

def dsin(angle):
  return math.sin(math.radians(angle))

def dcos(angle):
  return math.cos(math.radians(angle))

def darctan(tan):
  return math.degrees(math.atan2(tan,1))


# обчислення параметрів для рук при русі вперед (n-тий підкрок)
def calc_params_forward(L, N, n, h, aa0, hand_a, hand_b, hand_c):
    anglestep_c = (360 - (math.atan2(L, h) / math.pi * 180) * 2) / N

    # Рука С при прольоті не змінює, їй це не потрібно
    sa = math.sqrt((L / N * n) ** 2 + h ** 2)
    sb = math.sqrt((L - L / N * n) ** 2 + h ** 2)
    sc = math.sqrt(L ** 2 + h ** 2)

    # ЗАЧЕП руки, що пролітає (С)
    hc = 1
    if n < N:
        hc = 0

    # кути рахуються ЗА годинниковою стрілкою
    # aa = math.atan2(L*n/N/h,1)/math.pi*180+aa0;               if (aa>360) { aa-=360 } if (aa<0) { aa+=360 }
    # ab = 360-math.atan2((L-L*n/N)/h,1)/math.pi*180+aa0;      if (ab>360) { ab-=360 } if (ab<0) { ab+=360 }
    # ac = math.atan2(L/h,1)/math.pi*180 + n*anglestep_c + aa0; if (ac>360) { ac-=360 } if (ac<0) { ac+=360 }

    # кути рахуються ПРОТИ годинникової стрілки
    aa = 360 - math.atan2(L * n / N, h) / math.pi * 180 + aa0
    if aa > 360:
        aa -= 360
    elif aa < 0:
        aa += 360  # 360->283

    ab = math.atan2((L - L * n / N), h) / math.pi * 180 + aa0
    if ab > 360:
        ab -= 360
    elif ab < 0:
        ab += 360  # 76->0

    ac = 360 - math.atan2(L, h) / math.pi * 180 - n * anglestep_c + aa0
    if ac > 360:
        ac -= 360
    elif ac < 0:
        ac += 360  # 283->76 through 180

    shifts = [0.0, 0.0, 0.0]
    shifts[hand_a] = sa
    shifts[hand_b] = sb
    shifts[hand_c] = sc

    angs = [0.0, 0.0, 0.0]
    angs[hand_a] = aa
    angs[hand_b] = ab
    angs[hand_c] = ac

    holds = [0, 0, 0]
    holds[hand_a] = 1
    holds[hand_b] = 1
    holds[hand_c] = hc

    return shifts, angs, holds


def calc_params_backward(L, N, n, h, aa0, hand_a, hand_b, hand_c):
    anglestep_b = (360 - (math.atan2(L / h, 1) / math.pi * 180) * 2) / N

    # Рука B при прольоті не змінює, їй це не потрібно
    sa = math.sqrt((L / N * n) ** 2 + h ** 2)
    sb = math.sqrt(L ** 2 + h ** 2)
    sc = math.sqrt((L - L / N * n) ** 2 + h ** 2)

    # ЗАЧЕП руки, що пролітає (B)
    hb = 1
    if n < N:
        hb = 0

    # кути рахуються ПРОТИ годинникової стрілки
    aa = math.atan2(L * n / N / h, 1) / math.pi * 180 + aa0
    if aa > 360:
        aa -= 360
    elif aa < 0:
        aa += 360  # 360->283

    ac = 360 - math.atan2((L - L * n / N) / h, 1) / math.pi * 180 + aa0
    if ac > 360:
        ac -= 360
    elif ac < 0:
        ac += 360  # 76->0

    ab = math.atan2(L / h, 1) / math.pi * 180 + n * anglestep_b + aa0
    if ab > 360:
        ab -= 360
    elif ab < 0:
        ab += 360  # 283->76 through 180

    shifts = [0.0, 0.0, 0.0]
    shifts[hand_a] = sa
    shifts[hand_b] = sb
    shifts[hand_c] = sc

    angs = [0.0, 0.0, 0.0]
    angs[hand_a] = aa
    angs[hand_b] = ab
    angs[hand_c] = ac

    holds = [0, 0, 0]
    holds[hand_a] = 1
    holds[hand_b] = hb
    holds[hand_c] = 1

    return shifts, angs, holds

def to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                  - outMin))

def get_ceil_coords(x, y, rect_side, outer_border, outer_border_add):
    ceil_x = size["netBorder"] + x * size["netStep"]
    ceil_y = size["netBorder"] + y * size["netStep"]
    fin_x = to_range(ceil_x, 0, size["ceilLenX"], 0, rect_side) + outer_border_add
    fin_y = to_range(ceil_y, 0, size["ceilLenY"], 0, rect_side) + outer_border_add
    return fin_x, fin_y

def get_visual_coords(x, y, rect_side, outer_border, outer_border_add):
    fin_x = to_range(x, 0, size["ceilLenX"], 0, rect_side) + outer_border_add
    fin_y = to_range(y, 0, size["ceilLenY"], 0, rect_side) + outer_border_add
    return fin_x, fin_y



# def get_ang(x1, y1, xc, yc):
#     ax = x1 - xc
#     ay = y1 - yc
#     # bx = 10 # b is calculated from point on the line of the center
#     # by = 0
#
#     # ang = math.acos((ax*bx + ay*by)/(math.sqrt(ax**2+ay**2)*math.sqrt(bx**2+by**2)))
#     ang = math.acos((ax * 10) / (math.sqrt(ax ** 2 + ay ** 2) * 10))
#     if y1 > yc:
#         ang = 360 - ang
#
#     return ang
#
#
# xn, yn - hand coordinates; a,b,c - line equation for robot movement (can be replaced with desired_center)
# def calculate_new_shifts(x1, y1, x2, y2, x3, y3, a, b, c, min_shift, max_shift):
#     # eps = 1e-6
#     eps = 1
#
#     x1 = size["netBorder"] + x1 * size["netStep"]
#     y1 = size["netBorder"] + y1 * size["netStep"]
#
#     x2 = size["netBorder"] + x2 * size["netStep"]
#     y2 = size["netBorder"] + y2 * size["netStep"]
#
#     x3 = size["netBorder"] + x3 * size["netStep"]
#     y3 = size["netBorder"] + y3 * size["netStep"]
#
#     new_shift1 = 0
#     new_shift2 = 0
#     new_shift3 = 0
#     new_center_x = 0
#     new_center_y = 0
#
#     # простий перебір, поки підібраний центр не потрапить у прийнятний інтервал значень
#     for shift1 in range(min_shift, max_shift, 0.1):
#         for shift2 in range(min_shift, max_shift, 0.1):
#             for shift3 in range(min_shift, max_shift, 0.1):
#                 center_x, center_y = calculate_center(x1, y1, x2, y2, x3, y3, shift1, shift2, shift3)
#                 if get_dist_point_line(center_x, center_y, a, b, c) <= eps:
#                     new_shift1 = shift1
#                     new_shift2 = shift2
#                     new_shift3 = shift3
#                     new_center_x = center_x
#                     new_center_y = center_y
#                     break
#             if new_shift1 != 0:
#                 break
#         if new_shift1 != 0:
#             break
#     new_ang1 = get_ang(x1, y1, new_center_x, new_center_y)
#     new_ang2 = get_ang(x2, y2, new_center_x, new_center_y)
#     new_ang3 = get_ang(x3, y3, new_center_x, new_center_y)
#     return {new_shift1, new_ang1, new_shift2, new_ang2, new_shift3, new_ang3}

# розміри стелі + лап робота
size = {
    #"innerRadLimit": 48,  # min shift pos
    "innerRadLimit": 47,  # min shift pos # TODO NORMAL CALCULATION FOR REACH ZONE
    "outerRadLimit": 220,  # max shift pos
    "minAngle": 68,
    "netStep": 200,
    "ceilLenX": 2000,
    "ceilLenY": 2000,
    "netBorder": 100,
    # "D2": 400,
    # "d2": 200*math.sqrt(3),
    "holeRad": 40
}

# arm_state = get_arm_state_by_pos(7, size, 'b')
# print(arm_state)

# arm_state = get_arm_state_by_pos(200, size, 'g')
# print(arm_state)
#
# arm_state = get_arm_state_by_pos(-200, size, 'b')
# print(arm_state)
