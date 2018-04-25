#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/11
# @File    : start.py
# @Desc    : ""

import os
import re
import sys
from bson import ObjectId
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from InsectsAwake.views.lib.mongo_db import connectiondb, db_name_conf

asset_db = db_name_conf()['asset_db']
tasks_db = db_name_conf()['tasks_db']
vul_db = db_name_conf()['vul_db']
plugin_db = db_name_conf()['plugin_db']
config_db = db_name_conf()['config_db']
server_db = db_name_conf()['server_db']


def get_plugin_re(plugin_filename):
    name_pattern = re.compile(r'name\s*=\s*[\'\"\[](.*)[\'\"\]]')
    author_pattern = re.compile(r'author\s*=\s*[\'\"\[](.*)[\'\"\]]')
    vuldate_pattern = re.compile(r'vulDate\s*=\s*[\'\"\[](.*)[\'\"\]]')
    appname_pattern = re.compile(r'appName\s*=\s*[\'\"\[](.*)[\'\"\]]')
    vultype_pattern = re.compile(r'vulType\s*=\s*[\'\"\[](.*)[\'\"\]]')
    appversion_pattern = re.compile(r'appVersion\s*=\s*[\'\"\[](.*)[\'\"\]]')
    plugin_data = open(plugin_filename, 'r').read()
    try:
        plugin_name = name_pattern.findall(plugin_data)
        plugin_author = author_pattern.findall(plugin_data)
        plugin_vuldate = vuldate_pattern.findall(plugin_data)
        plugin_appname = appname_pattern.findall(plugin_data)
        plugin_vultype = vultype_pattern.findall(plugin_data)
        plugin_appversion = appversion_pattern.findall(plugin_data)
        plugin_info = {
            "plugin_filename": plugin_filename,
            "plugin_name": plugin_name[0],
            "plugin_author": plugin_author[0],
            "plugin_vuldate": plugin_vuldate[0],
            "plugin_appname": plugin_appname[0],
            "plugin_vultype": plugin_vultype[0],
            "plugin_appversion": plugin_appversion[0],
        }
        return plugin_info
    except Exception as e:
        print(e)
        pass


def local_install():
    print("[*]插件初始化...")
    connectiondb(plugin_db).drop()
    path = os.getcwd() + '/../InsectsAwake/views/modules/scanner/pocsuite_plugin/'
    files = os.listdir(path)
    for file_name in files:
        plugin_info = get_plugin_re(path + file_name.strip())
        if plugin_info is None:
            pass
        else:
            var = connectiondb(plugin_db).insert_one(plugin_info).inserted_id
    print("[*]插件初始化完成!")
    print("[*]当前插件数量：", connectiondb(plugin_db).count())


if __name__ == "__main__":
    local_install()
    connectiondb(config_db).drop()
    config_data = {
        'port_thread': 50,
        'scanner_thread': 80,
        'scanner_time': 60,
        'config_name': 'test',
        'port_list': [20, 21, 22, 23, 80, 81, 443, 445, 544, 873, 1080, 1433, 1434, 1521, 2100, 3306, 3389, 4440, 5671,
                      5672, 5900, 5984, 6379, 7001, 8080, 8081, 8089, 8888, 9090, 9200, 11211, 15672, 27017, 50070],
        'subdomain': ''
    }
    db_insert = connectiondb(config_db).insert_one(config_data).inserted_id
