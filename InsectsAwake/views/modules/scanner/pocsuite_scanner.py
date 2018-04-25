#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/03
# @File    : pocsuite_scanner.py
# @Desc    : ""

import sched
import time
import datetime
from pocsuite.api.cannon import Cannon
from bson.objectid import ObjectId
import threading
from InsectsAwake.views.lib.mongo_db import connectiondb, db_name_conf

schedule = sched.scheduler(time.time, time.sleep)
config_db = db_name_conf()['config_db']
tasks_db = db_name_conf()['tasks_db']
vul_db = db_name_conf()['vul_db']
plugin_db = db_name_conf()['plugin_db']
scanner_thread = int(connectiondb(config_db).find_one()['scanner_thread'])


class PocsuiteScan:
    def __init__(self, inc_time):
        self.inc_time = inc_time
        self.target_list = ''
        self.target = ''
        self.plugin_list = ''
        self.task_name = ''
        self.task_id = ''
        self.task_status = ''
        self.task_plan = ''
        self.poc_name = ''
        self.poc_filename = ''
        self.poc_mode = ''
        self.poc_vultype = ''
        self.plugin_id = ''
        self.plugin_filename = ''

    def verify_poc(self, target):
        self.target = target
        info = {"pocname": self.poc_name,
                "pocstring": open(self.plugin_filename, 'r').read(),
                "mode": self.poc_mode
                }
        invoker = Cannon(self.target.strip(), info)
        result = invoker.run()
        if result[-3][0] == 1:
            vul_result = {
                "target": result[0],
                "task_name": self.task_name,
                "task_id": self.task_id,
                "poc_name": result[1],
                "appname": result[3],
                "poc_vultype": self.poc_vultype,
                "vulversion": result[4],
                "scan_date": result[-2],
                "scan_result": result[-1],
                "plugin_id": self.plugin_id
            }
            db_insert = connectiondb(vul_db).insert_one(vul_result).inserted_id
            if db_insert:
                pass

    def start_scan(self):
        connectiondb(tasks_db).update_one({'_id': ObjectId(self.task_id)}, {'$set': {'task_status': 'Running'}})
        for self.plugin_id in self.plugin_list:
            threads = []
            try:
                plugin_info = connectiondb(plugin_db).find_one({'_id': ObjectId(self.plugin_id)})
                self.plugin_filename = plugin_info['plugin_filename'].encode("UTF-8")
                self.poc_name = plugin_info['plugin_name'].encode("UTF-8")
                self.poc_vultype = plugin_info['plugin_vultype'].encode("UTF-8")
                self.poc_mode = 'verify'
                for i in self.target_list:
                    t = threading.Thread(target=self.verify_poc, args=(i,))
                    threads.append(t)
                for t in threads:
                    t.start()
                    while True:
                        if len(threading.enumerate()) < scanner_thread:
                            break
            except Exception as e:
                print(e)
        connectiondb(tasks_db).update_one({'_id': ObjectId(self.task_id)}, {'$set': {'task_status': '扫描完成',
                                                                                    'end_date': time.strftime(
                                                                                        "%Y-%m-%d %H:%M:%S",
                                                                                        time.localtime())
                                                                                    }})

    def periodic_tasks(self):
        schedule.enter(self.inc_time, 1, self.periodic_tasks, ())
        # Timer(5, periodic_tasks, ()).start()
        for task_info in connectiondb(tasks_db).find():
            self.target_list = task_info['scan_target_list']
            self.plugin_list = task_info['plugin_id']
            self.task_name = task_info['task_name']
            self.task_status = task_info['task_status']
            self.task_plan = int(task_info['task_plan'])
            self.task_id = task_info['_id']
            end_date = task_info['end_date']
            # Single task execution immediately
            if self.task_plan == 0 and "Preparation" in self.task_status:
                print("Temporary plan start...", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                self.start_scan()
            # 日扫描计划开始
            if self.task_plan == 1:
                if "Preparation" in self.task_status:
                    print("Day plan start......", self.task_name)
                    # The first scan has no end time, start the task directly
                    self.start_scan()
                elif "Running" in self.task_status:
                    pass
                else:
                    start_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                    plan_time = (datetime.datetime.now() - start_date).total_seconds()
                    if plan_time > 60 * 60 * 24:
                        self.start_scan()
                    else:
                        pass
            # 周扫描计划
            elif self.task_plan == 7:
                if "Preparation" in self.task_status:
                    print("Weekly plan start...", self.task_name)
                    self.start_scan()
                elif "Running" in self.task_status:
                    pass
                else:
                    start_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                    plan_time = (datetime.datetime.now() - start_date).total_seconds()
                    if plan_time > 60 * 60 * 24 * 7:
                        self.start_scan()
                    else:
                        pass
            # 月扫描计划
            elif self.task_plan == 30:
                if "Preparation" in self.task_status:
                    print("Month plan start...", self.task_name)
                    self.start_scan()
                elif "Running" in self.task_status:
                    pass
                else:
                    start_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                    plan_time = (datetime.datetime.now() - start_date).total_seconds()
                    if plan_time > 60 * 60 * 24 * 30:
                        self.start_scan()
                    else:
                        pass


def scanner_loop_execute(inc):
    start = PocsuiteScan(inc)
    schedule.enter(inc, 0, start.periodic_tasks, ())
    schedule.run()

