import math


def calc_distance(p1_x, p1_y, p2_x, p2_y):
    return math.sqrt((p2_x - p1_x) ** 2 + (p2_y - p1_y) ** 2)


def get_symmetric_hairline_point(response, left_point_idx, target_gradient):
    left_x = response['face']['landmark']['face']['face_hairline_' + str(left_point_idx)]['x']
    left_y = response['face']['landmark']['face']['face_hairline_' + str(left_point_idx)]['y']

    min_gradient_gap = 9999.0
    min_gap_idx = -1
    start = 0 + (144 - left_point_idx) - 10
    end = 0 + (144 - left_point_idx) + 10
    for i in range(start, end, 1):
        if i < 0 or i > 144:
            continue
        right_x = response['face']['landmark']['face']['face_hairline_' + str(i)]['x']
        right_y = response['face']['landmark']['face']['face_hairline_' + str(i)]['y']
        gradient = (right_y - left_y) / (right_x - left_x)

        gap = abs(gradient - target_gradient)
        if gap < min_gradient_gap:
            min_gradient_gap = gap
            min_gap_idx = i

    return min_gap_idx


def get_symmetric_contour_point(response, left_point_idx, target_gradient):
    left_x = response['face']['landmark']['face']['face_contour_left_' + str(left_point_idx)]['x']
    left_y = response['face']['landmark']['face']['face_contour_left_' + str(left_point_idx)]['y']

    min_gradient_gap = 9999.0
    min_gap_idx = -1
    start = left_point_idx - 10
    end = left_point_idx + 10
    for i in range(start, end, 1):
        if i < 0 or i > 144:
            continue
        right_x = response['face']['landmark']['face']['face_contour_right_' + str(i)]['x']
        right_y = response['face']['landmark']['face']['face_contour_right_' + str(i)]['y']
        gradient = (right_y - left_y) / (right_x - left_x)

        gap = abs(gradient - target_gradient)
        if gap < min_gradient_gap:
            min_gradient_gap = gap
            min_gap_idx = i

    return min_gap_idx


def find_lower_left_idx(response):
    upper_lip_mid_y = response['face']['landmark']['mouth']['upper_lip_47']['y']
    low_lip_mid_y = response['face']['landmark']['mouth']['lower_lip_47']['y']
    lip_mid_y = (upper_lip_mid_y + low_lip_mid_y) / 2
    most_gap_y_idx = 10
    for i in range(10, 41, 1):
        min_gap_y = response['face']['landmark']['face']['face_contour_left_' + str(most_gap_y_idx)]['y']
        current_y = response['face']['landmark']['face']['face_contour_left_' + str(i)]['y']
        if abs(lip_mid_y - min_gap_y) > abs(lip_mid_y - current_y):
            most_gap_y_idx = i

    return most_gap_y_idx


def find_mid_idx(response):
    max_distance = 0
    ret_i = 45
    for i in range(45, 63, 1):
        current_left_x = response['face']['landmark']['face']['face_contour_left_' + str(i)]['x']
        current_left_y = response['face']['landmark']['face']['face_contour_left_' + str(i)]['y']
        current_right_x = response['face']['landmark']['face']['face_contour_right_' + str(i)]['x']
        current_right_y = response['face']['landmark']['face']['face_contour_right_' + str(i)]['y']
        distance = calc_distance(current_left_x, current_left_y, current_right_x, current_right_y)
        if distance > max_distance:
            max_distance = distance
            ret_i = i
    return ret_i, ret_i


def get_face_data(response):
    top_x = (response['face']['landmark']['face']['face_hairline_72']['x']
             + response['face']['landmark']['face']['face_hairline_73']['x']) / 2
    top_y = (response['face']['landmark']['face']['face_hairline_72']['y']
             + response['face']['landmark']['face']['face_hairline_73']['y']) / 2
    bottom_x = (response['face']['landmark']['face']['face_contour_left_0']['x']
                + response['face']['landmark']['face']['face_contour_right_0']['x']) / 2
    bottom_y = (response['face']['landmark']['face']['face_contour_left_0']['y']
                + response['face']['landmark']['face']['face_contour_right_0']['y']) / 2
    height = calc_distance(top_x, top_y, bottom_x, bottom_y)

    mid_left_idx, mid_right_idx = find_mid_idx(response)
    print(f'mid index : {mid_left_idx} to {mid_right_idx}')
    mid_left_x = response['face']['landmark']['face']['face_contour_left_' + str(mid_left_idx)]['x']
    mid_left_y = response['face']['landmark']['face']['face_contour_left_' + str(mid_left_idx)]['y']
    mid_right_x = response['face']['landmark']['face']['face_contour_right_' + str(mid_right_idx)]['x']
    mid_right_y = response['face']['landmark']['face']['face_contour_right_' + str(mid_right_idx)]['y']
    width = calc_distance(mid_left_x, mid_left_y, mid_right_x, mid_right_y)
    width_gradient = (mid_right_y - mid_left_y) / (mid_right_x - mid_left_x)

    upper_left_index = 105
    upper_left_x = response['face']['landmark']['face']['face_hairline_' + str(upper_left_index)]['x']
    upper_left_y = response['face']['landmark']['face']['face_hairline_' + str(upper_left_index)]['y']
    upper_right_idx = get_symmetric_hairline_point(response, upper_left_index, width_gradient)
    print(f'upper index : {upper_left_index} to {upper_right_idx}')
    upper_right_x = response['face']['landmark']['face']['face_hairline_' + str(upper_right_idx)]['x']
    upper_right_y = response['face']['landmark']['face']['face_hairline_' + str(upper_right_idx)]['y']
    upper_width = calc_distance(upper_left_x, upper_left_y, upper_right_x, upper_right_y)

    lower_left_index = find_lower_left_idx(response)
    lower_left_x = response['face']['landmark']['face']['face_contour_left_' + str(lower_left_index)]['x']
    lower_left_y = response['face']['landmark']['face']['face_contour_left_' + str(lower_left_index)]['y']
    lower_right_index = get_symmetric_contour_point(response, lower_left_index, width_gradient)
    print(f'lower index : {lower_left_index} to {lower_right_index}')
    lower_right_x = response['face']['landmark']['face']['face_contour_right_' + str(lower_right_index)]['x']
    lower_right_y = response['face']['landmark']['face']['face_contour_right_' + str(lower_right_index)]['y']
    lower_width = calc_distance(lower_left_x, lower_left_y, lower_right_x, lower_right_y)

    low_lip_mid_x = response['face']['landmark']['mouth']['lower_lip_47']['x']
    low_lip_mid_y = response['face']['landmark']['mouth']['lower_lip_47']['y']
    chin_height = calc_distance(low_lip_mid_x, low_lip_mid_y, bottom_x, bottom_y)

    nose_top_mid_x = response['face']['landmark']['nose']['nose_midline_0']['x']
    nose_top_mid_y = response['face']['landmark']['nose']['nose_midline_0']['y']
    forehead_height = calc_distance(top_x, top_y, nose_top_mid_x, nose_top_mid_y)

    return {'h_w_ratio': round(height / width, 2),
            'uw_ratio': round(upper_width / width, 2),
            'lw_ratio': round(lower_width / width, 2),
            'chin_ratio': round(chin_height / height, 2),
            'forehead_ratio': round(forehead_height / height, 2),
            'top_x': top_x,
            'top_y': top_y,
            'bottom_x': bottom_x,
            'bottom_y': bottom_y,
            'mid_left_x': mid_left_x,
            'mid_left_y': mid_left_y,
            'mid_right_x': mid_right_x,
            'mid_right_y': mid_right_y,
            'upper_left_x': upper_left_x,
            'upper_left_y': upper_left_y,
            'upper_right_x': upper_right_x,
            'upper_right_y': upper_right_y,
            'lower_left_x': lower_left_x,
            'lower_left_y': lower_left_y,
            'lower_right_x': lower_right_x,
            'lower_right_y': lower_right_y}
