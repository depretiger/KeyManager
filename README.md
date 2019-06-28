# KeyManager

自転車の鍵をFelicaで管理するアプリケーションを作りました。LINEのグループに通知します。

## 処理の流れ：SQLite

### データベースの作成

事前にデータベースをsqlite_init.pyで作っておきます。今回はidm_list.dbという名前で作成しました。

```python
import sqlite3

con = sqlite3.connect('./idm_list.db')
c = con.cursor()
sql = """
create table Felica (name varchar(64), IDm varchar(200), time varchar(32), status varchar(32))
"""
c.execute(sql)
```

### レコードの追加

任意でデータを追加します。

```python
import sqlite3

con = sqlite3.connect('./idm_list.db')
c = con.cursor()
sql = 'insert into Felica (name, IDm, time, status) values (?,?,?,?)'
user1 = ('tanaka', '01018a10d9163d05', '20:37', 'offline')
user2 = ('suzuki', '012e3d1c98b4d6f8a', '10:21', 'offline')
c.execute(sql,user1)
c.execute(sql,user2)
con.commit()
```

### 中身を確認する

データベースの中身を見たいときは以下のようにします。

```python
import sqlite3

con = sqlite3.connect('./idm_list.db')
c = con.cursor()
select_sql = 'select * from Felica'
for row in c.execute(select_sql) :
    print(row)
con.close()
```



## 処理の流れ：Felica読み取り

FelicaのIDmをRC-S380で読み取ります。

```python
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
```

## 処理の流れ：データベース

間違えて連続でタッチしないように時間で判定するようにしています。

statusがonlineのときは自転車を利用中、offlineのときは自転車を利用していないことを表しています。status更新とともにtimeも更新しておきます。

```python
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
                msg = "さんが自転車に乗ります。気をつけてね！"
            else:
                status = "offline"
                msg = "さんが自転車を返しました。お帰りなさい！"

            c.execute("update Felica set status='%s' where IDm='%s'" % ("status", idm))
            con.commit()
            return(name + msg )
        # 確認するとき
        # self.table_display()
```

## 処理の流れ：LINEで通知

同じディレクトリ内の.envファイルから環境変数を取り出してLINEBotAPIをつかってLINEのグループに通知します。

```python
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
```

