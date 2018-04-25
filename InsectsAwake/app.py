#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/02
# @File    : app.py
# @Desc    : ""

from flask import Flask, render_template
from InsectsAwake.views.index import index
from InsectsAwake.views.dashboard import dashboard
from InsectsAwake.views.task_management import task_management
from InsectsAwake.views.vulnerability_management import vulnerability_management
from InsectsAwake.views.asset_management import asset_management
from InsectsAwake.views.plugin_management import plugin_management
from InsectsAwake.views.authenticate import authenticate
from InsectsAwake.views.settings import settings
from InsectsAwake.views.sql_injection import sql_injection
from InsectsAwake.views.subdomain_brute import subdomain_brute
from InsectsAwake.views.weak_passwd_test import weak_passwd_test
from InsectsAwake.views.authenticate import login_check
from string import digits, ascii_lowercase
from random import sample


app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join(sample(digits + ascii_lowercase, 10))

app.register_blueprint(index)
app.register_blueprint(dashboard)
app.register_blueprint(task_management)
app.register_blueprint(vulnerability_management)
app.register_blueprint(asset_management)
app.register_blueprint(plugin_management)
app.register_blueprint(authenticate)
app.register_blueprint(settings)
app.register_blueprint(sql_injection)
app.register_blueprint(subdomain_brute)
app.register_blueprint(weak_passwd_test)


@app.errorhandler(404)
@login_check
def page_not_fount(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
@login_check
def internal_server_error(e):
    return render_template('500.html'), 500
