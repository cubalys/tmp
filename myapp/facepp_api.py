import requests 
import base64
import json 
import cv2
# POST (JSON) 
def get_facepp_api(filepath):
    URL = "https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark"
    API_KEY = "-D9lXEJg0Z0MMuSHKtmKxetMLqYkZp2c"
    API_SECRET = "2At_EM1UjwJHSzE_j325L2KxbXjDrefE"
    img_cv = cv2.imread(filepath)
    binary_cv = cv2.imencode('.PNG', img_cv)[1].tobytes()
    parameters = dict(api_key=API_KEY, api_secret=API_SECRET, return_landmark='all')
    response = requests.post(URL, data=parameters, files={'image_file': binary_cv})
    return response

