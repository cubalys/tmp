import cv2
import requests
import sys
import os
from PIL import Image

from . import error_score
from . import face_pp
import json

URL = 'https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark'
API_KEY = '-D9lXEJg0Z0MMuSHKtmKxetMLqYkZp2c'
API_SECRET = '2At_EM1UjwJHSzE_j325L2KxbXjDrefE'


def get_shape_possibilities(h_w_ratio, lw_ratio, chin_ratio, forehead_ratio):
    error_scores = error_score.get_error_score(h_w_ratio, lw_ratio, chin_ratio, forehead_ratio)
    error_score_sum = sum(error_scores.values())

    possibilities = {}
    for k, v in error_scores.items():
        p = 1.0 - (v / error_score_sum)
        possibilities[k] = p

    return possibilities


def get_shape(face_plusplus_response):
    fd = face_pp.get_face_data(face_plusplus_response)

    # calculate possibilities
    sp = get_shape_possibilities(h_w_ratio=fd["h_w_ratio"],
                                 lw_ratio=fd["lw_ratio"],
                                 chin_ratio=fd['chin_ratio'],
                                 forehead_ratio=fd['forehead_ratio'])
    #print(f'possibilities : {sp}')
    return fd, sp


# parameters = dict(api_key=API_KEY, api_secret=API_SECRET, return_landmark='all')
# img_cv = cv2.imread(sys.argv[1])
# binary_cv = cv2.imencode('.PNG', img_cv)[1].tobytes()
# response = requests.post(URL, data=parameters, files={'image_file': binary_cv})
# response = response.json()
with open(sys.argv[1], 'r') as f:
    response = json.load(f)
face_data, shape_possibilities = get_shape(response)
with open('/work/urs-server/myapp/faceshape_carrick/faceshape.json', 'w', encoding='utf-8') as make_file:
    json.dump(shape_possibilities, make_file, indent="\t")
print(shape_possibilities)
# # horizontal line
# cv2.line(img_cv, (int(face_data['upper_left_x']), int(face_data['upper_left_y'])),
#          (int(face_data['upper_right_x']), int(face_data['upper_right_y'])), color=(0, 80, 0))
# cv2.line(img_cv, (int(face_data['mid_left_x']), int(face_data['mid_left_y'])),
#          (int(face_data['mid_right_x']), int(face_data['mid_right_y'])), color=(0, 160, 0))
# cv2.line(img_cv, (int(face_data['lower_left_x']), int(face_data['lower_left_y'])),
#          (int(face_data['lower_right_x']), int(face_data['lower_right_y'])), color=(0, 240, 0))

# # vertical line
# cv2.line(img_cv, (int(face_data['top_x']), int(face_data['top_y'])),
#          (int(face_data['bottom_x']), int(face_data['bottom_y'])),
#          color=(255, 0, 0))

# # ratio text
# y = face_data['bottom_y'] - 60
# cv2.putText(img_cv, org=(20, int(y)),
#             fontFace=1, fontScale=1, color=(54, 54, 255), thickness=1,
#             text=f'height/width: {face_data["h_w_ratio"]}')
# cv2.putText(img_cv, org=(20, int(y + 20)),
#             fontFace=1, fontScale=1, color=(54, 54, 255), thickness=1,
#             text=f'uw ratio: {face_data["uw_ratio"]}')
# cv2.putText(img_cv, org=(20, int(y + 40)),
#             fontFace=1, fontScale=1, color=(54, 54, 255), thickness=1,
#             text=f'lw ratio: {face_data["lw_ratio"]}')
# cv2.putText(img_cv, org=(20, int(y + 60)),
#             fontFace=1, fontScale=1, color=(54, 54, 255), thickness=1,
#             text=f'chin ratio: {face_data["chin_ratio"]}')

# # shape text
# for key, possibility in shape_possibilities.items():
#     cv2.putText(img_cv, org=(350, int(y)),
#                 fontFace=1, fontScale=1, color=(200, 65, 217), thickness=1,
#                 text=f'{key}: {int(possibility * 100)}%')
#     y += 20

# img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
# im_pil = Image.fromarray(img_cv)
# im_pil.show()

