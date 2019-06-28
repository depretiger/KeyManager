import binascii
import nfc
import signal
import datetime
import sqlite3
import os
from os.path import join, dirname
from dotenv import load_dotenv

from linebot import LineBotApi
from linebot.models import TextSendMessage


class MyCardReader(object):

    def on_connect(self, tag):
        print ("読み取り中")
        self.idm = binascii.hexlify(tag.idm)
        return True

    def read_idm(self):
        clf = nfc.ContactlessFrontend('usb')
        try:
            clf.connect(rdwr = {'on-connect': self.on_connect})
        finally:
            clf.close()


class LineBotSender:

    def __init__(self):
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
        self.line_bot_api = LineBotApi(channel_access_token)

        self.group_id = os.environ.get('GROUP_ID')

    def sendMessage(self,message):
        messages = TextSendMessage(text=message)
        self.line_bot_api.push_message(self.group_id, messages=messages)


class DatabaseEdit:

    def table_display(self):
        # 確認
        con = sqlite3.connect('./idm_list.db')
        c = con.cursor()
        select_sql = 'select * from Felica'
        for row in c.execute(select_sql):
            print(row)
        con.close()

    def update_time(self,idm):
        dt_now = datetime.datetime.now()
        now = dt_now.strftime('%H:%M')
        con = sqlite3.connect('./idm_list.db')
        c = con.cursor()
        # 前回の時間とステータスを取得
        select_sql = "select * from Felica where IDm='%s'" % idm
        for row in c.execute(select_sql):
            lasttime = row[2]
            status = row[3]
            name = row[0]
        # 前回と時間が同じならステータスを更新
        if (lasttime == now):
            con.commit()
            return("連続タッチのため更新しません")
        else:
            c.execute("update Felica set time='%s' where IDm='%s'" % (now, idm))
            if status == "offline":
                status = "online"
            else:
                status = "offline"

            c.execute("update Felica set status='%s' where IDm='%s'" % ("status", idm))
            con.commit()
            return(name +"さんがofflineになりました")
        # 確認するとき
        # self.table_display()


if __name__ == '__main__':
    cr = MyCardReader()
    de = DatabaseEdit()
    lbs = LineBotSender()    

    while True:
        print ("カードをタッチしてください")
        cr.read_idm()
        #16進数16桁の文字列にする
        new_idm = str(cr.idm)
        new_idm = new_idm[2:-1]

        # print ("カードのID: ",end='')
        # print (new_idm)
        
       # 更新
        message = de.update_time(new_idm)
        print(message) 
        lbs.sendMessage(message)

        # Ctrl-Cで終了するまで待機し続ける
        signal.signal(signal.SIGINT,signal.SIG_DFL)
