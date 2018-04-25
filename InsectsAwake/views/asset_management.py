#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/03
# @File    : asset_management.py
# @Desc    : ""

import time
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from bson import ObjectId
from lib.mongo_db import connectiondb, db_name_conf
from InsectsAwake.views.authenticate import login_check

asset_management = Blueprint('asset_management', __name__)
asset_db = db_name_conf()['asset_db']
plugin_db = db_name_conf()['plugin_db']
server_db = db_name_conf()['server_db']


# 资产库操作
@asset_management.route('/asset-management', methods=['POST', 'GET'])
@login_check
def asset_view():
    if request.method == 'GET':
        # 资产库 删
        if request.args.get('delete'):
            asset_id = request.args.get('delete')
            connectiondb(asset_db).delete_one({'_id': ObjectId(asset_id)})
            return redirect(url_for('asset_management.asset_view'))

        # 资产库 改
        elif request.args.get('edit'):
            asset_id = request.args.get('edit')
            asset_edit_data = connectiondb(asset_db).find_one({'_id': ObjectId(asset_id)})
            asset_edit_data_json = {
                'asset_name': asset_edit_data['asset_name'],
                'admin_name': asset_edit_data['admin_name'],
                'dept_name': asset_edit_data['dept_name'],
                'asset_id': asset_id,
                'asset_text': '\n'.join(asset_edit_data['asset_text']),
            }
            return jsonify(asset_edit_data_json)

        # 默认资产库界面

    # 资产库 增
    elif request.method == 'POST':
        asset_name = request.form.get('asset_name')
        asset_text = request.form.get('asset_text').replace('\r', '').split('\n', -1),
        dept_name = request.form.get('dept_name')
        admin_name = request.form.get('admin_name')
        scan_option = request.form.get('scan_option')
        if scan_option == "true":
            scan_option = 'Enable'
        else:
            scan_option = 'Disallow'
        asset_data = {
            'asset_name': asset_name,
            'asset_text': asset_text[0],
            'dept_name': dept_name,
            'admin_name': admin_name,
            "asset_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'scan_option': scan_option,
        }
        print(asset_data)
        db_insert = connectiondb(asset_db).insert_one(asset_data).inserted_id
        if db_insert:
            return redirect(url_for('asset_management.asset_view'))

    asset_info = connectiondb(asset_db).find()
    plugin_data = connectiondb(plugin_db).find()
    return render_template('asset-management.html', asset_info=asset_info, plugin_data=plugin_data)


# 资产库更新
@asset_management.route('/asset-edit', methods=['POST'])
@login_check
def asset_edit():
    asset_name = request.form.get('asset_name')
    dept_name = request.form.get('dept_name')
    asset_text = request.form.get('asset_text').split('\n', -1)
    admin_name = request.form.get('admin_name')
    asset_id = request.form.get('asset_id')
    scan_option = request.form.get('scan_option')
    if scan_option == "true":
        scan_option = 'Enable'
    else:
        scan_option = 'Disallow'
    # 数据库更新
    update_asset_info = connectiondb(asset_db).update_one(
        {'_id': ObjectId(asset_id)},
        {'$set':
             {'asset_name': asset_name,
              'dept_name': dept_name,
              'asset_text': asset_text,
              'admin_name': admin_name,
              'scan_option': scan_option,
              }
         }
    )
    if update_asset_info:
        return 'success'


@asset_management.route('/asset-search', methods=['GET', 'POST'])
@login_check
def asset_search():
    asset_server = connectiondb(server_db).find().sort('scan_date', -1)
    plugin_data = connectiondb(plugin_db).find()
    return render_template('asset-search.html', asset_server=asset_server, plugin_data=plugin_data)


# 删除多选
@asset_management.route('/asset-delete', methods=['POST'])
@login_check
def asset_delete():
    if request.form.get('source') == 'delete_choice':
        server_id = request.form.get('server_id').split(',', -1)
        try:
            for i in server_id:
                connectiondb(server_db).remove({'_id': ObjectId(i)})
        except Exception as e:
            print(e)
        return jsonify({'result': 'success'})
