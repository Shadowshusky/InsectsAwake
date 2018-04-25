#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/08
# @File    : port_scanner.py
# @Desc    : ""

import nmap
import multiprocessing
from datetime import datetime
from urlparse import urlparse
from bson import ObjectId
from InsectsAwake.views.lib.mongo_db import db_name_conf, connectiondb

config_db = db_name_conf()['config_db']


def nmap_scanner(target_host):
    target_ports = connectiondb(config_db).find_one()['port_list']
    result_list = []
    port_scanner = nmap.PortScanner()
    try:
        # 从数据库取出的数据要进行转换
        port_scanner.scan(target_host, ','.join('%s' % port for port in target_ports))
        # 遍历存活端口
        for i in port_scanner[target_host].all_tcp():
            if port_scanner[target_host]['tcp'][i]['state'] == 'open':
                # port_server_data = {
                #     'host': 'host:' + target_host,
                #     'port': 'port:' + str(i),
                #     'port_server':  'server:' + port_scanner[target_host]['tcp'][i]['product'],
                #     'banner': port_scanner[target_host]['tcp'][i]['cpe'],
                # }
                port_server_data = {
                    'host': target_host,
                    'port': i,
                    'port_server': port_scanner[target_host]['tcp'][i]['product'],
                    'banner': port_scanner[target_host]['tcp'][i]['cpe'],
                }
                result_list.append(port_server_data)
    except Exception as e:
        print target_host, e
    return result_list


class MultiProcess:
    def __init__(self):
        self.target_list = []
        self.server_db = db_name_conf()['server_db']
        self.asset_db = db_name_conf()['asset_db']
        self.processes_count = int(connectiondb(config_db).find_one()['port_thread'])
        self.asset_id = ''
        self.asset_name = ''

    def scan_pool(self):
        target_list = []
        for target in self.target_list:
            target_list.append(target.strip())
        scanner_pool = multiprocessing.Pool(processes=self.processes_count)
        # 目前只能等待一个资产库资产扫描完毕返回结果 出现意外中断 结果没有办法保存 后期要解决掉
        result = scanner_pool.map(nmap_scanner, target_list)
        scanner_pool.close()
        scanner_pool.join()
        if result:
            # 删除旧数据
            connectiondb(self.server_db).remove({'asset_id': ObjectId(self.asset_id)})
            for scan_result in result:
                for server_data in scan_result:
                    server_data['asset_id'] = self.asset_id
                    server_data['asset_name'] = self.asset_name
                    server_data['scan_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    db_insert = connectiondb(self.server_db).insert_one(server_data).inserted_id
                    if db_insert:
                        print('[*]', self.asset_id, 'The result was saved successfully')

    def start_port_scan(self):
        print("++++++++++  Port Scan Start! ++++++++++")
        for asset_data in connectiondb(self.asset_db).find():
            if asset_data['scan_option'] == 'Enable':
                target_hosts = asset_data['asset_text']
                self.asset_id = asset_data['_id']
                self.asset_name = asset_data['asset_name']
                for target_host in target_hosts:
                    # 处理资产库中 以URL形式存在的资产
                    if 'http://' in target_host or 'https://' in target_host:
                        target_host = urlparse(target_host).netloc.split(':')[0]
                        self.target_list.append(target_host)
                    else:
                        self.target_list = target_hosts
                self.scan_pool()
        print("++++++++++ Port Scan Done! ++++++++++")


if __name__ == '__main__':
    print("++++++++++ Scan Start! ++++++++++")
    start_date = datetime.now()
    start_port_scan = MultiProcess()
    start_port_scan.start_port_scan()
    scan_time = datetime.now() - start_date
    print("++++++++++ Scan Done! ++++++++++", scan_time.total_seconds())


