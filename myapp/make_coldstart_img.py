from PIL import Image
import os
Dir = "/work/urs-server/recommend_hairdataset/UT/"
resDir = "/work/urs-server/recommend_hairdataset/UT/coldstart/"

FileList = os.listdir(Dir)
idx = 0
for img in FileList :
    if '.jpg' in img :
        idx += 1
        print(str(idx) + ". " + str(img))
        im = Image.open(Dir + img).convert('RGB')
        im = im.resize((256, 256), Image.NEAREST)
        img_name = img.split('.')
        im.save(resDir + img_name[0] + ".webp", 'webp')
