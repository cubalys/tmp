#!/usr/bin/env python
# coding: utf-8

import torch
from torch import nn
from torchvision import transforms
from PIL import Image
import sys
import os

model_path = sys.argv[1]
img_path = sys.argv[2]
use_cuda = True
image_size=(160,160)
class_names=['heart', 'oblog', 'oval', 'round', 'square']


class Flatten(nn.Module):
    def __init__(self):
        super(Flatten, self).__init__()
        
    def forward(self, x):
        x = x.view(x.size(0), -1)
        return x
class normalize(nn.Module):
    def __init__(self):
        super(normalize, self).__init__()
        
    def forward(self, x):
        x = F.normalize(x, p=2, dim=1)
        return x


model_ft = torch.load(model_path)



def predict_breed_transfer(img_path):
    
    #Preprocessing the input image
    transform = transforms.Compose([
        transforms.Resize(size=image_size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    img = Image.open(img_path)
    img = transform(img)[:3,:,:].unsqueeze(0)
    if use_cuda:
        img = img.cuda()
        model_ft.to('cuda')
        # Passing throught the model
    model_ft.eval()
    # Checking the name of class by passing the index

    #print(class_names)
    idx = torch.argmax(model_ft(img))
    return class_names[idx]


    output = model_ft(img)
    # Probabilities to class
    pred = output.data.max(1, keepdim=True)[1]
    return pred, output


if os.path.isfile(img_path):   
    print(predict_breed_transfer(img_path))
else:
    print("Please check your input image")

