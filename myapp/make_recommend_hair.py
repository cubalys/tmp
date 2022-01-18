import numpy as np
from numpy import dot
from numpy.linalg import norm
from numpy import sqrt
import pandas as pd # raw dataset
from surprise import SVD, accuracy, NMF # SVD model, 평가
from surprise import Reader, Dataset # SVD model의 dataset
import math
import csv
import cv2
import requests
import pickle
import json
import base64
import os
import time
import sys

def faceppAPI(filename):
    URL = "https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark"
    API_KEY = "-D9lXEJg0Z0MMuSHKtmKxetMLqYkZp2c"
    API_SECRET = "2At_EM1UjwJHSzE_j325L2KxbXjDrefE"
    img_cv = cv2.imread(filename)
    binary_cv = cv2.imencode('.PNG', img_cv)[1].tobytes()
    parameters = dict(api_key=API_KEY, api_secret=API_SECRET, return_landmark='all')
    response = requests.post(URL, data=parameters, files={'image_file': binary_cv})
    return response.json()
def nparrayTobytes(nparray):
    npbyte = pickle.dumps(nparray)
    result = base64.b64encode(npbyte)
    return result
def bytesTonparray(model_byte):
    npbyte = base64.b64decode(model_byte)
    result = pickle.loads(npbyte)
    return result
def jsonTofacevector(face_json):
    if "face" not in face_json:
        print(face_json)
    landmark = face_json["face"]["landmark"]
    rectangle = face_json["face"]["face_rectangle"]
    with open("/work/urs-server/face_factors.json") as json_file:
        face_factors = json.load(json_file)
    result = np.array([])
    reset_x = rectangle["left"]
    reset_y = rectangle["top"]
    reset_h = rectangle["height"]
    reset_w = rectangle["width"]
    for items in face_factors:
        for factors in face_factors[items]:
            for i in range(0, face_factors[items][factors]) :
                result = np.append(result, float(landmark[items][factors + str(i)]["y"] - reset_y)/reset_h)
                result = np.append(result, float(landmark[items][factors + str(i)]["x"] - reset_x)/reset_w)
    return result
Directory = sys.argv[1]
FileList = os.listdir(Directory)
face_vector_model = np.array([])
image_name = np.array([])
face_vector_model.resize (1, 1682)
index = 1
for file in FileList:
    if '.jpg' in file:
        print(str(index) + ". " + file)
        face_json = faceppAPI(Directory + file)
        tmp =  jsonTofacevector(face_json)
        print(tmp)
        face_vector_model =  np.concatenate((face_vector_model, [tmp]), axis = 0)
        image_name = np.append(image_name, file)
        time.sleep(20)
        index = index + 1
    if '.png' in file:
        print(str(index) + ". " + file)
        face_json = faceppAPI(Directory + file)
        tmp =  jsonTofacevector(face_json)
        print(tmp)
        face_vector_model =  np.concatenate((face_vector_model, [tmp]), axis = 0)
        image_name = np.append(image_name, file)
        time.sleep(10)
        index = index + 1
data = nparrayTobytes(image_name)
with open(Directory + "image_name.bin", "wb") as f:
    f.write(data)
data_output = 0
with open(Directory + "image_name.bin", "rb") as f:
    data_output = f.read()
result = bytesTonparray(data_output)
print(result)
data = nparrayTobytes(face_vector_model)
with open(Directory + "face_vector.bin", "wb") as f:
    f.write(data)
data_output = 0
with open(Directory + "face_vector.bin", "rb") as f:
    data_output = f.read()
result = bytesTonparray(data_output)
print(result)
