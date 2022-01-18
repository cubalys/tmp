def get_oblong_error_score(h_w_ratio, lw_ratio, chin_ratio, forehead_ratio):
    base_h_w_ratio_min = 1.45
    base_lw_ratio_min = 0.83
    base_lw_ratio_max = 0.88
    base_chin_ratio_min = 0.23
    base_forehead_ratio_max = 0.24

    error = 0

    if h_w_ratio < base_h_w_ratio_min:
        error += (base_h_w_ratio_min - h_w_ratio) ** 2

    if lw_ratio < base_lw_ratio_min:
        error += (base_lw_ratio_min - lw_ratio) ** 2
    elif lw_ratio > base_lw_ratio_max:
        error += (lw_ratio - base_lw_ratio_max) ** 2

    if chin_ratio < base_chin_ratio_min:
        error += (base_chin_ratio_min - chin_ratio) ** 2

    if forehead_ratio > base_forehead_ratio_max:
        error += (forehead_ratio - base_forehead_ratio_max) ** 2

    error *= 10000
    print(f'oblong error : {error}')
    return error


def get_oval_error_score(h_w_ratio, lw_ratio, chin_ratio):
    base_h_w_ratio_min = 1.39
    base_h_w_ratio_max = 1.44
    base_lw_ratio_min = 0.75
    base_lw_ratio_max = 0.85
    base_chin_ratio = 0.22

    error = 0

    if h_w_ratio < base_h_w_ratio_min:
        error += (base_h_w_ratio_min - h_w_ratio) ** 2
    elif h_w_ratio > base_h_w_ratio_max:
        error += (h_w_ratio - base_h_w_ratio_max) ** 2

    if lw_ratio < base_lw_ratio_min:
        error += (base_lw_ratio_min - lw_ratio) ** 2
    elif lw_ratio > base_lw_ratio_max:
        error += (lw_ratio - base_lw_ratio_max) ** 2

    error += (base_chin_ratio - chin_ratio) ** 2

    error *= 10000
    print(f'oval error : {error}')
    return error


def get_round_error_score(h_w_ratio, lw_ratio, chin_ratio):
    base_h_w_ratio_min = 1.30
    base_h_w_ratio_max = 1.35
    base_lw_ratio_min = 0.79
    base_lw_ratio_max = 0.82
    base_chin_ratio_max = 0.19

    error = 0

    if h_w_ratio < base_h_w_ratio_min:
        error += (base_h_w_ratio_min - h_w_ratio) ** 2
    elif h_w_ratio > base_h_w_ratio_max:
        error += (h_w_ratio - base_h_w_ratio_max) ** 2

    if lw_ratio < base_lw_ratio_min:
        error += (base_lw_ratio_min - lw_ratio) ** 2
    elif lw_ratio > base_lw_ratio_max:
        error += (lw_ratio - base_lw_ratio_max) ** 2

    if chin_ratio > base_chin_ratio_max:
        error += (chin_ratio - base_chin_ratio_max) ** 2

    error *= 10000
    print(f'round error : {error}')
    return error


def get_square_error_score(h_w_ratio, lw_ratio, chin_ratio):
    base_h_w_ratio_min = 1.30
    base_h_w_ratio_max = 1.38
    base_lw_ratio_min = 0.85
    base_chin_ratio_max = 0.21

    error = 0

    if h_w_ratio < base_h_w_ratio_min:
        error += (base_h_w_ratio_min - h_w_ratio) ** 2
    elif h_w_ratio > base_h_w_ratio_max:
        error += (h_w_ratio - base_h_w_ratio_max) ** 2

    if lw_ratio < base_lw_ratio_min:
        error += (base_lw_ratio_min - lw_ratio) ** 2

    if chin_ratio > base_chin_ratio_max:
        error += (chin_ratio - base_chin_ratio_max) ** 2

    error *= 10000
    print(f'square error : {error}')
    return error


def get_error_score(h_w_ratio, lw_ratio, chin_ratio, forehead_ratio):
    print(f'chin : {chin_ratio}')
    oblong_error_score = get_oblong_error_score(h_w_ratio, lw_ratio, chin_ratio, forehead_ratio)
    oval_error_score = get_oval_error_score(h_w_ratio, lw_ratio, chin_ratio)
    round_error_score = get_round_error_score(h_w_ratio, lw_ratio, chin_ratio)
    square_error_score = get_square_error_score(h_w_ratio, lw_ratio, chin_ratio)

    return {'oblong': oblong_error_score, 'oval': oval_error_score, 'round': round_error_score,
            'square': square_error_score}
