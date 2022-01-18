import cv2
import numpy as np
import requests
import time
from PIL import Image
def faceppAPI(filename):
    URL = "https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark"
    API_KEY = "-D9lXEJg0Z0MMuSHKtmKxetMLqYkZp2c"
    API_SECRET = "2At_EM1UjwJHSzE_j325L2KxbXjDrefE"
    img_cv = cv2.imread(filename)
    binary_cv = cv2.imencode('.PNG', img_cv)[1].tobytes()
    parameters = dict(api_key=API_KEY, api_secret=API_SECRET, return_landmark='all')
    response = requests.post(URL, data=parameters, files={'image_file': binary_cv})
    return response.json()

face = faceppAPI('/work/urs-server/myapp/img_trans_test/ref.jpg')

print(face['face']['face_rectangle'])
ref_rectangle = face['face']['face_rectangle']
time.sleep(6)
 
face2 = faceppAPI('/work/urs-server/myapp/img_trans_test/src.jpg')
src_rectangle = face2['face']['face_rectangle']
print(face2['face']['face_rectangle'])
img = cv2.imread('/work/urs-server/myapp/img_trans_test/src.jpg') 

dx_2 = ref_rectangle['width'] / src_rectangle['width']
dy_2 = ref_rectangle['height'] / src_rectangle['height']
dst2 = cv2.resize(img, None,  None, dx_2, dy_2, cv2.INTER_CUBIC)
cv2.imwrite('/work/urs-server/myapp/img_trans_test/res_2.jpg', dst2)
time.sleep(6)
face3 = faceppAPI('/work/urs-server/myapp/img_trans_test/res_2.jpg')
print(face3['face']['face_rectangle'])
src_rectangle = face3['face']['face_rectangle']
rows,cols = img.shape[0:2]
dx = ref_rectangle['left'] - src_rectangle['left']
dy = ref_rectangle['top'] - src_rectangle['top']
mtrx = np.float32([[1, 0, dx],
                   [0, 1, dy]]) 
dst = cv2.warpAffine(img, mtrx, (cols+dx, rows+dy), None, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT, (255,255,255) )

cv2.imwrite('/work/urs-server/myapp/img_trans_test/res.jpg', dst)
im = Image.open('/work/urs-server/myapp/img_trans_test/ref.jpg')
print(' ref : ' + str(im.size))
im = Image.open('/work/urs-server/myapp/img_trans_test/src.jpg')
print(' src : ' + str(im.size))
im = Image.open('/work/urs-server/myapp/img_trans_test/res.jpg')
croppedImage=im.crop((0,0,256,256))
croppedImage.save('/work/urs-server/myapp/img_trans_test/res.jpg')
im = Image.open('/work/urs-server/myapp/img_trans_test/res.jpg')
print(' res : ' + str(im.size))