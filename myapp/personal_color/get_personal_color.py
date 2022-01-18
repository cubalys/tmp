#!/usr/bin/env python
# coding: utf-8

from logger import setup_logger
from model import BiSeNet

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

import json

import time
start = time.time()


#image_path='./data/claire.png'
image_path=sys.argv[1]
model_path="./79999_iter.pth"

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

n_classes = 19
net = BiSeNet(n_classes=n_classes)
net.cuda()
net.load_state_dict(torch.load(model_path))
net.eval()

to_tensor = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
])


with torch.no_grad():
    img = Image.open(image_path)
    image = img.resize((512, 512), Image.BILINEAR)
    img = to_tensor(image)
    img = torch.unsqueeze(img, 0)
    img = img.cuda()
    out = net(img)[0]
    parsing = out.squeeze(0).cpu().numpy().argmax(0)
    # print(parsing)
    # print(np.unique(parsing))

    vis_parsing_maps(image, parsing, stride=1)


image2 = cv2.imread(image_path)
image2_tmp=cv2.resize(image2, (512,512))
image2_tmp=cv2.cvtColor(image2_tmp, cv2.COLOR_BGR2RGB)

changed = np.zeros_like(image2_tmp)
changed[parsing == 1]=image2_tmp[parsing == 1]

'''
http://www.koreascience.or.kr/article/JAKO201810237886055.pdf
퍼스널 컬러 스킨 톤 유형 분류의 정량적 평가 모델 구축에 대한 연구(김용현†·오유석·이정훈)
'''

pc_threshold=[65.2, 18.5, 0.33] #hsv v, lab b*, hsv s


#get skin color(rgb, lab, hsv)
skin_list=image2_tmp[parsing == 1]
rgb=np.mean(skin_list,axis=0)
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
봄 웜톤
매트골드, 로즈골드헤어
여름쿨톤 
애쉬카키브라운, 사하라 로즈핑크
가을웜톤
모카라떼 브라운, 초코브라운
겨울쿨톤
더스티 애쉬, 다크초코 턴
https://www.miseenscene.com/kr/ko/likeit-hair/hair-note/1306270_21441.html
'''

hair_color_list={"Spring warm": ["MatGold", "RoseGold"],
               "Summer cool": ["AshKhakiBrown", "SaharaRosePink"],
               "Autumn warm": ["MochaLatteBrown", "ChocoBrown"],
               "Winter cool": ["DustyAsh", "DarkChocoTurn"]}


output_tmp={"personalColor":"", "hairColor":""}
for pc, l in pc_type_table.items():
    if color_cmp in l:
        output_tmp["personalColor"] = pc
        output_tmp["hairColor"]= hair_color_list[pc]
        break


output=json.dumps(output_tmp, indent=4)
print(output)
#print(time.time()-start,"sec")
