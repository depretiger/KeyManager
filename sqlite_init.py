import sqlite3

con = sqlite3.connect('./idm_list.db')
c = con.cursor()
# 生成する
# sql = """
# create table Felica (name varchar(64), IDm varchar(200), time varchar(32), status varchar(32))
# """
# c.execute(sql)

# 追加する
sql = 'insert into Felica (name, IDm, time, status) values (?,?,?,?)'
user1 = ('tanaka', '01018a10d9163d05', '20:37', 'offline')
user2 = ('suzuki', '012e3d1c98b4d6f8a', '10:21', 'offline')
c.execute(sql,user1)
c.execute(sql,user2)
con.commit()


select_sql = 'select * from Felica'
for row in c.execute(select_sql) :
    print(row)
con.close()

