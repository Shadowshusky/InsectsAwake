#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/02
# @File    : index.py
# @Desc    : ""

from flask import Blueprint, redirect, url_for
from InsectsAwake.views.authenticate import login_check

index = Blueprint('index', __name__)


@index.route('/')
@login_check
def view_index():
    return redirect(url_for('dashboard.view_dashboard'))


@index.route('/index')
@login_check
def view_base():
    return redirect(url_for('index.view_index'))
