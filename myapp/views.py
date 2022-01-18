from django.shortcuts import render
from rest_framework import viewsets
from .serializers import PersonSerializer
from .serializers import PersonTestSerializer
from .serializers import PersonDetailSerializer
from .serializers import RecommendResultSerializer
from .serializers import RecommendTestSerializer
from .serializers import SimulationStyleListSerializer
from .serializers import GanRequestSeializer
from .serializers import ColdStartSerializer
from .serializers import UserDataSerializer
from .serializers import SconDataSerializer
from myapp.models import RecommendTest
from myapp.models import Person
from myapp.models import PersonTest
from myapp.models import RecommendResult
from myapp.models import SimulationStyleList
from myapp.models import SconData
from myapp.models import GanRequest
from myapp.models import ColdStart
from myapp.models import UserData
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
import myapp.cold_start as coldst
from PIL import Image
from io import BytesIO
import json
from django.db import models
from django.contrib.postgres.fields import ArrayField
import django.contrib.postgres.fields
import subprocess
import sys
import json
import base64
import cv2
import gzip, pickle
import requests 
import numpy as np
from numpy import dot
from numpy.linalg import norm
from numpy import sqrt
import time
from faceshape_carrick import shape
import os
import myapp.recommend as rs
from myapp.personal_color import get_personal_color4 as pc
from PIL import Image
from io import BytesIO
import myapp.stargan_v2.gen_img as gi
import myapp.crop_img as cr
from glob import glob
import shutil
from django.http import HttpRequest as request
from urllib import parse
from datetime import datetime
import uuid
from os.path import getsize
sys.path.append("/work/urs-server/myapp/Scon_dyeing")

import myapp.Scon_dyeing.dyeing_img as di

# Create your views here.

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


def jsonkey_present(json, key):
    if key in json : 
        return True
    return False

@csrf_exempt
def create_userdata(request):
    if request.method == 'POST' :
        user_data = JSONParser().parse(request)
        if jsonkey_present(user_data, 'API_KEY'):
           api_key = user_data['API_KEY']
           if api_key != 'a':
                err = dict()
                err['errors'] = "Wrong API KEY"
                return JSONResponse(err, status=status.HTTP_400_BAD_REQUEST)
        else :
            err = dict()
            err['errors'] = "API KEY not found."
            return JSONResponse(err, status=status.HTTP_400_BAD_REQUEST)
        idx = 1
        userJson = dict()
        usernum = 0
        while True:
            try :
                person = PersonTest.objects.get(no = idx)
                userJson[person.user_id] = person.no
                usernum = person.no
                idx+=1
            except:
                break
        user_info = dict()
        user_info['userid_json'] = userJson
        user_info['nofuser'] = usernum
        
        ud_serializer = UserDataSerializer(data=user_info)
        if ud_serializer.is_valid():
            ud_serializer.save()
            return JSONResponse(ud_serializer.data)
        
            
@csrf_exempt
def update_data(request):
    if request.method == 'PUT':
        scon_data = JSONParser().parse(request)
        if jsonkey_present(scon_data, 'version'):
           version = scon_data['version']
           update_scondata = SconData.objects.get(version = version)
        else :
            err = dict()
            err['errors'] = "Version not found."
            return JSONResponse(err, status=status.HTTP_400_BAD_REQUEST)
        if jsonkey_present(scon_data, 'API_KEY'):
           api_key = scon_data['API_KEY']
           if api_key != 'a':
                err = dict()
                err['errors'] = "Wrong API KEY"
                return JSONResponse(err, status=status.HTTP_400_BAD_REQUEST)
        else :
            err = dict()
            err['errors'] = "API KEY not found."
            return JSONResponse(err, status=status.HTTP_400_BAD_REQUEST)
        if jsonkey_present(scon_data, 'personalcolor_info'):
            update_scondata.personalcolor_info = scon_data['personalcolor_info']
        if jsonkey_present(scon_data, 'recommend_hair_domain'):
            update_scondata.recommend_hair_domain = scon_data['recommend_hair_domain']
        if jsonkey_present(scon_data, 'face_shape_info'):
            update_scondata.face_shape_info = scon_data['face_shape_info']
        if jsonkey_present(scon_data, 'face_ratio_info'):
            update_scondata.face_ratio_info = scon_data['face_ratio_info']
        if jsonkey_present(scon_data, 'userid_json'):
            update_scondata.userid_json = scon_data['userid_json']
        update_scondata.save()
        sr_scondata = SconDataSerializer(update_scondata)
        return JSONResponse(sr_scondata.data)
@csrf_exempt
def create_data(request):
    if request.method == 'POST':
        res = dict()
        scon_data = JSONParser().parse(request)
        if jsonkey_present(scon_data, 'API_KEY'):
           api_key = scon_data['API_KEY']
           if api_key != 'a':
                res['errors'] = "Wrong API KEY"
        else :
            res['errors'] = "API KEY not found."
        if jsonkey_present(scon_data, 'personalcolor_info') == False:
            res['errors'] = "'personal_color_info' not found."
        elif jsonkey_present(scon_data, 'recommend_hair_domain') == False:
            res['errors'] = "'recommend_hair_domain' not found."
        elif jsonkey_present(scon_data, 'face_shape_info') == False:
            res['errors'] = "'face_shape_info not found."
        elif jsonkey_present(scon_data, 'face_ratio_info') == False:
            res['errors'] = "'face_ratio_info' not found."
        else :
            res['personalcolor_info'] = scon_data['personalcolor_info']
            res['recommend_hair_domain'] = scon_data['recommend_hair_domain']
            res['face_shape_info'] = scon_data['face_shape_info']
            res['face_ratio_info'] = scon_data['face_ratio_info']
        if jsonkey_present(res, 'errors'):
            return JSONResponse(res, status=status.HTTP_400_BAD_REQUEST)
        scon_serializer = SconDataSerializer(data=res)
        if scon_serializer.is_valid():
            scon_serializer.save()
        return JSONResponse(scon_serializer.data)

@csrf_exempt
def view_data(request, version):
    if request.method == 'GET':
        res = dict()
        try :
            scon_data = SconData.objects.get(version=version)
        except:
            res['errors'] = "undefined version."
        scon_serializer = SconDataSerializer(scon_data)
        res['scon_data'] = scon_serializer.data
        return JSONResponse(res)



@csrf_exempt
def person_view(request, user_id):
    if request.method == 'GET':
        userobj = UserData.objects.get(version=1)
        user = userobj.userid_json

        # with open('/work/urs-server/myapp/user_id/user_id.json', 'r') as f:
        #     user = json.load(f)
        if user_id in user :
            queryset = PersonTest.objects.get(no=user[user_id])
            serializer_class = PersonTestSerializer(queryset, context={'request': request})
            personJson = serializer_class.data
            tmp = personJson['recommend_result']
            res = dict()
            
            if len(tmp) > 0: 
                rs_str = str(tmp[0]).split('/')[4]
                print(rs_str)
                rsset = RecommendResult.objects.get(no=int(rs_str))
                RSserializer = RecommendResultSerializer(rsset)
                res['last_recommend'] = RSserializer.data                                                                                                                                                           
                return JSONResponse(res)                         
            tmp = dict()
            return JSONResponse(tmp)
        tmp = dict()
        tmp["error"] = "user not exist"
        return JSONResponse(tmp)


@csrf_exempt
def recommend_create(request):
    mode = ""
    if request.method == 'POST':
        rs_data = JSONParser().parse(request)
        with open('/work/urs-server/myapp/log/rs_input.json', 'w', encoding='utf-8') as make_file:
            json.dump(rs_data, make_file, indent="\t")
        
        total_time_start = time.time()
        face_info_tmp=dict()
        imgdata = Image.open(BytesIO(base64.b64decode(rs_data['image_input'])))
        filename = str(uuid.uuid1()) + ".jpg"  # I assume you have a way of picking unique filenames
        imgdata = imgdata.resize((256,256))
        path = '/work/urs-server/media/media/' + filename
        if mode == "DEMO" : 
            path = '/work/urs-server/DEMO/input.jpg'
        else : 
            imgdata.save(path)
        # with open(path, 'wb') as f:
        #     f.write(imgdata)
        file_size = getsize(path)
        print(file_size) 
        if file_size >= 2000000 :
            restmp = dict()
            restmp["errors"] = "Image file is too big."
            print("Image file is too big.")
            return JSONResponse(restmp, status=status.HTTP_400_BAD_REQUEST)
        with open(path, "rb") as image_file:
            rs_data['image_input'] = base64.b64encode(image_file.read()).decode().strip()
        
        # path = '/work/urs-server/media/' + self.image_input.url
        # self.image_input = path
        scon_data = SconData.objects.get(version=1)
        scon_serializer = SconDataSerializer(scon_data)
        scon_json = scon_serializer.data
        ########################### facepp API##########################
        print("facepp api start")
        starttime = time.time()
        face_json = shape.get_facepp_api_res(path)
        if (jsonkey_present(face_json['face'], 'landmark') ==  False) or (jsonkey_present(face_json, 'face') == False):
            restmp = dict()
            restmp["errors"] = "Facepp error : face not detected."
            print("Facepp error : face not detected.")
            return JSONResponse(face_json, status=status.HTTP_400_BAD_REQUEST)
        rs_data['face'] = face_json
        # print(face_json)
        endtime = time.time()
        print("facepp api end - process time : " + str(endtime - starttime))
        
        ########################### faceinfo ###########################
        print("faceinfo start")
        starttime = time.time()
        face_info_tmp.update(shape.get_face_info(face_json, scon_json['face_ratio_info'], scon_json['face_shape_info']))
        # print(shape.get_face_info(face_json))
        print(type(face_info_tmp))
        rs_data['face_info'] = face_info_tmp
        endtime = time.time()
        print("faceshape end - process time : " + str(endtime - starttime))
        
        ########################### recommend ###########################
        print("recommend start")
        starttime = time.time()
        tmp = dict()
        rs_dir = "/work/urs-server/recommend_hairdataset/UT/"
        if mode == "V2":
            rs_dir = "/work/urs-server/recommend_hairdataset/UT/V2/"
        user_id = Person.objects.get(no=int(rs_data['person']))
        user_id = user_id.user_id
        tmp.update(rs.get_rs_result(face_json, user_id, rs_dir))
        #print((tmp))
        if mode == "DEMO" :
            hair_name = dict()
            hair_name["0182.jpg"] = "에어펌"
            hair_name["0190.jpg"] = "시스루뱅프릴펌"
            hair_name["0211.jpg"] = "시스루뱅모즈컷"
            hair_name["0219.jpg"] = "그레이스펌"
            for idx in range(0, 4):
                if tmp[str(idx)]["name"] in hair_name:
                    tmp[str(idx)]["title"] = hair_name[tmp[str(idx)]["name"]]
           # tmp["1"]["title"] = hair_name[tmp["1"]["name"]]
           # tmp["2"]["title"] = hair_name[tmp["2"]["name"]]
           # tmp["3"]["title"] = hair_name[tmp["3"]["name"]]

        rs_data['recommend_result_hairList_json'] = tmp
        endtime = time.time()
        print("recommend end - process time : " + str(endtime - starttime))
        
        ########################### personal color ###########################
        print("personal color start")
        starttime = time.time()
        rs_data['color_info'] = pc.get_pc("/work/urs-server/myapp/personal_color/79999_iter.pth", path)
        endtime = time.time()
        print(rs_data['color_info'])
        print("personal color end - process time : " + str(endtime - starttime))
        total_time_end = time.time()
        print("total_time : " + str(total_time_end - total_time_start))
        date = datetime.now()
        date = str(date.year) + ". " + str(date.month) + '. '+ str(date.day) + '.'
        print(date)
        rs_data['date'] = str(date)
        rs_serializer = RecommendTestSerializer(data = rs_data)
        if rs_serializer.is_valid():
            rs_serializer.save()
            return JSONResponse(rs_serializer.data, status=status.HTTP_201_CREATED)
        return JSONResponse(rs_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@csrf_exempt
def recommend_update(request):
    if request.method == 'POST':
        rs_data = JSONParser().parse(request)
        if rs_data['save_flag'] == True :
            rs_object = RecommendTest.objects.get(no=rs_data['no'])
            save_data = dict()
            save_data['person'] = rs_object.person
            save_data['image_input'] = rs_object.image_input
            save_data['face'] = rs_object.face
            save_data['face_info'] = rs_object.face_info
            save_data['color_info'] = rs_object.color_info
            save_data['recommend_result_hairList_json'] = rs_object.recommend_result_hairList_json
            save_data['hair_texture'] = rs_object.hair_texture
            save_data['hair_volume'] = rs_object.hair_volume
            save_data['hair_condition'] = rs_object.hair_condition
            save_data['date'] = rs_object.date
            person_tmp = Person.objects.get(no=rs_object.person)
            
            rs_serializer = RecommendResultSerializer(data = save_data)
            rs_object.delete()
            if rs_serializer.is_valid():
                rs_serializer.save()
                person_tmp.last_recommend = rs_serializer.data
                person_tmp.isrecommended = True
                person_tmp.person_save()
                return JSONResponse(rs_serializer.data, status=status.HTTP_201_CREATED)
            return JSONResponse(rs_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def person_save(request):
    if request.method == 'POST':
        # with open('/work/urs-server/myapp/user_id/user_id_test.json', 'r') as f:
        #     user = json.load(f)
        user_obj = UserData.objects.get(version = 1)
        user = user_obj.userid_json
        person_data = JSONParser().parse(request)
        if person_data['user_id'] in user :
            if jsonkey_present(person_data, 'hair_volume') :
                hair_volume = person_data['hair_volume']
            else : 
                hair_volume = 'default'
            if jsonkey_present(person_data, 'hair_texture') :
                hair_texture = person_data['hair_texture']
            else : 
                hair_texture = 'default'
            if jsonkey_present(person_data, 'hair_condition') :
                hair_condition = person_data['hair_condition']
            else : 
                hair_condition = 'default'
            if hair_volume == 'default' and hair_texture == 'default' and hair_condition == 'default':
                tmp = dict()
                tmp["error"] = "userid is already exist."
                return JSONResponse(tmp)
            queryset = PersonTest.objects.get(no=user[person_data['user_id']])
            # serializer_class = PersonSerializer(queryset, context={'request': request})
            print(queryset.no)
            queryset.hair_volume = hair_volume
            print(queryset.hair_volume)
            queryset.hair_texture = hair_texture
            print(queryset.hair_texture)
            queryset.hair_condition = hair_condition
            print(queryset.hair_condition)
            queryset.save() 
            return JSONResponse(PersonTestSerializer(queryset).data)
        user_num = user_obj.nofuser
        person_data['user_num'] = user_num + 1
        person_serializer = PersonTestSerializer(data = person_data)
        if person_serializer.is_valid():
            person_serializer.save()
            user_obj.nofuser = person_data['user_num']
            user[person_data['user_id']] = person_data['user_num']
            user_obj.userid_json = user
            user_obj.save()
            # with open('/work/urs-server/myapp/user_id/user_id_test.json', 'w', encoding='utf-8') as make_file:
            #     json.dump(user, make_file, indent="\t")
            return JSONResponse(person_serializer.data, status=status.HTTP_201_CREATED)
        return JSONResponse(person_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonDetail(RetrieveAPIView):
    lookup_field = 'user_id'
    queryset = Person.objects.all()
    serializer_class = PersonDetailSerializer

class RecommendView(viewsets.ModelViewSet):
    queryset = RecommendResult.objects.all()
    serializer_class = RecommendResultSerializer

class SimulationStyleListView(viewsets.ModelViewSet):
    queryset = SimulationStyleList.objects.all()
    serializer_class = SimulationStyleListSerializer

class GanViewSet(viewsets.ModelViewSet):
    queryset = GanRequest.objects.all()
    serializer_class = GanRequestSeializer


@csrf_exempt
def coldstart_selected(request, user_id, selected_image):
    if request.method == 'GET':
        total = 0.0
        with open('/work/urs-server/myapp/user_id/user_id.json', 'r') as f:
            user = json.load(f)
        if user_id in user :
            rs_img_path = "/work/urs-server/recommend_hairdataset/UT/"
            coldstartJson = dict()
            coldstartArray = coldst.get_similar_hair(rs_img_path, user_id, selected_image)
            index = 0
            for img in coldstartArray:
                img_tmp = Image.open(rs_img_path + "coldstart/" + img.split(".")[0]+".webp")
                start = time.time()
                buffered = BytesIO()
                img_tmp.save(buffered, format="JPEG")
                encoded_string = base64.b64encode(buffered.getvalue())
                end = time.time()
                total += (end - start)
                coldstartJson[img] = str(encoded_string).split("'")[1]
                index += 1
            print("encode time : " + str(total))
            return JSONResponse(coldstartJson)
        else :
            retJson = dict()
            retJson['error'] = 'no user id'
            return JSONResponse(retJson, status=status.HTTP_400_BAD_REQUEST)
@csrf_exempt
def coldstart_listup(request, user_id):
    if request.method == 'POST' :
        data = JSONParser().parse(request)
        print(data)
        s_imgs = data['selected_images']
        s_imgs = s_imgs.replace('\'', '')
        s_imgs = s_imgs.replace('"', '')
        s_imgs = s_imgs.replace('[', '')
        s_imgs = s_imgs.replace(']', '')
        s_imgs = s_imgs.replace(' ', '')
        s_imgs = s_imgs.split(',')
        for s_img in s_imgs :
            coldst.input_score(user_id, s_img)
        return JSONResponse(data)

    if request.method == 'GET':
        start = time.time()
        with open('/work/urs-server/myapp/user_id/user_id.json', 'r') as f:
            user = json.load(f)
        if user_id in user :
            rs_img_path = "/work/urs-server/recommend_hairdataset/UT/"
            coldstartJson = dict()
            coldstartArray = coldst.coldStart(rs_img_path, user_id)
            index = 0
            for img in coldstartArray:              
                # img_tmp = Image.open(rs_img_path + img)
                img_tmp = Image.open(rs_img_path + "coldstart/" + img.split(".")[0] + ".webp")
                buffered = BytesIO()
                # img_tmp.save(buffered, format="jpeg")
                img_tmp.save(buffered, format="webp")
                encoded_string = base64.b64encode(buffered.getvalue())
                coldstartJson[img] = str(encoded_string).split("'")[1]
                index += 1
            end = time.time()
            print("coldstart time : " + str(end-start))
            return JSONResponse(coldstartJson)
        else :
            retJson = dict()
            retJson['error'] = 'no user id'
            return JSONResponse(retJson, status=status.HTTP_400_BAD_REQUEST)
@csrf_exempt
def person_test(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        with open('/work/urs-server/myapp/user_id/user_id.json', 'r') as f:
            user = json.load(f)
        if data['user_id'] in user :
            person_no = user[data['user_id']]
            queryset = Person.objects.get(no=person_no)
            serializer_class = PersonSerializer(queryset, context={'request': request})
            personJson = serializer_class.data
            rs_str = str(personJson['recommend_result'][0]).split('/')[4]
            rsset = RecommendResult.objects.get(no=int(rs_str))
            RSserializer = RecommendResultSerializer(rsset)
            return JSONResponse(RSserializer.data)
        else :
            queryset = Person.objects.all()
            serializer_class = PersonSerializer
            newdata = Person(data)
            newdata.save()
            return JSONResponse(newdata)


class ColdStartSet(viewsets.ModelViewSet):
    queryset = ColdStart.objects.all()
    serializer_class = ColdStartSerializer
