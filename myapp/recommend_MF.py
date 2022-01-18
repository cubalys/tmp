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
import sys
def nparrayTobytes(nparray):
    npbyte = pickle.dumps(nparray)
    result = base64.b64encode(npbyte)
    return result
def bytesTonparray(model_byte):
    npbyte = base64.b64decode(model_byte)
    result = pickle.loads(npbyte)
    return result

def recommend_MF(user_id):
    rating = pd.read_csv("/work/urs-server/recommend_MF_dummyuser/scoreDB.csv")
    #pprint(rating)   #   critic(user)   title(item)   rating
    rating['critic'].value_counts()
    rating['title'].value_counts()
    tab = pd.crosstab(rating['critic'], rating['title'])
    #print(tab)
    rating_g = rating.groupby(['critic', 'title'])
    rating_g.sum()
    tab = rating_g.sum().unstack() # 행렬구조로 변환
    print(tab)
    reader = Reader(rating_scale= (0, 100)) # 평점 범위
    data = Dataset.load_from_df(df=rating, reader=reader)
    #print(data)
    train = data.build_full_trainset() # 훈련셋
    test = train.build_testset() # 검정셋
    #help(SVD)
    model = SVD()
    model.fit(train) # model 생성
    Directory_rs = '/work/urs-server/recommend_hairdataset/UT/'
    with open(Directory_rs + "image_name.bin", "rb") as f:
        data_output = f.read()
    image_name_rsdb = bytesTonparray(data_output)
    actual_rating = 0 # 실제 평점
    for item_id in image_name_rsdb :
        tmp_result = model.predict(user_id, item_id, actual_rating)
        print(item_id + " : " + str(tmp_result.est))
    # sim_options = {
    #     "name" : "cosine",
    #     "user_based" : True,
    # }
    # model = KNNWithMeans(sim_options=sim_options)
    # trainingSet = data.build_full_trainset()
    # model.fit(trainingSet)
    # for item_id in item_ids :
    #     print(model.predict(user_id, item_id, actual_rating))
    # sim_options = {
    #     "name" : "cosine",
    #     "user_based" : False,
    # }
    # model = KNNWithMeans(sim_options=sim_options)
    # trainingSet = data.build_full_trainset()
    # model.fit(trainingSet)
    # for item_id in item_ids :
    #     print(model.predict(user_id, item_id, actual_rating))