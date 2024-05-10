from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# データベースのORMモデルを定義
Base = declarative_base()

# AttendanceDBの内容定義
class Date(Base):
    __tablename__ = 'date'
    id = Column(Integer, primary_key=True, unique=True)
    number = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)

# Userデータベースの内容定義
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True)
    uid = Column(String, nullable=False)
    number = Column(String(10), nullable=False, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    grade = Column(String(10), nullable=False)
    furigana = Column(String(50))

# SQLiteデータベースに接続
engine1 = create_engine('sqlite:///date.db')
engine2 = create_engine('sqlite:///user.db')

# データベースを作成
Base.metadata.create_all(engine1)
Base.metadata.create_all(engine2)