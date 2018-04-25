#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/11
# @File    : sql_injection.py
# @Desc    : ""

from flask import Blueprint, render_template
from InsectsAwake.views.authenticate import login_check

sql_injection = Blueprint('sql_injection', __name__)


@sql_injection.route('/sql-injection')
@login_check
def sqlmap_view():
    return render_template('sql-injection.html')
