import requests 
import base64
import json 
import cv2
from PIL import Image
import os
import base64
import time
# POST (JSON) 
from io import BytesIO
def crop_img(file, face):
    W = face['face']['face_rectangle']['width']
    H = face['face']['face_rectangle']['height']
    L = face['face']['face_rectangle']['left']
    T = face['face']['face_rectangle']['top']
    print(L, T, W, H)
    tmp_x = 900 - face['face']['face_rectangle']['width']
    tmp_y = 900 - face['face']['face_rectangle']['height']
    left = face['face']['face_rectangle']['left'] - tmp_x/2
    right = face['face']['face_rectangle']['left'] +  face['face']['face_rectangle']['width'] + tmp_x/2
    top = face['face']['face_rectangle']['top'] - tmp_y/4*3
    tmp = 0
    if top < 0:
        tmp = top 
        top = 0
    bottom = face['face']['face_rectangle']['top'] + face['face']['face_rectangle']['height'] + tmp_y/4 - tmp
    area = (left, top, right, bottom)
    img = Image.open(file)
    croped_img = img.crop(area)
    print(str(file).split('media/media/')[1])
    split_dir = str(file).split('media/media/')
    save_img_dir = split_dir[0] + 'media/media/cropped_' + split_dir[1]
    croped_img.save(save_img_dir) 
    im_file = BytesIO()
    croped_img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
    return base64.b64encode(im_bytes)