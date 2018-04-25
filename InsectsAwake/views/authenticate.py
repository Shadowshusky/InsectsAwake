#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/03
# @File    : authenticate.py
# @Desc    : ""

from flask import Blueprint, render_template, request, redirect, url_for, Flask, session
from instance import config
from functools import wraps

authenticate = Blueprint('authenticate', __name__)

ProductionConfig = config.ProductionConfig
app = Flask(__name__)
app.config.from_object(ProductionConfig)


@authenticate.route('/login', methods=['GET', 'POST'])
def login_view():
    # 登录界面
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == app.config.get('WEB_USER') and password == app.config.get('WEB_PASSWORD'):
            try:
                session['login'] = 'A1akPTQJiz9wi9yo4rDz8ubM1b1'
                return redirect(url_for('index.view_index'))
            except Exception as e:
                print(e)
        else:
            return redirect(url_for('authenticate.login_view'))
    return render_template('login.html')


# 登出
@authenticate.route('/login-out')
def login_out():
    session['login'] = ''
    return redirect(url_for('authenticate.login_view'))


def login_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if "login" in session:
                if session['login'] == 'A1akPTQJiz9wi9yo4rDz8ubM1b1':
                    return f(*args, **kwargs)
                else:
                    return redirect(url_for('authenticate.login_view'))
            else:
                return redirect(url_for('authenticate.login_view'))
        except Exception, e:
            print e
            return redirect(url_for('authenticate.login_view'))
    return wrapper
