#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/20
# @File    : weak_passwd_test.py
# @Desc    : ""

import time
import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, send_from_directory
from bson import ObjectId
from lib.mongo_db import connectiondb, db_name_conf
from InsectsAwake.views.authenticate import login_check

weak_passwd_test = Blueprint('weak_passwd_test', __name__)
domain_db = db_name_conf()['domain_db']
plugin_db = db_name_conf()['plugin_db']
subdomain_db = db_name_conf()['subdomain_db']
weekpasswd_db = db_name_conf()['weekpasswd_db']


@weak_passwd_test.route('/week-passwd-test', methods=['POST', 'GET'])
@login_check
def task_view():
    if request.method == 'GET':
        # 任务 删
        if request.args.get('delete'):
            task_id = request.args.get('delete')
            connectiondb(weekpasswd_db).delete_one({'_id': ObjectId(task_id)})
            return redirect(url_for('weak_passwd_test.task_view'))

        # 结果下载
        elif request.args.get('download'):
            domain_id = request.args.get('download')
            try:
                file_name = connectiondb(domain_db).find_one({'_id': ObjectId(domain_id)})['domain_text'][0]
                file_path = os.getcwd() + '/InsectsAwake/static/download/'
                os.remove(file_path + file_name)
                for result in connectiondb(subdomain_db).find({'domain_id': ObjectId(domain_id)}):
                    subdomain = eval(result['result']).keys()[0]
                    with open(file_path + file_name, "a") as download_subdomain:
                        download_subdomain.write(subdomain + "\n")
                sub_response = make_response(send_from_directory(file_path, file_name, as_attachment=True))
                sub_response.headers["Content-Disposition"] = "attachment; filename=" + file_name
                return sub_response
            except Exception as e:
                print(e)
        else:
            week_passwd_task = connectiondb(weekpasswd_db).find()
            return render_template('week-passwd-test.html', week_passwd_task=week_passwd_task)

    # 撞库任务 增
    elif request.method == 'POST':
        task_data = {
            "task_name": request.form.get('task_name'),
            "target": request.form.get('target'),
            "post_data": request.form.get('post_data'),
            "username": request.form.get('username'),
            "password": request.form.get('password'),
            "success_data": request.form.get('success_data'),
            "error_data": request.form.get('error_data'),
            "status": "Preparation",
            "week_passwd_result": "",
            "week_passwd_count": "-",
            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }
        inserted = connectiondb(weekpasswd_db).insert_one(task_data).inserted_id
        if inserted:
            return redirect(url_for('weak_passwd_test.task_view'))
