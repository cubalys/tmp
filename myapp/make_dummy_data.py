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
import subprocess
import random
import sys
#from make_recommend_hair import faceppAPI
# POST (JSON) 
#print(make_recommend_hair.faceppAPI('/work/urs-server/media/media/00668153-5c90-463d-8d6e-923e7c3d5a5f.jpg'))
def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))
def nparrayTobytes(nparray):
    npbyte = pickle.dumps(nparray)
    result = base64.b64encode(npbyte)
    return result
def bytesTonparray(model_byte):
    npbyte = base64.b64decode(model_byte)
    result = pickle.loads(npbyte)
    return result
Directory = '/work/urs-server/recommend_MF_dummyuser/'
with open(Directory + "face_vector.bin", "rb") as f:
    data_output = f.read()
face_vector_model = bytesTonparray(data_output)
with open(Directory + "image_name.bin", "rb") as f:
    data_output = f.read()
user_list = bytesTonparray(data_output)

f = open(Directory + 'scoreDB_UT.csv','w', newline='')
wr = csv.writer(f)
index = 2
wr.writerow(['critic', 'title', 'rating'])

Directory_rs = '/work/urs-server/recommend_hairdataset/UT/'
with open(Directory_rs + "face_vector.bin", "rb") as f:
    data_output = f.read()
face_vector_rsdb = bytesTonparray(data_output)
with open(Directory_rs + "image_name.bin", "rb") as f:
    data_output = f.read()
image_name_rsdb = bytesTonparray(data_output)

index = 1
for user in user_list:
    index_rs = 1
    for rs_db in image_name_rsdb:
        rand_tmp = random.randrange(1, 6)
        if rand_tmp > 2:
            wr.writerow([str(user), str(rs_db), cos_sim(face_vector_model[index], face_vector_rsdb[index_rs]) * 100])
        index_rs = index_rs + 1
    index = index + 1
