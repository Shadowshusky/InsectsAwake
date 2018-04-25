#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/23
# @File    : InsectsAwake.py
# @Desc    : ""

import threading
from flask import Flask
from InsectsAwake.app import app
from instance import config
from InsectsAwake.views.modules.scanner.pocsuite_scanner import scanner_loop_execute
from InsectsAwake.views.modules.subdomain.subdomain import subdomain_loop_execute
from InsectsAwake.views.lib.mongo_db import connectiondb, db_name_conf
from InsectsAwake.views.modules.discovery.port_scanner import MultiProcess
from apscheduler.schedulers.blocking import BlockingScheduler

ProductionConfig = config.ProductionConfig
flask_app = Flask(__name__)
flask_app.config.from_object(ProductionConfig)


def scanner():
    config_db = db_name_conf()['config_db']
    scanner_time = int(connectiondb(config_db).find_one()['scanner_time'])
    print('Scanner is start...')
    scanner_loop_execute(scanner_time)


def manage():
    app.run(host=flask_app.config.get('WEB_HOST'), port=flask_app.config.get('WEB_PORT'))


def discovery():
    print('Discovery is start...')
    scheduler = BlockingScheduler()
    try:
        scheduler.add_job(MultiProcess().start_port_scan, 'cron', day='1-31', hour=14, minute=47)
        scheduler.start()
    except Exception as e:
        print(e)


def subdomain():
    scanner_time = 30
    print('Subdomain is start...')
    subdomain_loop_execute(scanner_time)


if __name__ == "__main__":
    t1 = threading.Thread(target=scanner, args=())
    t2 = threading.Thread(target=manage, args=())
    t3 = threading.Thread(target=subdomain, args=())
    t4 = threading.Thread(target=discovery, args=())
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
