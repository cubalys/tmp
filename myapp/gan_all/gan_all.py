if __name__ == '__main__':
	if __package__ is None:
		import sys
		from os import path
		print(path.dirname( path.dirname( path.abspath(__file__) ) ))
		sys.path.append(path.dirname( path.dirname( path.abspath(__file__) ) ))
		from stargan_v2 import gen_img as gi
	else:
		from ..stargan_v2 import gen_img as gan_image
import json
import os
from glob import glob
import shutil
from PIL import Image
ref_Dir = "/work/urs-server/recommend_hairdataset/UT/crop/"
with open('/work/urs-server/data/rs_hair_domain_backup.json', 'r') as f:
    domain = json.load(f)
src_image = '/work/urs-server/myapp/gan_all/openlab3.jpg'
result_Dir = "/work/urs-server/myapp/gan_result/"
result_name = "fake_image.jpg"
FileList = os.listdir(ref_Dir)
idx = 1
for file in FileList:
    if '.jpg' in file :
        if file in domain : 
            ref_image=ref_Dir + file
            print(str(idx) + ". " + ref_image)
            cate=domain[file]
            dirPath='/work/urs-server/myapp/stargan_v2'

            src_dir=dirPath + '/assets/representative/input/1'
            ref_dir=dirPath + '/assets/representative/ref/1'
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
            gi.main(urs_config)
            shutil.rmtree(src_dir)
            shutil.rmtree(ref_dir)

            shutil.copy(result_Dir + result_name, "/work/urs-server/myapp/gan_all/openlab3/" + file)
            idx += 1
