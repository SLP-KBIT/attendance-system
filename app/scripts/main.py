from flask import Flask, render_template, request, redirect, Response, url_for, render_template_string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Date, User
from datetime import datetime, timedelta
import subprocess
import re
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES

app = Flask(__name__, static_url_path='/attendance')

# SQLiteデータベースに接続
engine1 = create_engine('sqlite:///date.db')
engine2 = create_engine('sqlite:///user.db')

# SQLAlchemyセッションを作成
Session1 = sessionmaker(bind=engine1)
Session2 = sessionmaker(bind=engine2)

# 同じ日付のデータを省く
def compute_day(date, onDays):
    for onDay in onDays:
        if date == onDay:
            return 0
    return 1

# 出席者の学籍番号取得
def attend_number(dates, users):
    numbers = {}
    tmp_number = ""
    tmp_last_name = ""
    tmp_first_name = ""
    tmp_grade = ""
    for user in users:
        flg = False
        if user.last_name == tmp_last_name and user.grade == tmp_grade:
            flg = True
            if tmp_number in numbers:
                numbers[tmp_number] = tmp_last_name + tmp_first_name[0]
        for date in dates:
            if date.number == user.number and flg:
                numbers[user.number] = user.last_name + user.first_name[0]
                break
            elif date.number == user.number:
                numbers[user.number] = user.last_name
                break
        tmp_number = user.number
        tmp_last_name = user.last_name
        tmp_first_name = user.first_name
        tmp_grade = user.grade
    return numbers

# 更新に失敗した時のエラー処理
error = ['',0]
def error_handle(e):
    if e and error[1]:
        error[0] = e
        return ''
    elif error[0] and error[1] == 0:
        error[0] = ''
        return error[0]
    else:
        error[1] = 0
        return error[0]
    
# 学生かどうか判定
def judge_student(entry, memberuid):
    if str(entry['uid']) in memberuid:
        pattern = r"s(\d{2})([a-z])(\d{3})@kagawa-u\.ac\.jp"
        result = re.match(pattern, str(entry['mail']))
        if result:
            number = result.group(1) + result.group(2).upper() + result.group(3)

            year_of_admission = int(result.group(1)) + 2000
            current_date = datetime.now()
            current_year = current_date.year
            if current_date < datetime(current_year, 4, 1):
                current_year -= 1
            year_of_grade = current_year - year_of_admission + 1

            if result.group(2).upper() == "G":
                year_of_grade += 4
            elif result.group(2).upper() == "D":
                year_of_grade += 6

            grade_sample = {1:"B1", 2:"B2", 3:"B3", 4:"B4", 5:"M1", 6:"M2", 7:"D1", 8:"D2", 9:"D3"}

            grade = ""
            if year_of_grade in grade_sample:
                grade = grade_sample[year_of_grade]
            
            return number, grade

    return None, None

@app.route('/attendance', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            subprocess.run('sh /app/scripts/getFile.sh', shell=True, check=True)
        except subprocess.CalledProcessError as e:
            error[1] = 1
            e = error_handle(e)
        return redirect('/attendance')

    session1 = Session1()
    dates = session1.query(Date).order_by(Date.date.desc()).all()
    session1.close()
    
    onDays = []
    for date in dates:
        date = date.date.strftime('%Y-%m-%d')
        if compute_day(date, onDays):
            onDays.append(date)

    errorOut = error_handle(0)
    return render_template('index.html', onDays=onDays, error=errorOut)

# 指定した日付
@app.route('/attendance/date/<currentDate_str>', methods=['GET', 'POST'])
def date(currentDate_str):
    if request.method == 'POST':

        number = request.form.get('number')

        session2 = Session2()
        user = session2.query(User).filter(User.number == number).first()
        session2.close()

        if user == None:
            return redirect(f'/attendance/date/{currentDate_str}')

        currentDate = datetime.strptime(currentDate_str, "%Y-%m-%d")

        new_date = Date(number=number, date=currentDate)

        session1 = Session1()
        session1.add(new_date)
        session1.commit()
        session1.close()

        return redirect(f'/attendance/date/{currentDate_str}')

    currentDate = datetime.strptime(currentDate_str, "%Y-%m-%d")
    session1 = Session1()
    dates = session1.query(Date).order_by(Date.date.desc()).filter(Date.date >= currentDate, Date.date < currentDate+timedelta(days=1)).all()
    session1.close()

    session2 = Session2()
    users = session2.query(User).order_by(User.grade.desc()).order_by(User.furigana).all()
    session2.close()

    numbers = attend_number(dates, users)

    return render_template('date.html', dates=dates, currentDate_str=currentDate_str, users=users, numbers=numbers)

# 指定した学籍番号
@app.route('/attendance/user/<currentNumber>', methods=['GET', 'POST'])
def user(currentNumber):
    if request.method == 'POST':
        furigana = request.form.get('furigana')

        pattern = r'^[ァ-ンー　\s]{1,40}$'
        if re.match(pattern, furigana) or furigana == "":
            session2 = Session2()
            user = session2.query(User).filter(User.number == currentNumber).first()
            user.furigana = furigana
            session2.commit()
            session2.close()

        return redirect(f'/attendance/user/{currentNumber}')
    
    else:
        session1 = Session1()
        session2 = Session2()
        dates = session1.query(Date).order_by(Date.date.desc()).filter(Date.number == currentNumber).all()
        user = session2.query(User).filter(User.number == currentNumber).first()
        session1.close()
        session2.close()
        return render_template('user.html', dates=dates, user=user, currentNumber=currentNumber)

# 指定したDateのid
@app.route('/attendance/delete/<int:id>')
def delete(id):
    from_url = request.referrer
    split_url = from_url.partition('/attendance/')

    session1 = Session1()
    date = session1.query(Date).get(id)
    session1.delete(date)
    session1.commit()
    session1.close()

    return redirect(f'/attendance/{split_url[-1]}')

@app.route('/attendance/member', methods=['GET', 'POST'])
def member():
    if request.method == 'POST':
        # opneldapから取得
        server = Server('miku.eng.kagawa-u.ac.jp', get_info=ALL, port=636, use_ssl=True)
        conn = Connection(server, user='cn=admin,dc=slp,dc=eng,dc=kagawa-u,dc=ac,dc=jp', password='<パスワード>', auto_bind=True)
        conn.search('cn=slp,ou=groups,dc=slp,dc=eng,dc=kagawa-u,dc=ac,dc=jp', '(cn=slp)', attributes=['memberuid'], paged_size=None, search_scope=SUBTREE)
        memberuid = conn.entries[0]['memberuid']
        conn.search('ou=members,dc=slp,dc=eng,dc=kagawa-u,dc=ac,dc=jp', '(objectclass=person)', attributes=['uid', 'mail', 'sn', 'givenName'], paged_size=None, search_scope=SUBTREE)
        
        session2 = Session2()

        # DBへの追加・更新
        for entry in sorted(conn.entries):
            number, grade = judge_student(entry, memberuid)
            if number == None:
                continue
            
            uid = str(entry['uid'])
            first_name = str(entry['givenName'])
            last_name = str(entry['sn'])
            user = session2.query(User).filter(User.uid == uid).first()
            if user:
                user.uid = uid
                user.number = number
                user.first_name = first_name
                user.last_name = last_name
                user.grade = grade
            else :
                new_user = User(uid=uid, number=number, first_name=first_name, last_name=last_name, grade=grade, furigana="")
                session2.add(new_user)

            session2.commit()

        # DBへの削除
        users = session2.query(User).all()
        for user in users:
            if user.uid in memberuid:
                continue
            else:
                session2.delete(user)
                session2.commit()

        session2.close()
        return redirect('/attendance/member')

    else:
        session2 = Session2()
        users = session2.query(User).order_by(User.grade.desc()).order_by(User.number).all()
        session2.close()
        return render_template('member.html', users=users)

@app.route('/attendance/other', methods=['GET', 'POST'])
def other():
    other_date = request.form.get('other')
    return redirect(f'/attendance/date/{other_date}')

# main
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)