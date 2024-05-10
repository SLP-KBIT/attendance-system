import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Date, User
import unicodedata

# JSONファイル開く
with open('/app/data.json', 'r') as json_file:
    json_datas = json.load(json_file)

# SQLiteデータベースに接続
engine1 = create_engine('sqlite:///date.db')
engine2 = create_engine('sqlite:///user.db')

# SQLAlchemyセッションを作成
Session1 = sessionmaker(bind=engine1)
session1 = Session1()
Session2 = sessionmaker(bind=engine2)
session2 = Session2()

# 学籍番号から名前と学年を探す関数
for json_data in json_datas:

    # フリガナ設定
    user = session2.query(User).filter(User.number == json_data["number"]).first()
    if user.furigana == "":
        user.furigana = unicodedata.normalize('NFKC', json_data["furigana"])
        session2.commit()

    # 文字列型から日時型に変換
    date_object = datetime.strptime(json_data["timestamp"], "%Y-%m-%d %H:%M:%S")

    # AttendanceDBに保存するための型を用意
    attendance = Date(number=json_data["number"], date=date_object)

    # AttendanceDBに追加(※ステージング)
    session1.add(attendance)

# 変更内容をデータベースに反映
session1.commit()

# セッションを閉じる
session1.close()
session2.close()