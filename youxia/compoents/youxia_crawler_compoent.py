#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json

import youxia_connector_compoent as connector_compoent
import youxia_compoent as youxia_repository
import util


logger = util.get_logger("YouxiaCrawler")


class YouxiaCrawler(object):
    def __init__(self, sqlite_file):
        self.sqlite_file = sqlite_file
        self.connector = connector_compoent.YouxiaConnectorCompoentImpl()
        self.repo = youxia_repository.YouxiaCompoentImpl(self.sqlite_file)

    def run(self):
        for i in xrange(1000271859, 1000271859+100000):
            self.fetch_and_save_to_db(i)

    def fetch_and_save_to_db(self, uid):
        try:
            user_info_json = self.connector.get_user_info(uid)
            user_info_json_dict = json.loads(user_info_json)
            user_info_json_dict['IMEI']

            user_info = self.repo.save_user_info(user_info_json, uid)

            location_info_json = self.connector.get_location(user_info.imei)
            self.repo.save_location(location_info_json, uid)

            device_info_json = self.connector.get_device_info(user_info.imei)
            self.repo.save_device_info(device_info_json, uid)
        except KeyError as k:
                logger.error("[爬虫进程] - 无效的用户id %s " % uid)
        except Exception as e:
            return


class YouxiaCrawlerException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message



