import mysql.connector
import string
import random
import hashlib
import json
from flask import render_template, flash, redirect, g, session, abort, request
from app import app
from app.forms import LoginForm, SigupForm, VerCode
from login import fuck_bilibili

def connect_db():
    # 仅用作测试, 不定时DROP一次
    return mysql.connector.connect(host='114.215.137.141', port=3306, user='test', password='123456', database='test')

def md5Password(password, salt0 = '', salt1 = ''):
    dic = string.ascii_letters + string.digits

    if '' == salt0 and '' == salt1:
        salt0 = ''.join(random.sample(dic, 3))
        salt1 = ''.join(random.sample(dic, 7))

    password = salt0 + password
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))

    password = password + salt1
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))

    return md5.hexdigest(), salt0, salt1

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title = 'Home')

@app.route('/sigup', methods=['GET', 'POST'])
def sigup():
    if session.get('bisLogin'):
        flash('You have login in bilibili!')
        return redirect('/go')

    if session.get('isLogin'):
        flash('You have login!')
        form = LoginForm()
        return render_template('blogin.html',
                               title='login in',
                               form=form)

    form = SigupForm()
    if form.validate_on_submit():
        username = form.username.data
        password0 = str(form.password0.data)
        password1 = str(form.password1.data)

        if password0 == password1:
            password, salt0, salt1 = md5Password(password1)
            cur = g.db.cursor()
            cur.execute("INSERT INTO test0 (username, password, salt0, salt1) VALUES ('%s', '%s', '%s', '%s')"
                                  % (username, password, salt0, salt1))
            g.db.commit()
            flash('sigup success')
            return redirect('/login')
        else:
            flash('Bad password!')
    return render_template('sigup.html',
                           title = 'Sign up',
                           form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('bisLogin'):
        flash('You have login in bilibili!')
        return redirect('/go')

    form = LoginForm()
    if session.get('isLogin'):
        flash('You have login!')
        return render_template('blogin.html',
                               title='login in',
                               form=form)

    if form.validate_on_submit():
        username = form.username.data
        _password = str(form.password.data)
        print(_password)

        cur = g.db.cursor()
        cur.execute("SELECT password, salt0, salt1 FROM test0 WHERE username = '%s'" % username)
        try:
            res = cur.fetchall()[0]
            password = res[0]
            print(password)
            salt0 = res[1]
            salt1 = res[2]
            _password = md5Password(_password, salt0, salt1)[0]
            print(_password)
            if password == _password:
                flash('Login success')
                session['isLogin'] = True
                form = LoginForm()
                return render_template('blogin.html',
                                       title = 'login in',
                                       form = form)
            else:
                flash('Bad username or password')
        except:
            flash('Bad username or password')
    return render_template('login.html',
                           title = 'Sign in',
                           form = form)

@app.route('/logout')
def logout():
    session.pop('isLogin', None)
    session.pop('username', None)
    session.pop('password', None)
    session.pop('mySession', None)
    session.pop('bisLogin', None)
    flash('Logout success!')
    form = LoginForm()
    return redirect('login')

@app.route('/blogin', methods=['POST'])
def blogin():
    if not session.get('isLogin'):
        abort(401)
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        session['username'] = username
        session['password'] = password

        return redirect('/go')
    return render_template('blogin.html',
                           title='Sign in',
                           form=form)

@app.route('/go', methods=['GET', 'POST'])
def go():
    if not session.get('isLogin'):
        abort(401)

    try:
        username = session['username']
        password = session['password']
    except:
        flash('Please enter your BILIBILI account and password!')
        form = LoginForm()
        return render_template('blogin.html',
                               title='Sign in',
                               form=form)

    fuck = fuck_bilibili(username, password)

    if session.get('mySession') and 'POST' == request.method:
        fuck.session.cookies.update(json.loads(session['mySession']))

    session['mySession'] = json.dumps(fuck.session.cookies.get_dict())

    if fuck.loadCookies() and fuck.isLogin():
        fuck.getAccountInfo()
        flash(fuck.userData['data']['uname'])
        session['bisLogin'] = True
        return redirect('/index')

    if 'GET' == request.method:
        if not fuck.getVerCode():
            flash('Can not get vercode image!')
            form = LoginForm()
            return render_template('blogin.html',
                                   title='Sign in',
                                   username=username,
                                   form=form)
    form = VerCode()
    if form.is_submitted():
        vercode = form.vercode.data
        fuck.vercode = vercode

        if fuck.login() and fuck.isLogin():
            fuck.saveCookies()
            flash("Welcom %s" % fuck.userData['data']['uname'])
            session['bisLogin'] = True
            return redirect('/index')
        else:
            flash('Can not login success!')
            form = LoginForm()
            return render_template('blogin.html',
                                   title='Sign in',
                                   form=form)

    return render_template('blogin-go.html',
                           title='Sign in',
                           username=username,
                           form=form)

@app.route('/img/<account>')
def img(account):
    filename = "./img/%s.jpg" % account
    with open(filename, 'rb') as f:
        res = app.make_response(f.read())
    res.headers['Content-Type'] = 'image / jpeg'
    return res
