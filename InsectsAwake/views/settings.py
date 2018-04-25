#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/03
# @File    : settings.py
# @Desc    : ""

import json
from flask import Blueprint, redirect, url_for, render_template, request, jsonify
from bson import ObjectId
from InsectsAwake.views.lib.mongo_db import db_management, connectiondb, db_name_conf
from InsectsAwake.views.authenticate import login_check

settings = Blueprint('settings', __name__)
config_db = db_name_conf()['config_db']


@settings.route('/scanner-setting')
@login_check
def scanner_settings():
    return redirect(url_for('dashboard.view_dashboard'))


@settings.route('/dev-tools', methods=['POST', 'GET'])
@login_check
def dev_tools():
    if request.method == 'POST':
        collections_name = request.form.get('collections_name')
        db_command = request.form.get('db_command')
        object_id = request.form.get('object_id')
        result_json = {}
        print collections_name, db_command, object_id

        # 单条查询
        if int(db_command) == 1:
            result = connectiondb(collections_name).find_one()
            result_json = {
                'result': str(result)
            }

        # 批量查询
        elif int(db_command) == 2:
            result = []
            if not object_id == "":
                try:
                    result_cursor = connectiondb(collections_name).find(object_id)
                    for i in result_cursor:
                        result.append(i)
                    result_json = {
                        'result': str(result)
                    }
                    print(result_json)
                except Exception as e:
                    print(e)

            # 返回全部数据
            else:
                try:
                    result_cursor = connectiondb(collections_name).find()
                    for i in result_cursor:
                        result.append(i)
                    print(result)
                    result_json = {
                        'result': str(result)
                    }
                    print(result_json)
                except Exception as e:
                    print(e)

        # 删除集合数据
        elif int(db_command) == 3:
            if not object_id == "":
                print collections_name, object_id
                try:
                    connectiondb(collections_name).delete_one({'_id': ObjectId(object_id)})
                    result_json = {
                        'result': "删除" + str(collections_name) + " 成功!"
                    }
                except Exception as e:
                    print(e)
            else:
                try:
                    connectiondb(collections_name).drop()
                    result_json = {
                        'result': "删除" + str(collections_name) + " 成功!"
                    }
                    print(result_json)
                except Exception as e:
                    print(e)

        return jsonify(result_json)
    config_info = connectiondb(config_db).find_one()
    collections_names = db_management('collection_names')
    return render_template('dev-tools.html', collections_names=collections_names, config_info=config_info)


@settings.route('/config-change', methods=['POST'])
@login_check
def configuration_change():
    # 端口扫描设置
    if request.form.get('source') == 'port_scan':
        scan_port = request.form.get('scan_port')
        port_thread = request.form.get('port_thread')
        update_doc = {
            'port_list': scan_port,
            'port_thread': port_thread,
        }
        connectiondb(config_db).update({'config_name': {'$regex': '.*'}}, {"$set": update_doc})
        return jsonify({'data': 'success'})

    # 漏洞扫描设置
    elif request.form.get('source') == 'scanner_config':
        scanner_time = request.form.get('scanner_time')
        scanner_thread = request.form.get('scanner_thread')
        update_doc = {
            'scanner_time': scanner_time,
            'scanner_thread': scanner_thread,
        }
        print(update_doc)
        connectiondb(config_db).update_one({'config_name': {'$regex': '.*'}}, {"$set": update_doc})
        return jsonify({'data': 'success'})

    elif request.form.get('source') == 'subdomain_scan':
        subdomain_dict = request.form.get('subdomain_dict').split('\n', -1)
        update_doc = {
            'subdomain': subdomain_dict,
        }
        print(update_doc)
        connectiondb(config_db).update_one({'config_name': {'$regex': '.*'}}, {"$set": update_doc})
        return jsonify({'data': 'success'})


@settings.route('/setting', methods=['POST', 'GET'])
@login_check
def setting_view():
    config_info = connectiondb(config_db).find_one()
    config_json = {
        "subdomain": '\n'.join(config_info['subdomain']),
    }
    collections_names = db_management('collection_names')
    return render_template('setting.html', collections_names=collections_names,
                           config_info=config_info, config_json=config_json)