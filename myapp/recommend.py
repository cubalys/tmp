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
from PIL import Image
from io import BytesIO
import os
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
def hair_csvTovector():
    results = np.array([])
    results.resize(1, 21)
    hairDB = np.array([])
    with open("/work/urs-server/hair.csv") as csvfile:
        reader = csv.reader(csvfile) #, quoting=csv.QUOTE_MINIMAL) # change contents to floats
        for row in reader: # each row is a list
            tmp = np.array([row])
            hairDB = np.append(hairDB, nparrayTobytes(tmp))
            results = np.concatenate((results, tmp), axis=0)
    hairDB = np.unique(hairDB)
    hairDB_nparray = np.array([])
    hairDB_nparray.resize(1, 21)
    hindex = 0
    for hair in hairDB:
        hairDB_nparray = np.concatenate((hairDB_nparray, bytesTonparray(hair)), axis = 0)
    return results
def cos_sim(A, B):
       return dot(A, B)/(norm(A)*norm(B))
def jsonTofacevector(face_json):
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
def recommend_MF(user_id, hair_domain, rs_dir):
    rating = pd.read_csv("/work/urs-server/recommend_MF_dummyuser/scoreDB_UT.csv")
    #pprint(rating)   #   critic(user)   title(item)   rating
    rating['critic'].value_counts()
    rating['title'].value_counts()
    tab = pd.crosstab(rating['critic'], rating['title'])
    #print(tab)
    rating_g = rating.groupby(['critic', 'title'])
    rating_g.sum()
    tab = rating_g.sum().unstack() # 행렬구조로 변환
    reader = Reader(rating_scale= (0, 100)) # 평점 범위
    data = Dataset.load_from_df(df=rating, reader=reader)
    #print(data)
    train = data.build_full_trainset() # 훈련셋
    test = train.build_testset() # 검정셋
    #help(SVD)
    model = SVD()
    model.fit(train) # model 생성
    with open(rs_dir + "image_name.bin", "rb") as f:
        data_output = f.read()
    image_name_rsdb = bytesTonparray(data_output)
    actual_rating = 0 # 실제 평점
    rs_result = np.array([])
    for item_id in image_name_rsdb :
        if item_id in hair_domain : 
            tmp_result = model.predict(user_id, item_id, actual_rating)
            rs_result = np.append(rs_result, str(tmp_result.est))
    
    return rs_result
def is_json_key_present(json, key):
    try:
        buf = json[key]
    except KeyError:
        return False
    return True
def jsonkey_present(json, key):
    if key in json : 
        return True
    return False
def get_rs_result(facepp_result, user_id, rs_dir):
    face_vector_model = np.array([])
    with open(rs_dir + "face_vector.bin", "rb") as f:
        data_output = f.read()
    face_vector_model = bytesTonparray(data_output)
    with open(rs_dir + "image_name.bin", "rb") as f:
        data_output = f.read()
    image_name = bytesTonparray(data_output)
    with open('/work/urs-server/data/recommend_hair_domain.json', 'r') as f:
        domain = json.load(f)
    MF_result = recommend_MF(user_id, domain, rs_dir)
    # hair_vector_model = hair_csvTovector()
    # data = nparrayTobytes(hair_vector_model)
    # with open("/work/urs-server/face_vector_tmp.bin", "wb") as f:
    #     f.write(data)
    # data_output = 0
    # with open("/work/urs-server/face_vector_tmp.bin", "rb") as f:
    #     data_output = f.read()
    # result = bytesTonparray(data_output)
    # print(image_name[0])
    test_json = facepp_result
    test_vector = jsonTofacevector(test_json)
    index = 0
    rs_cos_result = np.array([])
    rs_euclid_result = np.array([])
    rs_cos_index = np.array([])
    rs_euclid_index = np.array([])
    rs_result = np.array([])
    rs_index = np.array([])
    img_idx = 0
    # print(face_vector_model)
    # print(image_name)
    for face_vector in face_vector_model:
        if(index == 0):
            index = int(index) + 1
            continue
        # print(image_name[img_idx])
        if jsonkey_present(domain, image_name[img_idx]) :
            print(image_name[img_idx])
            cos_result = cos_sim(face_vector , test_vector)
            euclid_result = np.linalg.norm(face_vector - test_vector)
            rs_cos_result = np.append(rs_cos_result, cos_result*10-9)
            rs_euclid_result = np.append(rs_euclid_result, 1/(1+euclid_result))
            rs_result = np.append(rs_result, (cos_result + 1/(1+euclid_result))/2)
            rs_cos_index = np.append(rs_cos_index, index)
            rs_euclid_index = np.append(rs_euclid_index, index)
            rs_index = np.append(rs_index, index)
        index = int(index) + 1
        img_idx = img_idx + 1
        # if(index == 0):
        #     index = int(index) + 1
        #     continue
        # cos_result = cos_sim(face_vector , test_vector)
        # euclid_result = np.linalg.norm(face_vector - test_vector)
        # rs_cos_result = np.append(rs_cos_result, cos_result*10-9)
        # rs_euclid_result = np.append(rs_euclid_result, 1/(1+euclid_result))
        # rs_result = np.append(rs_result, (cos_result + 1/(1+euclid_result))/2)
        # rs_cos_index = np.append(rs_cos_index, index)
        # rs_euclid_index = np.append(rs_euclid_index, index)
        # rs_index = np.append(rs_index, index)
        # index = int(index) + 1
    lenarr = len(rs_result)
    #print(rs_index)
    #print(rs_result)
    #print(len(rs_result))
    #print(len(MF_result))
    min = 100
    for idx in range(0, lenarr):
        rs_result[idx] = float(rs_result[idx]) * 100 * 0.5 + float(MF_result[idx]) * 0.5
        if min > int(rs_result[idx]):
            min = int(rs_result[idx])
    max = 0
    for idx in range(0, lenarr):
        rs_result[idx] = rs_result[idx] - min
        if max < rs_result[idx]:
            max  = rs_result[idx]
    for idx in range(0, lenarr):    
        rs_result[idx] = rs_result[idx] * 100 / max
    sort_by_euclid = rs_euclid_result.argsort()[::-1]
    sort_by_cossim = rs_cos_result.argsort()[::-1]
    sort_rs = rs_result.argsort()[::-1]
    rs_cos_result = rs_cos_result[sort_by_cossim]
    rs_cos_index = rs_cos_index[sort_by_cossim]
    rs_euclid_result = rs_euclid_result[sort_by_euclid]
    rs_euclid_index = rs_euclid_index[sort_by_euclid]
    rs_result = rs_result[sort_rs]
    rs_index = rs_index[sort_rs]
    print(rs_result)
    print(rs_index)
    rs_res_nparray = np.array([])
    for file_index in rs_index:
        tmp = image_name[int(file_index)-1]
        rs_res_nparray = np.append(rs_res_nparray, str(tmp))
    byte_point = nparrayTobytes(rs_res_nparray)

    recommend_hair = dict()
    rshair_Directory = rs_dir
    # with open('/work/urs-server/recommend_hairdataset/UT/name.json', 'r') as f:
    #     name_title = json.load(f)
    cnt = 0
    rs_index = 0
    print(rs_res_nparray)
    for rshair_idx in range(0, 6):
        # print(rshair_Directory + str(rs_res_nparray[rshair_idx]))
        img_tmp = Image.open(rshair_Directory + str(rs_res_nparray[rshair_idx]))
        img_tmp = img_tmp.resize((512, 512), Image.NEAREST)
        buffered = BytesIO()
        img_tmp.save(buffered, format="JPEG")
        encoded_string = base64.b64encode(buffered.getvalue())
        selectedImg_vector = np.array([])
        with open("/work/urs-server/data/UT_vector.csv") as csvfile:
            reader = csv.reader(csvfile) 
            for row in reader :
                if row[0] == rs_res_nparray[rshair_idx]:
                    for col in range(1, len(row)):
                        selectedImg_vector = np.append(selectedImg_vector, row[col])
        # print(selectedImg_vector)
        if selectedImg_vector.size == 0 : 
            continue
        selectedImg_vector = selectedImg_vector.astype(np.int64)
        bang = ["앞머리 없는 ", "앞머리 있는 ", "앞머리 있는 "]
        howlong = ["숏컷 ", "단발 ", "장발 ", "장발 "]
        curl = ["", "C컬", "S컬", "S컬"]
        name_title = bang[selectedImg_vector[1]] + howlong[selectedImg_vector[0]] + curl[selectedImg_vector[2]]
        rs_tmp = dict()
        rs_tmp['name'] = rs_res_nparray[rshair_idx] 
        rs_tmp['title'] = name_title
        rs_tmp['image'] = str(encoded_string).split("'")[1]
        recommend_hair[str(rs_index)] = rs_tmp
        rs_index += 1
        cnt += 1
        if cnt == 4 : 
            break
    recommend_result_hairList_json = recommend_hair
    return recommend_result_hairList_json
