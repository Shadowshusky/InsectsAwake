#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/03
# @File    : task_management.py
# @Desc    : ""

import time
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from bson import ObjectId
from lib.mongo_db import connectiondb, db_name_conf
from InsectsAwake.views.authenticate import login_check

task_management = Blueprint('task_management', __name__)
tasks_db = db_name_conf()['tasks_db']
asset_db = db_name_conf()['asset_db']
server_db = db_name_conf()['server_db']
subdomain_db = db_name_conf()['subdomain_db']


@task_management.route('/task-management')
@login_check
def tasks_list():
    # 删除任务
    if request.args.get('trash'):
        task_id = request.args.get('trash')
        connectiondb('test_tasks').delete_one({'_id': ObjectId(task_id)})
        return redirect(url_for('task_management.tasks_list'))

    # 任务重扫
    elif request.args.get('refresh'):
        task_id = request.args.get('refresh')
        connectiondb('test_tasks').update_one({'_id': ObjectId(task_id)}, {'$set': {'task_status': 'Preparation'}})
        return redirect(url_for('task_management.tasks_list'))

    # 任务编辑
    elif request.args.get('edit'):
        task_id = request.args.get('edit')
        task_edit_data = connectiondb(tasks_db).find_one({'_id': ObjectId(task_id)})
        task_edit_data_json = {
            'task_name': task_edit_data['task_name'],
            'scan_target_list': '\n'.join(task_edit_data['scan_target_list']),
        }
        return jsonify(task_edit_data_json)

    # 默认返回任务列表
    task_data = connectiondb('test_tasks').find().sort('end_date', -1)
    return render_template('task-management.html', task_data=task_data)


# 任务编辑
@task_management.route('/task-edit', methods=['POST', 'GET'])
@login_check
def tasks_edit():
    task_name = request.form.get('task_name')
    task_plan = request.form.get('plan')
    target_text = request.form.get('target_text').split('\n', -1)
    task_id = request.form.get('task_id')
    update_task_info = connectiondb(tasks_db).update_one(
        {'_id': ObjectId(task_id)},
        {'$set':
             {'task_name': task_name,
              'task_plan': task_plan,
              'scan_target_list': target_text,
              }
         }
    )
    if update_task_info:
        return 'success'


# 创建任务UI
@task_management.route('/create-tasks', methods=['POST', 'GET'])
@login_check
def create_tasks():
    plugin = connectiondb('test_plugin_info').find()
    return render_template('create-tasks.html', plugin=plugin)


# 新建任务
@task_management.route('/add-task', methods=['POST'])
@login_check
def add_task():
    # 从资产库过来 新建任务
    if request.form.get('source') == 'asset':
        asset_id = request.form.get('target_text').replace('\r', '').split('\n', -1)[0]
        scan_target_text = connectiondb(asset_db).find_one({'_id': ObjectId(asset_id)})['asset_text']
        task_data = {
            "task_name": request.form.get('taskname'),
            "task_plan": request.form.get('plan'),
            "scan_target_list": scan_target_text,
            "plugin_id": request.form.get('plugin_text').split(',', -1),
            "start_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "end_date": "-",
            "task_status": "Preparation"
        }
        if task_data:
            db_insert = connectiondb(tasks_db).insert_one(task_data).inserted_id
            if db_insert:
                return 'success'
        else:
            return 'error'

    # 从服务库中创建任务
    elif request.form.get('source') == 'server':
        server_id = request.form.get('target_text').split(',', -1)
        target_list = []
        for i in server_id:
            print(i)
            try:
                server_result = connectiondb(server_db).find_one({'_id': ObjectId(i)})
                target_list.append(server_result['host'] + ':' + str(server_result['port']))
            except Exception as e:
                print(e)
        # print(target_list)
        task_data = {
            "task_name": request.form.get('taskname'),
            "task_plan": request.form.get('plan'),
            "scan_target_list": target_list,
            "plugin_id": request.form.get('plugin_text').split(',', -1),
            "start_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "end_date": "-",
            "task_status": "Preparation"
        }
        if task_data:
            db_insert = connectiondb(tasks_db).insert_one(task_data).inserted_id
            if db_insert:
                return 'success'
        else:
            return 'error'

    # 从域名库过来建立任务
    elif request.form.get('source') == 'subdomain':
        scan_target_text = []
        domain_id = request.form.get('target_text').replace('\r', '').split('\n', -1)[0]
        for i in connectiondb(subdomain_db).find_one({'domain_id': ObjectId(domain_id)})['result']:
            for subdomain_url in eval(i):
                scan_target_text.append(subdomain_url)
        task_data = {
            "task_name": request.form.get('taskname'),
            "task_plan": request.form.get('plan'),
            "scan_target_list": scan_target_text,
            "plugin_id": request.form.get('plugin_text').split(',', -1),
            "start_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "end_date": "-",
            "task_status": "Preparation"
        }
        if task_data:
            db_insert = connectiondb(tasks_db).insert_one(task_data).inserted_id
            if db_insert:
                return 'success'
        else:
            return 'error'

    # 任务列表界面建立任务
    else:
        task_data = {
            "task_name": request.form.get('taskname'),
            "task_plan": request.form.get('plan'),
            "scan_target_list": request.form.get('target_text').replace('\r', '').split('\n', -1),
            "plugin_id": request.form.get('plugin_text').split(',', -1),
            "start_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "end_date": "-",
            "task_status": "Preparation"
        }
        if task_data:
            db_insert = connectiondb('test_tasks').insert_one(task_data).inserted_id
            if db_insert:
                return 'success'
        else:
            return 'error'


def host_port(server_id):
    scan_target_list = []
    for i in server_id:
        result = connectiondb(server_db).find_one({'_id': ObjectId(i)})
        host = result['host']
        port = result['port']
        scan_target_list.append(host + ':' + str(port))
    return scan_target_list
