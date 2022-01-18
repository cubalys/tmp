import cv2
import requests
import sys
import os
from PIL import Image
import json
import numpy as np
from . import error_score
from . import face_pp

URL = 'https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark'
API_KEY = ['-D9lXEJg0Z0MMuSHKtmKxetMLqYkZp2c', 'eORdjUCXMFgW-RahCeWAzZM-huNDakIi', '5AkMaXLVTFXwCCJNEwpCOttuHeAa-wf3', 'hyQuigXn3o3g4A73OI3inYxOqnm_G6W_', '_M-34D9kPT66uMXCjTOXetY1A_7MbnXV']
API_SECRET = ['2At_EM1UjwJHSzE_j325L2KxbXjDrefE', 'KpWC-gpiLp1WuMwfm-LGN1UtvnsUYa1M', 'QEvQvEeoiRXkknw01pXtF0Cd1D9ZfjxK', '6jxwxwTdC-wvDbKIaiCH_dXWk2GqGqPD', 'XzgKDBV5MEmp_CkerpPshpXZIDU1xMeW']
api_idx = 0

def get_facepp_api_res(filepath):
    global api_idx
    img_cv = cv2.imread(filepath)
    binary_cv = cv2.imencode('.PNG', img_cv)[1].tobytes()
    nofAPI = len(API_KEY)
    parameters = dict(api_key=API_KEY[api_idx], api_secret=API_SECRET[api_idx], return_landmark='all')
    api_idx = (api_idx + 1) % nofAPI
    response = requests.post(URL, data=parameters, files={'image_file': binary_cv})

    try: 
        res = response.json()
    except:
        tmp = dict()
        tmp["errors"] = "facepp error : face not detected" 
        res = tmp
    with open('/work/urs-server/myapp/log/facepp_result.json', 'w', encoding='utf-8') as make_file:
        json.dump(res, make_file, indent="\t")

    ####test####
    # srcname = filepath.split('/')[-1]
    # ref_rectangle = dict(width = 131, top = 93, height = 131, left = 62)
    # src_rectangle = res['face']['face_rectangle']
    # dx_scale = ref_rectangle['width'] / src_rectangle['width']
    # dy_scale = ref_rectangle['height'] / src_rectangle['height']
    # img = cv2.imread(filepath) 
    # scaleimg = cv2.resize(img, None,  None, dx_scale, dy_scale, cv2.INTER_CUBIC)
    # dx = ref_rectangle['left'] - src_rectangle['left']
    # dy = ref_rectangle['top'] - src_rectangle['top']
    # mtrx = np.float32([[1, 0, dx],
    #                 [0, 1, dy]]) 
    # rows,cols = 256, 256
    # gan_src = cv2.warpAffine(scaleimg, mtrx, (cols+dx, rows+dy), None, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT, (255,255,255) )
    # crop_src = gan_src[0:256, 0:256]
    # pil_image=Image.fromarray(crop_src)
    # pil_image.save('/work/urs-server/media/media/gan_src_image/' + srcname)
   # cv2.write('/work/urs-server/media/media/gan_src_img/' + srcname, gan_src)

    ############
    return res

def get_shape_possibilities(h_w_ratio, lw_ratio, chin_ratio, forehead_ratio):
    error_scores = error_score.get_error_score(h_w_ratio, lw_ratio, chin_ratio, forehead_ratio)
    error_score_sum = sum(error_scores.values())

    possibilities = {}
    for k, v in error_scores.items():
        p = 1.0 - (v / error_score_sum)
        possibilities[k] = p

    return possibilities


def get_shape(face_json, face_shape_table):
    fd = face_pp.get_face_data(face_json)

    # calculate possibilities
    sp = get_shape_possibilities(h_w_ratio=fd["h_w_ratio"],
                                 lw_ratio=fd["lw_ratio"],
                                 chin_ratio=fd['chin_ratio'],
                                 forehead_ratio=fd['forehead_ratio'])
    print(f'possibilities : {sp}')
    return get_face_shape_detail(face_json, sp, face_shape_table)


def get_face_shape_detail(face_json, sp, face_shape_table):
    rev_dict = dict()
    rev_dict[str(sp['oblong'])] = 'oblong'
    rev_dict[str(sp['oval'])] = 'oval'
    rev_dict[str(sp['round'])] = 'round'
    rev_dict[str(sp['square'])] = 'square'
    faceshape = rev_dict[str(max(sp['oblong'], sp['oval'], sp['round'], sp['square']))]

    # with open('/work/urs-server/data/face_shape.json', 'r') as f:
    #     face_shape_table = json.load(f)
    face_golden_ratio = 1.3
    tmp_faceshape = faceshape 
    islong = False
    isshort = False
    diff_garosero = 1.15
    face_info_tmp = dict()
    face_top = (face_json['face']['landmark']['face']['face_hairline_72']["y"]+face_json['face']['landmark']['face']['face_hairline_74']["y"])/2
    face_jaw =  (face_json['face']['landmark']['face']['face_contour_left_0']["y"]+face_json['face']['landmark']['face']['face_contour_right_0']["y"])/2
    face_height = face_jaw-face_top
    face_width = 0
    for i in range(0, 64):
        tmp = face_json['face']['landmark']['face']["face_contour_right_" + str(i)]["x"] - face_json['face']['landmark']['face']["face_contour_left_" + str(i)]["x"] 
        if face_width < tmp:
            face_width = tmp
    face_user_ratio = face_height/face_width
    face_info_tmp['width_height_ratio']=face_user_ratio
    if face_user_ratio >  face_golden_ratio * diff_garosero :
        islong = True
    elif face_user_ratio * diff_garosero < face_golden_ratio :
        isshort = True
    if isshort and tmp_faceshape != "oblog":
        tmp_faceshape = "short_" + tmp_faceshape
    elif islong and tmp_faceshape == "square":
        tmp_faceshape = "square_oblog"
    face_info_tmp['face_shape'] = tmp_faceshape
    face_info_tmp['face_shape_detail'] = face_shape_table[tmp_faceshape]
    print(tmp_faceshape)
    return face_info_tmp 

def get_face_info(face_json, face_ratio_table, face_shape_table):
    face_info_tmp = dict()
    face_info_tmp.update(get_face_landmark(face_json))
    face_info_tmp.update(get_face_ratio(face_json, face_ratio_table))
    face_info_tmp.update(get_shape(face_json, face_shape_table))
    return face_info_tmp
def get_face_landmark(face_json):
    face_info_tmp = dict()
    face_landmark=dict()
    face_landmark['top']={'x': (face_json['face']['landmark']['face']['face_hairline_72']["x"]+face_json['face']['landmark']['face']['face_hairline_74']["x"])/2, 'y': (face_json['face']['landmark']['face']['face_hairline_72']["y"]+face_json['face']['landmark']['face']['face_hairline_74']["y"])/2}
    face_landmark['upper_mid']={'x': (face_json['face']['landmark']['left_eyebrow']['left_eyebrow_31']["x"]+face_json['face']['landmark']['right_eyebrow']['right_eyebrow_31']["x"])/2, 'y': (face_json['face']['landmark']['left_eyebrow']['left_eyebrow_31']["y"]+face_json['face']['landmark']['right_eyebrow']['right_eyebrow_31']["y"])/2}
    face_landmark['lower_mid']={'x':(face_json['face']['landmark']['nose']['nose_left_47']["x"]+face_json['face']['landmark']['nose']['nose_right_47']["x"])/2, "y": (face_json['face']['landmark']['nose']['nose_left_47']["y"]+face_json['face']['landmark']['nose']['nose_right_47']["y"])/2}
    face_landmark['bottom']={"x":(face_json['face']['landmark']['face']['face_contour_left_0']["x"]+face_json['face']['landmark']['face']['face_contour_right_0']["x"])/2, "y": (face_json['face']['landmark']['face']['face_contour_left_0']["y"]+face_json['face']['landmark']['face']['face_contour_right_0']["y"])/2}
    face_info_tmp['landmark']=face_landmark
    return face_info_tmp
def get_face_ratio(face_json, face_ratio_table):
    # with open('/work/urs-server/data/face_ratio.json', 'r') as f:
    #     face_ratio_table = json.load(f)
    face_info_tmp = dict()
    face_top = (face_json['face']['landmark']['face']['face_hairline_72']["y"]+face_json['face']['landmark']['face']['face_hairline_74']["y"])/2
    face_eyebrow = (face_json['face']['landmark']['left_eyebrow']['left_eyebrow_31']["y"]+face_json['face']['landmark']['right_eyebrow']['right_eyebrow_31']["y"])/2
    face_noseend = (face_json['face']['landmark']['nose']['nose_left_47']["y"]+face_json['face']['landmark']['nose']['nose_right_47']["y"])/2
    face_jaw =  (face_json['face']['landmark']['face']['face_contour_left_0']["y"]+face_json['face']['landmark']['face']['face_contour_right_0']["y"])/2
    sanganbu = face_eyebrow-face_top
    junganbu = face_noseend-face_eyebrow
    haanbu = face_jaw-face_noseend

    face_ratio=dict()
    face_ratio['top']=round(sanganbu/(sanganbu+junganbu+haanbu)*100)
    face_ratio['mid']=round(junganbu/(sanganbu+junganbu+haanbu)*100)
    face_ratio['bottom']=round(haanbu/(sanganbu+junganbu+haanbu)*100)

    face_info_tmp['ratio']=face_ratio

    face_ratio_type = "tmp"
    diff_sangjungha = 1.05
    print(face_jaw-face_top)
    print(face_json['face']['face_rectangle']['height'])
    print(face_json['face']['face_rectangle']['width'])
    print(face_json['face']['landmark']['face']['face_hairline_0']["x"] - face_json['face']['landmark']['face']['face_hairline_144']["x"])
    if sanganbu > junganbu * diff_sangjungha and sanganbu > haanbu * diff_sangjungha : 
        face_ratio_type = "long_sanganbu"
    elif junganbu > sanganbu * diff_sangjungha and junganbu > haanbu * diff_sangjungha : 
        face_ratio_type = "long_junganbu"
    elif haanbu > sanganbu * diff_sangjungha and haanbu > junganbu * diff_sangjungha : 
        face_ratio_type = "long_haanbu"
    elif sanganbu * diff_sangjungha < junganbu and sanganbu * diff_sangjungha < haanbu :
        face_ratio_type = "short_sanganbu" 
    elif junganbu * diff_sangjungha < sanganbu and junganbu * diff_sangjungha < haanbu :
        face_ratio_type = "short_junganbu" 
    elif haanbu * diff_sangjungha < junganbu and haanbu * diff_sangjungha < sanganbu :
        face_ratio_type = "short_haanbu"
    else :
        face_ratio_type = "golden_face" 
    face_info_tmp['ratio_detail'] = face_ratio_table[str(face_ratio_type)]
    return face_info_tmp
