import sqlite3
import datetime


def table_display():
    # 確認
    con = sqlite3.connect('./idm_list.db')
    c = con.cursor()
    select_sql = 'select * from Felica'
    for row in c.execute(select_sql):
        print(row)
    con.close()

table_display()
