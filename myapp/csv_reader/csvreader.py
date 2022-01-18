import csv
import json
import os 
share_dir = '/data/baidu/seeprettyface_wanghong/'
server_dir = '/work/urs-server/recommend_hairdataset/openlab/'
f = open('openlab_rs_image.csv','r', encoding='utf-8')
rdr = csv.reader(x.replace('\0', '') for x in f)
rs_name = dict()
for line in rdr:
    if line[1] != '':
        if '.png' in line[1]:
            os.system('cp ' + share_dir + line[1] + ' ' + server_dir)
            rs_name[line[1]] = line[2]
with open('/work/urs-server/recommend_hairdataset/openlab/name.json', 'w', encoding='utf-8') as make_file:
    json.dump(rs_name, make_file, indent="\t")
with open('/work/urs-server/recommend_hairdataset/openlab/name.json', 'r') as f:
    json_data = json.load(f)
print(json_data)