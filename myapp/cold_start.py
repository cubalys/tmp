import numpy as np
from numpy import dot
from numpy.linalg import norm
from numpy import sqrt
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
def nparrayTobytes(nparray):
    npbyte = pickle.dumps(nparray)
    result = base64.b64encode(npbyte)
    return result
def bytesTonparray(model_byte):
    npbyte = base64.b64decode(model_byte)
    result = pickle.loads(npbyte)
    return result
def coldStart(Directory_rs, user_id):
    with open(Directory_rs + "image_name.bin", "rb") as f:
        data_output = f.read()
    image_name_rsdb = bytesTonparray(data_output) 
    rsImageLen = image_name_rsdb.size
    print (rsImageLen)
    check = np.array([])
    coldStartImg = np.array([], dtype=np.string_)
    check.resize(rsImageLen)
    print(check[10])
    cnt = 0
    with open('/work/urs-server/data/recommend_hair_domain.json', 'r') as f:
        rs_hair_domain = json.load(f)
    while cnt < 9:
        rand = random.randrange(1, rsImageLen)
        if image_name_rsdb[rand].split('_')[0] + ".jpg" in rs_hair_domain : 
            if check[rand] == 0 :
                check[rand] = 1
                coldStartImg = np.append(coldStartImg, image_name_rsdb[rand])
                print(str(rand) + " " +  image_name_rsdb[rand])
                cnt = cnt + 1
    data = nparrayTobytes(check)
    with open(Directory_rs + user_id + "_cs.bin", "wb") as f:
        f.write(data)
    print(bytesTonparray(data_output))
    return coldStartImg
# def getSimilarImg(Directory_rs, user_id, selected_img):
def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))
    
def input_score(user_id, selected_image) :
    f = open('/work/urs-server/recommend_MF_dummyuser/scoreDB_UT.csv','a', newline='')
    wr = csv.writer(f)
    print(user_id +" " + selected_image)
    wr.writerow([user_id,selected_image, 100])
    f.close()

def get_similar_hair(Directory_rs, user_id, selected_image) :
    f = open('/work/urs-server/recommend_MF_dummyuser/scoreDB.csv','a')
    wr = csv.writer(f)
    print(user_id +" " + selected_image)
    wr.writerow(['\n' + user_id,selected_image, 100])
    f.close()
    with open(Directory_rs + "image_name.bin", "rb") as f:
        data_output = f.read()
    image_name = bytesTonparray(data_output)
    with open(Directory_rs + user_id + "_cs.bin", "rb") as f:
        data_output = f.read()
    check = bytesTonparray(data_output)
    results = np.array([])
    results.resize(1, 6)
    hairDB = np.array([])

    selectedImg_vector = np.array([])
    hairvector = np.array([])
    with open("/work/urs-server/data/UT_vector.csv") as csvfile:
        reader = csv.reader(csvfile) 
        for row in reader :
            if row[0] == selected_image:
                for col in range(1, len(row)):
                    selectedImg_vector = np.append(selectedImg_vector, row[col])
                    selectedImg_vector = selectedImg_vector.astype(np.int64)
    print(selectedImg_vector)
    result_array = [0.0,0.0,0.0]
    result_name = ["", "", ""]
    print(selected_image)
    with open("/work/urs-server/data/UT_vector.csv") as csvfile:
        reader = csv.reader(csvfile) 
        index = 1
        for row in reader: 
            if row[0] == "이름" :
                continue 
            lenrow = len(row)
            hairvector = np.array([])
            for col in range(0, lenrow):
                if row[col].isdigit() :
                    hairvector = np.append(hairvector, row[col])
                    if col == lenrow - 1 :
                        if check[np.where(image_name == row[0])] != 1:
                            
                            hairvector = hairvector.astype(np.int64)
                            score = cos_sim(hairvector, selectedImg_vector)
                            if score > result_array[0] :
                                result_array[2] = result_array[1]
                                result_array[1] = result_array[0]
                                result_array[0] = score 
                                result_name[2] = result_name[1]
                                result_name[1] = result_name[0]
                                result_name[0] = row[0]
                            elif score > result_array[1]:
                                result_array[2] = result_array[1]
                                result_array[1] = score
                                result_name[2] = result_name[1]
                                result_name[1] = row[0]
                            elif score > result_array[2]:
                                result_array[2] = score
                                result_name[2] = row[0]
                            index = index + 1
    print(check)
    print(result_name)
    check[np.where(image_name == result_name[0])] = 1
    check[np.where(image_name == result_name[1])] = 1
    check[np.where(image_name == result_name[2])] = 1
    data = nparrayTobytes(check)
    
    with open(Directory_rs + user_id + "_cs.bin", "wb") as f:
        f.write(data)
    return result_name
# tmp = np.array([row + 1])
# hairDB = np.append(hairDB, nparrayTobytes(tmp))
# results = np.concatenate((results, tmp), axis=0)
# hairDB = np.unique(hairDB)
# hairDB_nparray = np.array([])
# hairDB_nparray.resize(1, 5)
# hindex = 0
# for hair in hairDB:
#     hairDB_nparray = np.concatenate((hairDB_nparray, bytesTonparray(hair)), axis = 0)
# print(hairDB_nparray)
