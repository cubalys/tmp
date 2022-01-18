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
import myapp.stargan_v2.gen_img as gi1
import myapp.LOHO.gen_img as gi2
import myapp.crop_img as cr
from glob import glob
import shutil
import myapp.cold_start as coldst
from django.http import HttpRequest as request
from urllib import parse
import uuid
sys.path.append("/work/urs-server/myapp/Scon_dyeing")
from django.http import HttpResponse
import myapp.Scon_dyeing.dyeing_img as di
from myapp.LOHO import get_mask_img2 as gmi
import traceback
import multiprocessing as mp
import threading
print("thread set ")
sem = threading.Semaphore(1)
current_path = os.getcwd()
# class JSONResponse(HttpResponse):
#     def __init__(self, data, **kwargs):
#         content = JSONRenderer().render(data)
#         kwargs['content_type'] = 'application/json'
#         super(JSONResponse, self).__init__(content, **kwargs)
class UserData(models.Model):
    version = models.AutoField(db_column='NO', primary_key=True) 
    userid_json = models.JSONField(default=dict)
    nofuser = models.IntegerField(default=-1)

class SconData(models.Model):
    version = models.AutoField(db_column='NO', primary_key=True)
    personalcolor_info = models.JSONField(default=dict)
    recommend_hair_domain = models.JSONField(default=dict)
    face_shape_info = models.JSONField(default=dict)
    face_ratio_info = models.JSONField(default=dict)
    def save(self, *args, **kwargs):
        super(SconData, self).save(*args, **kwargs)
# Create your models here.
class PersonTest(models.Model):
    no = models.AutoField(db_column='NO', primary_key=True)
    user_id = models.CharField(max_length=10,default='0')
    user_num = models.IntegerField(default = -1)
    # useridjson = models.ForeignKey(Useridjson, on_delete=models.CASCADE, related_name="person", null=True, blank=True)
    last_recommend = models.JSONField(default = dict)
    isexist = models.BooleanField(default = False)
    isrecommended = models.BooleanField(default = False)
    hair_texture = models.TextField(default = "default")
    hair_volume = models.TextField(default = "default")
    hair_condition = models.TextField(default = "default")
    def save(self, *args, **kwargs):
        super(PersonTest, self).save(*args, **kwargs)
        print(self.no)
        print(self.user_num)

class RecommendTest(models.Model):
    no = models.AutoField(db_column='NO', primary_key=True)
    person = models.IntegerField(default=-1)
    image_input = models.TextField(default = 'default')
    face = models.JSONField(default=dict)
    face_info=models.JSONField(default=dict)
    color_info = models.JSONField(default=dict)
    hair_texture = models.TextField(default = "default")
    hair_volume = models.TextField(default = "default")
    hair_condition = models.TextField(default = "default")
    date = models.TextField(default="default")
    # cropped_image = models.TextField(default=0)
    # recommend_result_hairList = models.BinaryField(default=b'\x08')
    recommend_result_hairList_json = models.JSONField(default=dict)
    def save(self, *args, **kwargs):
        super(RecommendTest, self).save(*args, **kwargs)
        
class Person(models.Model):
    no = models.AutoField(db_column='NO', primary_key=True)
    user_id = models.CharField(max_length=10,default='0')
    user_num = models.IntegerField(default = -1)
    last_recommend = models.JSONField(default = dict)
    isexist = models.BooleanField(default = False)
    isrecommended = models.BooleanField(default = False)
    # hair_texture = models.TextField(default = "default")
    # hair_volume = models.TextField(default = "default")
    # hair_condition = models.TextField(default = "default")
    def person_save(self, *args, **kwargs):
        super(Person, self).save(*args, **kwargs)
    def save(self, *args, **kwargs):
        with open('/work/urs-server/myapp/user_id/user_id.json', 'r') as f:
            user = json.load(f)
        if self.user_id in user :
            person_tmp = Person.objects.get(no = user[self.user_id])
            # tmp = "http://192.168.0.14:8080/persons/" + str(user[self.user_id]) + "/"
            # response = requests.get(tmp)
            # tmp = response.json() #["recommend_result"] 
                # response = requests.get(tmp[0])
                # self.last_recommend = response.json()
            self.isrecommended = person_tmp.isrecommended
            self.last_recommend = person_tmp.last_recommend # ["last_recommend"]
            self.user_num = user[self.user_id]
            self.isexist = True
        else :
            super(Person, self).save(*args, **kwargs)
            self.user_num = self.no
            user[self.user_id] = self.no
            with open('/work/urs-server/myapp/user_id/user_id.json', 'w', encoding='utf-8') as make_file:
                json.dump(user, make_file, indent="\t")
    


class RecommendResult(models.Model):
    no = models.AutoField(db_column='NO', primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="recommend_result", null=True, blank=True)
    #image_input = models.ImageField(upload_to="media", default='default.jpeg')
    image_input = models.TextField(default = 'default')
    face = models.JSONField(default=dict)
    face_info=models.JSONField(default=dict)
    color_info = models.JSONField(default=dict)
    # cropped_image = models.TextField(default=0)
    # recommend_result_hairList = models.BinaryField(default=b'\x08')
    recommend_result_hairList_json = models.JSONField(default=dict)
    hair_texture = models.TextField(default = "default")
    hair_volume = models.TextField(default = "default")
    hair_condition = models.TextField(default = "default")
    date = models.TextField(default="default")
    def save(self, *args, **kwargs):
        super(RecommendResult, self).save(*args, **kwargs)
    # def save(self, *args, **kwargs):
    #     total_time_start = time.time()
    #     face_info_tmp=dict()
    #     imgdata = base64.b64decode(self.image_input)
    #     filename = str(uuid.uuid1()) + ".jpg"  # I assume you have a way of picking unique filenames
    #     path = '/work/urs-server/media/media/' + filename
    #     with open(path, 'wb') as f:
    #         f.write(imgdata)
        
    #     # path = '/work/urs-server/media/' + self.image_input.url
    #     # self.image_input = path
    #     print(self.save_flag)
    #     if self.save_flag : 
    #         self.person.isrecommended = True
    #     self.person.user_num = self.person.no
    #     self.person.isexist = True
    #     self.person.save()
        
    #     ########################### facepp API##########################
    #     print("facepp api start")
    #     starttime = time.time()
    #     face_json = shape.get_facepp_api_res(path)
    #     self.face = face_json
    #     print(face_json)
    #     endtime = time.time()
    #     print("facepp api end - process time : " + str(endtime - starttime))
        
    #     ########################### faceinfo ###########################
    #     print("faceinfo start")
    #     starttime = time.time()
    #     face_info_tmp.update(shape.get_face_info(face_json))
    #     # print(shape.get_face_info(face_json))
    #     print(type(face_info_tmp))
    #     self.face_info = face_info_tmp
    #     endtime = time.time()
    #     print("faceshape end - process time : " + str(endtime - starttime))
        
    #     ########################### recommend ###########################
    #     print("recommend start")
    #     starttime = time.time()
    #     print(self.person.user_id)
    #     tmp = dict()
    #     tmp.update(rs.get_rs_result(face_json, self.person.user_id))
    #     #print((tmp))
    #     self.recommend_result_hairList_json = tmp
    #     endtime = time.time()
    #     print("recommend end - process time : " + str(endtime - starttime))
        
    #     ########################### personal color ###########################
    #     print("personal color start")
    #     starttime = time.time()
    #     self.color_info = pc.get_pc("/work/urs-server/myapp/personal_color/79999_iter.pth", path)
    #     endtime = time.time()
    #     print(self.color_info)
    #     print("personal color end - process time : "+ str(endtime - starttime))
    #     total_time_end = time.time()
    #     print("total_time : " + str(total_time_end - total_time_start))
    #     # self.save()
    #     if self.save_flag : 
    #         super(RecommendResult, self).save(*args, **kwargs)
    #     return

class ColdStart(models.Model):
    no = models.AutoField(db_column='NO', primary_key=True)
    user_id = models.CharField(max_length=20, default = 'default')
    selected_image = models.CharField(max_length=50, default = 'default')
    coldstart = models.JSONField(default=dict)
    def save(self, *args, **kwargs):
        super(ColdStart, self).save(*args, **kwargs)
        rs_img_path = "/work/urs-server/recommend_hairdataset/UT/"
        return_path = "/recommend_hairdataset/UT/"
        if(self.selected_image == "default"):
            #print(localhost)
            coldstartJson = dict()
            coldstartArray = coldst.coldStart(rs_img_path, self.user_id)
            index = 0
            for img in coldstartArray:
                img_tmp = Image.open(rs_img_path + img)
                img_tmp = img_tmp.resize((256, 256), Image.NEAREST)
                buffered = BytesIO()
                img_tmp.save(buffered, format="JPEG")
                encoded_string = base64.b64encode(buffered.getvalue())
                coldstartJson[img] = str(encoded_string).split("'")[1]
                index += 1
            self.coldstart = coldstartJson
        else:
            coldstartJson = dict()
            coldstartArray = coldst.get_similar_hair(rs_img_path, self.user_id, self.selected_image)
            index = 0
            for img in coldstartArray:
                img_tmp = Image.open(rs_img_path + img)
                img_tmp = img_tmp.resize((256, 256), Image.NEAREST)
                buffered = BytesIO()
                img_tmp.save(buffered, format="JPEG")
                encoded_string = base64.b64encode(buffered.getvalue())
                coldstartJson[img] = str(encoded_string).split("'")[1]
                index += 1
            self.coldstart = coldstartJson

def ErrorLog(error: str):
    curTime= time.strftime("%Y.%m.%d/%H:%M:%S", time.localtime(time.time()))
    with open("/work/urs-server/myapp/log/Log.txt", "a") as f:
        f.write(f"[{curTime}] - {error}\n")

class GanRequest(models.Model):
    no = models.AutoField(db_column='NO', primary_key=True)
    user_image = models.ImageField(upload_to="media", default='default.jpeg')
    hair_color = models.CharField(max_length=20, default = 'default')
    hair_style = models.CharField(max_length=50, default = 'default')
    gan_image = models.ImageField(upload_to="media", default='default.jpeg')
    gan_image_base64 = models.TextField(default = '0')
   
    def save(self, *args, **kwargs):
        user_Dir = "/work/urs-server/media/"
        user_img = self.user_image.url
        super(GanRequest, self).save(*args, **kwargs)
        hair_style_req = self.hair_style
        hair_color_req = self.hair_color
        result_Dir = "/work/urs-server/myapp/gan_result/" + str(self.no) + '/'
        if os.path.isdir(result_Dir) == False :
            os.mkdir(result_Dir)
        mode = 2
        nofcore = 6
        
        if hair_style_req != "default":
            with open('/work/urs-server/data/recommend_hair_domain.json', 'r') as f:
                domain = json.load(f)
            result_name = "fake_image.jpg"
            ref_Dir = "/work/urs-server/recommend_hairdataset/UT/crop/"
            starttime = time.time()
            strno = str(self.no)
            print(strno + " : " + user_img + " + " + self.hair_style)
            src_image=user_Dir + user_img
            image_for_GAN = hair_style_req
            ref_image=ref_Dir + image_for_GAN

            if mode == 99 :
                dirDEMO= '/work/urs-server/DEMO/'
                img = self.hair_style
                with open(dirDEMO + img, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()) 
                time.sleep(0.75)

            if mode == 1:
                cate=domain[image_for_GAN]

                dirPath='/work/urs-server/myapp/stargan_v2'

                src_dir=dirPath + '/assets/representative/input/' + str(self.no) 
                ref_dir=dirPath + '/assets/representative/ref/' + str(self.no)
                
                # src_fl=glob(src_dir+"/*/*")
                # ref_fl=glob(ref_dir+"/*/*")

                # for f in src_fl:
                #     os.remove(f)
                # for f in ref_fl:
                #     os.remove(f)
                #LOHO
                
                cate_dict={"front": {0: "x", 1: "o"}, "len":{0: "short", 1: "mid", 2: "long"}, "style": {0: "straight", 1: "c", 2: "s"}}
                if os.path.isdir(ref_dir):
                    shutil.rmtree(ref_dir)
                os.mkdir(ref_dir)
                
                for cate_key in cate_dict.keys():
                    for mem_key in cate_dict[cate_key].keys():
                        dir_name = cate_key+"_"+cate_dict[cate_key][mem_key]
                        os.mkdir(os.path.join(ref_dir,dir_name))

                shutil.copytree(ref_dir, src_dir)

                src_fn = os.path.basename(src_image)
                shutil.copy(src_image, src_dir + "/" + cate + "/" + src_fn)
                ref_fn = os.path.basename(ref_image)
                shutil.copy(ref_image, ref_dir + "/" + cate + "/" + ref_fn)
                
                with open("/work/urs-server/myapp/stargan_v2/urs_config.json", 'r') as f:
                    urs_config = json.load(f)
                urs_config['ref_dir'] = ref_dir
                urs_config['src_dir'] = src_dir
                urs_config['result_dir'] = result_Dir
                
                #try :
                #mp.set_start_method('spawn')
                #p = mp.Process(target =gi1.main, args=(urs_config, ))
                #p.start()
                #p.join()
                gan_check_file ="/work/urs-server/myapp/log/"+user_img.split('/')[2] + ".txt" 
                with open(gan_check_file, 'a') as f :
                    f.write(str(threading.currentThread()) + "\nstart_gan\n")
                f.close()
                print(strno + " : gan start")
                try :
                
                    sem.acquire()
                    gi1.main(urs_config)
                    sem.release()
                except Exception:
                    err = traceback.format_exc()
                    ErrorLog(str(err))
                print(strno + " : gan end")
                with open(gan_check_file, 'a') as f:
                    f.write("end_gan\n")
                f.close()
                #except Exception:
                #    err = traceback.format_exc()
                #    ErrorLog(str(err))
                shutil.rmtree(src_dir)
                shutil.rmtree(ref_dir)
                shutil.copy(result_Dir + result_name, "/work/urs-server/media/media/gan_result/" + user_img.split('/')[2])
                
                with open(result_Dir + result_name, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read())
                shutil.rmtree(result_Dir)
            if mode == 2 :
                ###test####
                name = src_image.split('/')[-1]
                ref_rectangle = dict(width = 131, top = 93, height = 131, left = 62)
                faceres = shape.get_facepp_api_res(src_image)
                src_rectangle = faceres['face']['face_rectangle']
                dx_scale = ref_rectangle['width'] / src_rectangle['width']
                dy_scale = ref_rectangle['height'] / src_rectangle['height']
                img = cv2.imread(src_image) 
                scaleimg = cv2.resize(img, None,  None, dx_scale, dy_scale, cv2.INTER_CUBIC)
                dx = ref_rectangle['left'] - src_rectangle['left']
                dy = ref_rectangle['top'] - src_rectangle['top']
                mtrx = np.float32([[1, 0, dx],
                                [0, 1, dy]]) 
                rows,cols = 256, 256
                gan_src = cv2.warpAffine(scaleimg, mtrx, (cols+dx, rows+dy), None, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT, (255,255,255) )
                crop_src = gan_src[0:256, 0:256]
                color_coverted = cv2.cvtColor(crop_src, cv2.COLOR_BGR2RGB)
                pil_image=Image.fromarray(color_coverted)

                pil_image.save('/work/urs-server/media/media/gan_src_image/' + name)

                gmi.main('/work/urs-server/media/media/gan_src_image/' + name, "/work/urs-server/media/media/gan_src_image/masks/")
                ########################################
                #gmi.main(src_image, "/work/urs-server/media/media/masks/")
                with open("/work/urs-server/myapp/LOHO/urs_config.json", 'r') as f:
                    urs_config = json.load(f)

                urs_config['image1']=user_img.split('/')[-1]
                urs_config['input_dir'] = "/work/urs-server/media/media/gan_src_image"
                urs_config['image2']=image_for_GAN
                urs_config['step'] = 200
                gi2.main(urs_config)
                with open("/work/urs-server/media/media/gan_result/" + urs_config['image1'].split('.')[0]+'.png', "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read())
            # print(user_img.split('/')[2])
            self.gan_image_base64 = encoded_string.decode().strip()
            # os.remove(result_Dir + result_name)
            endtime = time.time()
            # with open(gan_check_file, 'a') as f :
            #     f.write("send_result\n")
            # f.close()
            print(strno + " : GAN process time : " + str(endtime - starttime))
        if hair_color_req != "default":
            starttime = time.time()
            result_name = "color_image.jpg"
            ref_Dir = "/work/urs-server/color_dataset/" 
            # #sys.path.append("/work/urs-server/myapp/Scon_dyeing/")
            # os.chdir("/work/urs-server/myapp/Scon_dyeing")
            sem.acquire()
            di.run(user_Dir + user_img, ref_Dir + self.hair_color + '.jpg', result_Dir + result_name)
            sem.release()
            # os.chdir(current_path)
            # os.chdir("/work/urs-server/myapp/Scon_dyeing")
            # subprocess.run(['python', '/work/urs-server/myapp/Scon_dyeing/main.py', '--data_src_path', user_Dir + user_img, '--data_ref_path', ref_Dir + self.hair_color + '.jpg', '--result_out_path', result_Dir + result_name, '--gpu_ids', '0'])
            # os.chdir(current_path)
            with open(result_Dir + result_name, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            self.gan_image_base64 = encoded_string.decode().strip()
            os.remove(result_Dir + result_name)
            endtime = time.time()
            
            print("GAN process time : " + str(endtime - starttime))

class SimulationStyleList(models.Model):
    no = models.AutoField(db_column='NO', primary_key=True)
    possible_style_img = models.ImageField(upload_to="media", default='default.jpeg')
    simulation_style_img = models.ImageField(upload_to="media", default='default.jpeg')
    recommend = models.ForeignKey(RecommendResult, on_delete=models.CASCADE, related_name="simulation_style_list", null=True, blank=True)
    def __str__(self):
        return f"{self.possible_style_img},{self.simulation_style_img}"
