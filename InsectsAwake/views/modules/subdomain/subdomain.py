#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 2018/04/12
# @File    : subdomain_brute.py
# @Desc    : ""

import sched
import time
import dns.resolver
import multiprocessing
from datetime import datetime
from string import digits, ascii_lowercase
from random import sample
from InsectsAwake.views.lib.mongo_db import connectiondb, db_name_conf
from bson import ObjectId

domain_db = db_name_conf()['domain_db']
config_db = db_name_conf()['config_db']
subdomain_db = db_name_conf()['subdomain_db']
schedule = sched.scheduler(time.time, time.sleep)


class DomainsBrute:
    def __init__(self, target_domain, subdomain_dict, domain_id, domain_name):
        self.target_domain = target_domain
        self.subdomain_dict = subdomain_dict
        self.domain_id = domain_id
        self.domain_name = domain_name
        self.domain_list = []
        self.result = {}
        self.subdomain_db_name = subdomain_db
        self.random_subdomain = ''.join(sample(digits + ascii_lowercase, 10)) + '.' + self.target_domain

    # check wildcard DNS record
    def resolver_check(self):
        try:
            ha_resolver_domain(self.random_subdomain)
            if ha_resolver_domain(self.random_subdomain)[self.random_subdomain]:
                return ha_resolver_domain(self.random_subdomain)[self.random_subdomain]
            else:
                return False
        except Exception as e:
            return False

    def handle_domain(self):
        for sub_domain in self.subdomain_dict:
            self.domain_list.append(sub_domain.strip() + '.' + self.target_domain)

    # handle wildcard DNS record
    def handle_result(self):
        result_wildcard = {}
        for result in self.result:
            # 这里为了处理空字典
            if result:
                if self.resolver_check():
                    for domain in result.keys():
                        for record in result[domain]:
                            if record not in self.resolver_check():
                                result_wildcard[domain] = result[domain]
                                # 字典有‘.’不能直接存储到mongodb中 这里转换一下类型 后期调用用eval转换成字典
                                self.save_db(str(result_wildcard))
                                result_wildcard = {}
                else:
                    self.save_db(str(result))

    def save_db(self, result):
        data = {
            'domain': self.target_domain,
            'result': result,
            'domain_id': self.domain_id,
            'domain_name': self.domain_name,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(data)
        try:
            inserted = connectiondb(self.subdomain_db_name).insert_one(data).inserted_id
            if inserted:
                print inserted
        except Exception as e:
            print("save_db error", e)

    def run_multi(self):
        self.handle_domain()
        scanner_pool = multiprocessing.Pool(processes=100)
        self.result = scanner_pool.map(ha_resolver_domain, self.domain_list)
        scanner_pool.close()
        scanner_pool.join()
        self.handle_result()


def ha_resolver_domain(domain):
    _result = {}
    record_a = []
    record_cname = []
    try:
        respond = dns.resolver.query(domain.strip())
        for record in respond.response.answer:
            for i in record.items:
                if i.rdtype == dns.rdatatype.from_text('A'):
                    record_a.append(str(i))
                    _result[domain] = record_a
                elif i.rdtype == dns.rdatatype.from_text('CNAME'):
                    record_cname.append(str(i))
                    _result[domain] = record_cname
    except Exception as e:
        pass
    # del record_a
    # del record_cname
    return _result


def start_brute(inc_time):
    schedule.enter(inc_time, 1, start_brute, (inc_time,))
    subdomain_list = connectiondb(config_db).find_one()['subdomain']
    for domain_text in connectiondb(domain_db).find():
        if domain_text['scan_status'] == "Preparation":
            domain_list = domain_text['domain_text']
            domain_id = domain_text['_id']
            domain_name = domain_text['domain_name']
            print("++++++++++ Scan Start! ++++++++++")
            start_date = datetime.now()
            connectiondb(domain_db).update_one({'_id': ObjectId(domain_id)}, {'$set': {'scan_status': 'Running'}})
            for target in domain_list:
                start = DomainsBrute(target, subdomain_list, domain_id, domain_name)
                start.run_multi()
            if domain_text['scan_option'] == "Enable":
                for result in connectiondb(subdomain_db).find({'domain_id': ObjectId(domain_id)}):
                    next_subdomain = eval(result['result']).keys()[0]
                    start = DomainsBrute(next_subdomain, subdomain_list, domain_id, domain_name)
                    start.run_multi()
            connectiondb(domain_db).update_one({'_id': ObjectId(domain_id)}, {'$set': {'scan_status': 'Done'}})
            scan_time = datetime.now() - start_date
            print("++++++++++ Scan Done! ++++++++++", scan_time.total_seconds())


def subdomain_loop_execute(inc,):

    schedule.enter(inc, 0, start_brute, (inc,))
    schedule.run()
