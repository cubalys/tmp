#!/usr/bin/env python
# coding: utf-8

#from .logger import setup_logger
from .model import BiSeNet

import torch

import os
import sys
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import torchvision.transforms as transforms
import cv2

from colormath.color_objects import LabColor, sRGBColor, HSVColor 
from colormath.color_conversions import convert_color

from .WB_sRGB_Python.classes import WBsRGB as wb_srgb

import json

import time
start = time.time()


#image_path='./data/claire.png'
#image_path=sys.argv[1]
#model_path="res/cp/79999_iter.pth"

wbModel = wb_srgb.WBsRGB(gamut_mapping=2,upgraded=0) 

def vis_parsing_maps(im, parsing_anno, stride, save_im=False, save_path='vis_results/parsing_map_on_im.jpg'):
    # Colors for all 20 parts
    part_colors = [[255, 0, 0], [255, 85, 0], [255, 170, 0],
                   [255, 0, 85], [255, 0, 170],
                   [0, 255, 0], [85, 255, 0], [170, 255, 0],
                   [0, 255, 85], [0, 255, 170],
                   [0, 0, 255], [85, 0, 255], [170, 0, 255],
                   [0, 85, 255], [0, 170, 255],
                   [255, 255, 0], [255, 255, 85], [255, 255, 170],
                   [255, 0, 255], [255, 85, 255], [255, 170, 255],
                   [0, 255, 255], [85, 255, 255], [170, 255, 255]]

    im = np.array(im)
    vis_im = im.copy().astype(np.uint8)
    vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
    vis_parsing_anno = cv2.resize(vis_parsing_anno, None, fx=stride, fy=stride, interpolation=cv2.INTER_NEAREST)
    vis_parsing_anno_color = np.zeros((vis_parsing_anno.shape[0], vis_parsing_anno.shape[1], 3)) + 255

    num_of_class = np.max(vis_parsing_anno)

    for pi in range(1, num_of_class + 1):
        index = np.where(vis_parsing_anno == pi)
        vis_parsing_anno_color[index[0], index[1], :] = part_colors[pi]

    vis_parsing_anno_color = vis_parsing_anno_color.astype(np.uint8)
    # print(vis_parsing_anno_color.shape, vis_im.shape)
    vis_im = cv2.addWeighted(cv2.cvtColor(vis_im, cv2.COLOR_RGB2BGR), 0.4, vis_parsing_anno_color, 0.6, 0)

    # Save result or not
    if save_im:
        cv2.imwrite(save_path[:-4] +'.png', vis_parsing_anno)
        print(save_path[:-4] +'.png')
        #cv2.imwrite(save_path, vis_im, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        print(save_path)

    # return vis_im

def get_pc(model_path, image_path):
    net = BiSeNet(n_classes=19)
    net.cuda()
    net.load_state_dict(torch.load(model_path))
    net.eval()

    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])

    img = cv2.imread(image_path)
    img = wbModel.correctImage(img)
    image=cv2.resize(img, (512,512))
    image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    with torch.no_grad():
        img = to_tensor(image)
        img = torch.unsqueeze(img, 0)
        img = img.cuda()
        out = net(img)[0]
        parsing = out.squeeze(0).cpu().numpy().argmax(0)
        # print(parsing)
        # print(np.unique(parsing))

        vis_parsing_maps(image, parsing, stride=1)

    changed = np.zeros_like(image)
    changed[parsing == 1]=image[parsing == 1]

    eyes=np.concatenate((np.where(parsing==4)[0], np.where(parsing==5)[0]))
    nose=np.where(parsing==10)[1]
    lip=np.concatenate((np.where(parsing==11)[0], np.where(parsing==12)[0], np.where(parsing==13)[0]))
    
    if len(eyes) and len(nose) and len(lip):
        eyes_bottom=eyes[eyes.argmax()]
        nose_right=nose[nose.argmax()]
        nose_left=nose[nose.argmin()]
        lip_upper=lip[lip.argmin()]

        changed[:eyes_bottom]=0
        changed[:,nose_left:nose_right]=0
        changed[lip_upper:]=0

    '''
    http://www.koreascience.or.kr/article/JAKO201810237886055.pdf
    ????????? ?????? ?????? ??? ?????? ????????? ????????? ?????? ?????? ????????? ?????? ??????(??????????????????????????????????)
    '''

    pc_threshold=[65.2, 18.5, 0.33] #hsv v, lab b*, hsv s


    #get skin color(rgb, lab, hsv)
    rgb=changed.sum(axis=0).sum(axis=0)/sum(sum(changed.sum(axis=2)>0))
    rgb_tmp = sRGBColor(rgb[0],rgb[1],rgb[2], is_upscaled=True)
    lab = convert_color(rgb_tmp, LabColor, through_rgb_type=sRGBColor)
    hsv = convert_color(rgb_tmp, HSVColor, through_rgb_type=sRGBColor)

    extracted_color=[hsv.hsv_v*100, lab.lab_b, hsv.hsv_s]

    color_cmp=list(np.array(extracted_color)>np.array(pc_threshold))

    #hsv v, lab b*, hsv s
    #Luminance/Value/Contrast/Dept: light and dark/deep
    #Saturation/Chroma/Clarity/Intensity/Tone: muted/soft and bright/clear

    '''
    pc_type_table={"Spring warm bright": [True, True, True], 
                   "Spring warm light": [True, True, False],
                   "Summer cool light": [True, False, False],
                   "Summer cool mute": [False, False, False],
                   "Autumn warm mute": [False, True, False],
                   "Autumn warm deep": [False, True, True],
                   "Winter cool deep": [False, False, True],
                   "Winter cool bright": [True, False, True]}
    '''

    pc_type_table={"Spring warm": [[True, True, True], [True, True, False]],
                   "Summer cool": [[True, False, False], [False, False, False]],
                   "Autumn warm": [[False, True, False], [False, True, True]],
                   "Winter cool": [[False, False, True], [True, False, True]]}


    '''
    Color list
    ??? ??????
    ????????????, ??????????????????
    ???????????? 
    ?????????????????????, ????????? ????????????
    ????????????
    ???????????? ?????????, ???????????????
    ????????????
    ????????? ??????, ???????????? ???
    https://www.miseenscene.com/kr/ko/likeit-hair/hair-note/1306270_21441.html
    '''
    for pc, l in pc_type_table.items():
        if color_cmp in l:
            with open('/work/urs-server/myapp/personal_color/personal_color.json', 'r') as f:
                personal_color_info = json.load(f)
            return personal_color_info[pc]
                     


    #print(time.time()-start,"sec")
