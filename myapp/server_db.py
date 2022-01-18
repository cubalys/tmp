import psycopg2
# conn = psycopg2.connect(host='localhost', dbname='mydb', user='myuser', password='password', port='5432')
# cur = conn.cursor()
#cur.execute("CREATE TABLE test_table (title varchar, content text);") 
# cur.execute("insert into test_table (title, content) values ('a', 'b');") 
# cur.execute("select * from test_table;") 
# print (cur.fetchone())
# conn.commit()

def create_table(conn, cur, table_name, table_info):
    cur.execute("create table " + table_name + " (" + table_info + ");")
    conn.commit()

def read_table(conn, cur, table_name, table_column):
    cur.execute("select "+ table_column + " from " + table_name + ";") 
    print (cur.fetchone())
    conn.commit()
    return cur
def read_table_2(conn, cur, table_name, table_column, where):
    cur.execute("select "+ table_column + " from " + table_name + " where " + where + ";") 
    return cur.fetchone()
    conn.commit()
    return cur

def insert(conn, cur, table_name, columns, values):
    cur.execute("insert into " + table_name + " (" + columns + ") values (" + values + ");")
    conn.commit()

def update(conn, cur, table_name, set, where):
    cur.execute("update " + table_name + " set " + set + " where " + where + ";")
    conn.commit()

def drop_table(conn, cur, table_name):
    cur.execute("drop table " + table_name + ";")
    conn.commit()

