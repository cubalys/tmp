import server_db
import psycopg2
import json
# crud = input()

with open('/work/urs-server/data/face_ratio.json', 'r') as f:
    face_ratio = json.load(f)
with open('/work/urs-server/data/face_shape.json', 'r') as f:
    face_shape = json.load(f)
conn = psycopg2.connect(host='localhost', dbname='mydb', user='myuser', password='password', port='5432')
cur = conn.cursor()
str_face_ratio = json.dumps(face_ratio)
str_face_shape = json.dumps(face_shape)
print(str_face_shape)
cur = server_db.insert(conn, cur, "content_table", "title, content","face_shape, [" + str_face_shape +"]") 
cur = server_db.read_table_2(conn, cur, "content_table", "content","title='face_shape'")
# print(server_db.read_table(conn, cur, "content_table", "content"))# ,"title='face_ratio'"))
str_res = str(cur) #.split('[')[1].split(']')[0]
print(str_res)
str_res_json = str(cur).replace("\'","\"")
json_res = json.loads(str_res_json)
print(json_res)

conn.close()
