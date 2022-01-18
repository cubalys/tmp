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

with open(Directory_rs + "image_name.bin", "rb") as f:
    data_output = f.read()
    image_name = data_output
with open("/work/urs-server/data/UT_vector.csv") as csvfile:
    reader = csv.reader(csvfile) 
    for row in reader :
        if row[0] == selected_image:
            for col in range(1, len(row)):
                selectedImg_vector = np.append(selectedImg_vector, row[col])
