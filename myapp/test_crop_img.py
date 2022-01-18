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

DIR = "/work/urs-server/myapp/crop_test_data/"
URL = "https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark"
API_KEY = "-D9lXEJg0Z0MMuSHKtmKxetMLqYkZp2c"
API_SECRET = "2At_EM1UjwJHSzE_j325L2KxbXjDrefE"
FileList = os.listdir(DIR)
index = 1

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
    img = Image.open(DIR + file)
    print(img.size)
    croped_img = img.crop(area)
    croped_img.save(DIR + "crop/" + file)
    im_file = BytesIO()
    croped_img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
    return base64.b64encode(im_bytes)

for file in FileList:
    if '.jpg' in file:
        print(file)
        img_cv = cv2.imread(DIR + file)
        binary_cv = cv2.imencode('.PNG', img_cv)[1].tobytes()
        parameters = dict(api_key=API_KEY, api_secret=API_SECRET, return_landmark='all')
        response = requests.post(URL, data=parameters, files={'image_file': binary_cv})
        face = response.json()
        print(face)
        
        # area = (left, top, right, bottom)
        # img = Image.open(DIR + file)
        # print(img.size)
        # croped_img = img.crop(area)
        print(str(index) + ". " + file)
        # croped_img.save(DIR + "crop/" + file)
        b64 = crop_img(file, face)
        time.sleep(2)
        index = index +1
