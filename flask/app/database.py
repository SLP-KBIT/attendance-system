from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# データベースのORMモデルを定義
Base = declarative_base()

# AttendanceDBの内容定義
class AttendanceDB(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    number = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    grade = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)

# NameDBの内容定義
class NameDB(Base):
    __tablename__ = 'name'
    id = Column(Integer, primary_key=True)
    number = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    grade = Column(String(10), nullable=False)

# SQLiteデータベースに接続
engine1 = create_engine('sqlite:///attendance.db')
engine2 = create_engine('sqlite:///name.db')

# データベースを作成
Base.metadata.create_all(engine1)
Base.metadata.create_all(engine2)

# # SQLAlchemyセッションを作成
# Session1 = sessionmaker(bind=engine1)
# session1 = Session1()

# Session2 = sessionmaker(bind=engine2)
# session2 = Session2()

# # # # データを追加
# # name = NameDB(number='21T000', name='ずんだもん', grade='B3')

# # session2.add(name)

# # # # 変更をデータベースにコミット
# # session2.commit()

# # データを取得
# datas = session2.query(NameDB).all()

# # 取得したデータを表示
# # for data in datas:
# #     print(f"number: {data.number}, Name: {data.name}, grade: {data.grade}")

# # セッションを閉じる
# session1.close()
# session2.close()