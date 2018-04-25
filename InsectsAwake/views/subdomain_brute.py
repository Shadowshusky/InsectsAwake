#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/13
# @File    : subdomain_brute.py
# @Desc    : ""

import time
import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, send_from_directory
from bson import ObjectId
from lib.mongo_db import connectiondb, db_name_conf
from InsectsAwake.views.authenticate import login_check

subdomain_brute = Blueprint('subdomain_brute', __name__)
domain_db = db_name_conf()['domain_db']
plugin_db = db_name_conf()['plugin_db']
subdomain_db = db_name_conf()['subdomain_db']


@subdomain_brute.route('/subdomain-brute', methods=['POST', 'GET'])
@login_check
def subdomain_view():
    if request.method == 'GET':
        # 域名任务 删
        if request.args.get('delete'):
            domain_id = request.args.get('delete')
            connectiondb(domain_db).delete_one({'_id': ObjectId(domain_id)})
            connectiondb(subdomain_db).remove({'domain_id': ObjectId(domain_id)})
            return redirect(url_for('subdomain_brute.subdomain_view'))

        # 子域名下载
        elif request.args.get('download'):
            domain_id = request.args.get('download')
            try:
                file_name = connectiondb(domain_db).find_one({'_id': ObjectId(domain_id)})['domain_text'][0]
                file_path = os.getcwd() + '/InsectsAwake/static/download/'
                try:
                    os.remove(file_path + file_name)
                except Exception as e:
                    pass
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
            domain_data = connectiondb(domain_db).find().sort('domain_date', -1)
            plugin_data = connectiondb(plugin_db).find()
            return render_template('subdomain-brute.html', domain_data=domain_data, plugin_data=plugin_data)

    # 主域名库 增
    elif request.method == 'POST':
        domain_name = request.form.get('domain_name')
        domain_text = request.form.get('domain_text').replace('\r', '').split('\n', -1),
        dept_name = request.form.get('dept_name')
        scan_option = request.form.get('scan_option')
        if scan_option == "true":
            scan_option = 'Enable'
        else:
            scan_option = 'Disallow'
        domain_data = {
            'domain_name': domain_name,
            'domain_text': domain_text[0],
            'dept_name': dept_name,
            "domain_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'scan_option': scan_option,
            'scan_status': "Preparation",
        }
        print(domain_data)
        db_insert = connectiondb(domain_db).insert_one(domain_data).inserted_id
        if db_insert:
            pass
            return redirect(url_for('subdomain_brute.subdomain_view'))


@subdomain_brute.route('/subdomain-list', methods=['POST', 'GET'])
@login_check
def subdomain_list():
    sub_result = {}
    result_list = []
    # 从域名扫描任务列表过来 筛选出该任务子域名
    if request.method == "GET":
        if request.args.get('domain'):
            domain_id = request.args.get('domain')
            for result in connectiondb(subdomain_db).find({'domain_id': ObjectId(domain_id)}):
                subdomain = eval(result['result']).keys()[0]
                sub_result['subdomain'] = subdomain
                # 有的域名解析的IP太多 默认只显示三条IP
                sub_result['subdomain_ip'] = '|'.join(eval(result['result'])[subdomain][0:3])
                sub_result['date'] = result['date']
                sub_result['domain_id'] = result['domain_id']
                sub_result['domain'] = result['domain']
                sub_result['domain_name'] = result['domain_name']
                sub_result['_id'] = result['_id']
                result_list.append(sub_result)
                sub_result = {}
            return render_template('subdomain-list.html', result_list=result_list)

        # 删除单个子域名
        elif request.args.get('delete'):
            subdomain_id = request.args.get('delete')
            domain_id = connectiondb(subdomain_db).find_one({'_id': ObjectId(subdomain_id)})['domain_id']
            result = connectiondb(subdomain_db).delete_one({'_id': ObjectId(subdomain_id)})
            if result:
                return redirect(url_for('subdomain_brute.subdomain_list', domain=domain_id))

        # 默认返回全部任务子域名
        else:
            for result in connectiondb(subdomain_db).find():
                subdomain = eval(result['result']).keys()[0]
                sub_result['subdomain'] = subdomain
                # 有的域名解析的IP太多 默认只显示三条IP
                sub_result['subdomain_ip'] = '|'.join(eval(result['result'])[subdomain][0:3])
                sub_result['date'] = result['date']
                sub_result['domain_id'] = result['domain_id']
                sub_result['domain'] = result['domain']
                sub_result['domain_name'] = result['domain_name']
                sub_result['_id'] = result['_id']
                result_list.append(sub_result)
                sub_result = {}
            return render_template('subdomain-list.html', result_list=result_list)
    # 接收POST请求
    else:
        # 删除多选子域名
        if request.form.get('source') == "delete-choice":
            subdomain_id = request.form.get('subdomain_id').split(',', -1)
            try:
                for i in subdomain_id:
                    connectiondb(subdomain_db).remove({'_id': ObjectId(i)})
            except Exception as e:
                print(e)
            return jsonify({'result': 'success'})
