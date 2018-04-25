#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/02
# @File    : config.py
# @Desc    : ""

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    WEB_USER = 'admin'
    WEB_PASSWORD = 'passwd'
    POCSUITE_PATH = basedir + '/../InsectsAwake/views/modules/scanner/pocsuite_plugin/'
    WEB_HOST = '127.0.0.1'
    WEB_PORT = 5000


class ProductionConfig(Config):
    DB_HOST = '127.0.0.1'
    DB_PORT = 27017
    DB_USERNAME = 'testuser'
    DB_PASSWORD = 'testpwd'
    DB_NAME = 'InsectsAwake'

    PLUGIN_DB = 'test_plugin_info'
    TASKS_DB = 'test_tasks'
    VULNERABILITY_DB = 'test_vuldb'
    ASSET_DB = 'test_asset'
    CONFIG_DB = 'test_config'
    SERVER_DB = 'test_server'
    SUBDOMAIN_DB = 'test_subdomain'
    DOMAIN_DB = 'test_domain'
    WEEKPASSWD_DB = 'test_weekpasswd'
