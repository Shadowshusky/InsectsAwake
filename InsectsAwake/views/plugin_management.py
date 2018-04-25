#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/03
# @File    : plugin_management.py
# @Desc    : ""

import time
from flask import Blueprint, render_template, request, redirect, url_for, Flask, jsonify
from bson import ObjectId
from lib.mongo_db import connectiondb, db_name_conf
from werkzeug.utils import secure_filename
from InsectsAwake.views.modules.scanner.vulnerability_plugin import get_plugin_re
from instance import config
from InsectsAwake.views.authenticate import login_check

ProductionConfig = config.ProductionConfig

app = Flask(__name__)
app.config.from_object(ProductionConfig)

plugin_management = Blueprint('plugin_management', __name__)
asset_db = db_name_conf()['asset_db']
plugin_db = db_name_conf()['plugin_db']


# 资产库操作
@plugin_management.route('/plugin-management', methods=['POST', 'GET'])
@login_check
def plugin_list():
    if request.method == 'GET':
        if request.args.get('delete'):
            plugin_id = request.args.get('delete')
            connectiondb(plugin_db).delete_one({'_id': ObjectId(plugin_id)})
            return redirect(url_for('plugin_management.plugin_list'))

    # 文件上传接口 新增插件
    elif request.method == 'POST':
        file_path = app.config.get('POCSUITE_PATH')
        file_data = request.files['file']
        plugin_name = request.form.get('plugin_name')
        if file_data:
            file_name = "_" + time.strftime("%y%m%d", time.localtime()) + "_" + secure_filename(file_data.filename)
            save_path = file_path + file_name
            file_data.save(save_path)
            try:
                new_plugin_info = get_plugin_re(save_path)
                db_insert = connectiondb(plugin_db).insert_one(new_plugin_info).inserted_id
                if db_insert:
                    return redirect(url_for('plugin_management.plugin_list'))
            except Exception as e:
                print(e)
                return redirect(url_for('plugin_management.plugin_list'))
    plugin_info_data = connectiondb(plugin_db).find().sort('plugin_vuldate', -1)
    return render_template('plugin-management.html', plugin_info=plugin_info_data)


@plugin_management.route('/plugin-info', methods=['GET'])
@login_check
def plugin_info():
    if request.args.get('plugin_id'):
        plugin_id = request.args.get('plugin_id')
        plugin_info_dict = connectiondb(plugin_db).find_one({'_id': ObjectId(plugin_id)})
        del plugin_info_dict['_id']
        return jsonify(plugin_info_dict)
