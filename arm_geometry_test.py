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


size = {
    "innerRadLimit": 48,  # min shift pos
    "outerRadLimit": 210,  # max shift pos
    "netStep": 200
}

# arm_state = get_arm_state_by_pos(7, size, 'b')
# print(arm_state)

# arm_state = get_arm_state_by_pos(200, size, 'g')
# print(arm_state)
#
# arm_state = get_arm_state_by_pos(-200, size, 'b')
# print(arm_state)
