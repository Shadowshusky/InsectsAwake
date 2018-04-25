#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/02
# @File    : dashboard.py
# @Desc    : ""

import datetime
import re
from collections import Counter
from flask import Blueprint, render_template
from bson import ObjectId
from lib.mongo_db import connectiondb, db_name_conf
from InsectsAwake.views.authenticate import login_check

dashboard = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

vul_db = db_name_conf()['vul_db']
plugin_db = db_name_conf()['plugin_db']
tasks_db = db_name_conf()['tasks_db']
asset_db = db_name_conf()['asset_db']


@dashboard.route('/dashboard')
@login_check
def view_dashboard():

    # 获取漏洞数 插件数 任务数 资产数
    vul_count = connectiondb(vul_db).count()
    plugin_count = connectiondb(plugin_db).count()
    task_count = connectiondb(tasks_db).count()
    asset_count = 0
    for i in connectiondb(asset_db).find():
        asset_count += len(i['asset_text'])

    # 从漏洞库中统计近七天的漏洞数量
    vul_day_count = []
    vul_date_list = []
    vul_day_count_dict = {}
    now_date = datetime.datetime.now()
    for scan_date in range(6, -1, -1):
        vul_date = (now_date - datetime.timedelta(scan_date)).strftime("%Y-%m-%d")
        vul__day_count = connectiondb(vul_db).find({'scan_date': re.compile(vul_date)}).count()
        vul_day_count.append(vul__day_count)
        vul_date_list.append(vul_date)
    vul_day_count_dict['date'] = vul_date_list
    vul_day_count_dict['count'] = vul_day_count

    # 漏洞类型分布 取漏洞库中排名前十的插件ID
    plugin_count_list = []
    plugin_stats_name = []
    plugin_stats_count = []
    for i in connectiondb(vul_db).find():
        plugin_count_list.append(i['plugin_id'])
    word_counts = Counter(plugin_count_list)
    top_10 = word_counts.most_common(10)
    for i in top_10:
        plugin_name = connectiondb(plugin_db).find_one({'_id': ObjectId(i[0])})['plugin_name']
        plugin_stats_name.append(plugin_name)
        plugin_stats_count.append(i[1])
        # print plugin_name, i[1]

    return render_template('dashboard.html', vul_count=vul_count, plugin_count=plugin_count,
                           task_count=task_count, asset_count=asset_count, vul_day_count_dict=vul_day_count_dict,
                           plugin_stats_count=plugin_stats_count, plugin_stats_name=plugin_stats_name)