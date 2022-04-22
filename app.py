import os
from flask import Flask, render_template, request, session, redirect
import sqlite3

app = Flask(__name__)

global user

app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/', methods=['GET', "POST"])  # 路由默认接收请求方式位POST，然而登录所需要请求都有，所以要特别声明。
@app.route('/login', methods=['GET', "POST"])
def login():

    if request.method == "GET":
        return render_template('login.html')

    user = request.form.get('username')
    pwd = request.form.get('password')

    user_dict = {}
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select * from user"
    data = cur.execute(sql)
    for item in data:
        user_dict[item[0]] = item [1]
    cur.close()
    con.close()

    #  此处暂时有bug，必须登录一次admin账户才能使其他账户生效(已解决)
    if user_dict.get(user, 0) and user_dict.get(user) == pwd:  # 这里可以根据数据库里的用户和密码来判断，因为是最简单的登录界面，数据库学的不是很好，所有没用。
        session['user_info'] = user
        return redirect('/index')
    else:
        return render_template('login.html', msg='用户名或密码输入错误')

@app.before_request
def before_request():
    # user_info变成session中的健，可以随时访问
    user_info = session.get('user_info')
    print(user_info)
    print(request.path)
    if request.path == '/' or request.path == '/login' or request.path == '/static/assets/css/Login.css':
        pass
    # 判断用户是否在数据库中
    elif user_info:
        pass
    else:
        return redirect('/login')


@app.route('/index')
def home():
    return render_template("index.html")

@app.route('/movie')
def movie():
    datalist = []
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select * from movieTop250"
    data = cur.execute(sql)
    for item in data:
        datalist.append(item)

    cur.close()
    con.close()

    return render_template("movie.html",movies = datalist)

@app.route('/score')
def score():
    score = []   #评分
    num = []     #每个评分所统计出的电影数量
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select score,count(score) from movieTop250 group by score"
    data = cur.execute(sql)
    for item in data:
        score.append(str(item[0]))
        num.append(item[1])

    cur.close()
    con.close()
    return render_template("score.html",score = score,num = num)

@app.route('/word')
def word():
    return render_template("word.html")

@app.route('/team')
def team():
    return render_template("team.html")

# 添加了退出登录功能
@app.route('/logout')
def logout():
    del session['user_info']
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)     #debug=True 开启debug调试