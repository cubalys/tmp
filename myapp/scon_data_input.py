import json
import requests
from .models import UserData
from .models import PersonTest
from .serializers import PersonTestSerializer
from .serializers import UserDataSerializer

idx = 1
userJson = dict()
usernum = 0
while True:
    try :
       person = PersonTest.objects.get(no = idx)
       userJson[person.user_id] = person.no
       usernum = person.no
    except:
        break
print(person)
print(usernum)
