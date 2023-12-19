from flask import Flask, render_template, request, redirect, Response, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from database import AttendanceDB, NameDB
from datetime import datetime, timedelta
import subprocess

app = Flask(__name__)

# SQLiteデータベースに接続
engine2 = create_engine('sqlite:///name.db')
engine1 = create_engine('sqlite:///attendance.db')

# SQLAlchemyセッションを作成
Session1 = sessionmaker(bind=engine1)
Session2 = sessionmaker(bind=engine2)

# Basic認証のUsername,password
users = {'admin': generate_password_hash('slp2284kbit')}

# Basic認証のチェック関数
def check_auth(username, password):
    if username in users and check_password_hash(users[username], password):
        return True
    return False

# Basic認証エラーメッセージ
def authenticate():
    return Response('出席管理システムにアクセスするには認証が必要です', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

# Basic認証をアプリケーションに適用(Webサイトに表示)
@app.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

def compute_day(post, onDays):
    for onDay in onDays:
        if post == onDay:
            return 0
    return 1

def extrack_name(my_names, post):
    for my_name in my_names:
        if my_name == post.name:
            return 0
    return post.name

# URL:(/)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subprocess.run('sh script.sh', shell=True)
        return redirect('/')

    session1 = Session1()
    posts = session1.query(AttendanceDB).order_by(AttendanceDB.date.desc()).all()
    onDays = []
    for post in posts:
        post = post.date.strftime('%Y-%m-%d')
        if compute_day(post, onDays):
            onDays.append(post)

    session1.close()
    return render_template('index.html', onDays=onDays)


# URL(/date/<指定した日付>)
@app.route('/date/<currentDate_str>', methods=['GET', 'POST'])
def date(currentDate_str):
    if request.method == 'POST':
        session1 = Session1()
        session2 = Session2()
        name = request.form.get('name')

        number = session2.query(NameDB.number).filter(NameDB.name == name).scalar()
        grade = session2.query(NameDB.grade).filter(NameDB.name == name).scalar()

        currentDate = datetime.strptime(currentDate_str, "%Y-%m-%d")

        new_post = AttendanceDB(number=number, name=name, grade=grade, date=currentDate)

        session1.add(new_post)
        session1.commit()
        session1.close()

        return redirect(f'/date/{currentDate_str}')

    currentDate = datetime.strptime(currentDate_str, "%Y-%m-%d")
    session1 = Session1()
    posts = session1.query(AttendanceDB).order_by(AttendanceDB.number).filter(AttendanceDB.date >= currentDate, AttendanceDB.date < currentDate+timedelta(days=1)).all()
    session1.close()

    session2 = Session2()
    posts2 = session2.query(NameDB).order_by(NameDB.number).all()
    session2.close()

    my_names = [100]
    for post in posts:
        tmp_name = extrack_name(my_names, post)
        if tmp_name != 0:
            my_names.append(tmp_name)
    posts = session1.query(AttendanceDB).order_by(AttendanceDB.date).filter(AttendanceDB.date >= currentDate, AttendanceDB.date < currentDate+timedelta(days=1)).all()
    return render_template('date.html', posts=posts, currentDate=currentDate_str, posts2=posts2, my_names=my_names)


# URL(/user/<指定した学籍番号>)
@app.route('/user/<currentNumber>')
def user(currentNumber):
    session1 = Session1()
    posts = session1.query(AttendanceDB).order_by(AttendanceDB.date.desc()).filter(AttendanceDB.number == currentNumber).all()
    lasts = session1.query(AttendanceDB).order_by(AttendanceDB.date.desc()).filter(AttendanceDB.number == currentNumber).first()
    session1.close()
    return render_template('user.html', posts=posts, lasts=lasts)


# URL(/delete/<指定したAttendanceDBのid>)
@app.route('/delete/<int:id>')
def delete(id):
    session1 = Session1()
    post = session1.query(AttendanceDB).get(id)
    session1.delete(post)
    session1.commit()
    session1.close()
    return redirect('/')


# URL(/member)
@app.route('/member', methods=['GET', 'POST'])
def member():
    if request.method == 'GET':
        session2 = Session2()
        posts = session2.query(NameDB).order_by(NameDB.number).all()
        session2.close()
        return render_template('member.html', posts=posts)

    else:
        number = request.form.get('number')
        name = request.form.get('name')
        grade = request.form.get('grade')
        new_post = NameDB(number=number, name=name, grade=grade)

        session2 = Session2()
        session2.add(new_post)
        session2.commit()
        session2.close()
        return redirect('/member')


# URL(/member/delete/<指定したNameDBのid>)
@app.route('/member/delete/<int:id>')
def delete_member(id):
    session2 = Session2()
    post = session2.query(NameDB).get(id)

    session2.delete(post)
    session2.commit()
    session2.close()
    return redirect('/member')

# main
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)