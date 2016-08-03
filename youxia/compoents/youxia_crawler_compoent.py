#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json
import youxia_connector_compoent as connector_compoent
import youxia_compoent as youxia_repository
import youxia_redis_compoent as yxredis
import util


logger = util.get_logger("YouxiaCrawler")

GENERATE_SIZE = 10000 # 每次自动生成的id数量
IDS_INIT_START = 1000271859


class YouxiaCrawler(object):
    def __init__(self, sqlite_file, redis_host='localhost', create_table=False):
        self.sqlite_file = sqlite_file
        self.connector = connector_compoent.YouxiaConnectorCompoentImpl()
        self.repo = youxia_repository.YouxiaCompoentImpl(self.sqlite_file, create_table)
        self.redis = yxredis.YouxiaRedisImpl(redis_host)

    def run(self):
        logger.debug("[爬虫进程] - 初始化成功!")
        while True:

            # active & queue 列表中数据为空
            if self.redis.queue_size() == 0 and self.redis.active_size() == 0:
                top_id = self.repo.get_top_user_id()

                if top_id == 0:
                    top_id = IDS_INIT_START
                    logger.debug("[爬虫进程] - 程序第一次启动将自动从%s开始生成id!" % IDS_INIT_START)
                self.generate_ids_put_in_redis(top_id, GENERATE_SIZE)

            # 将active列表中的数据移到queue中重新进行抓取
            if self.redis.active_size() > 0:
                logger.debug("[爬虫进程] - 检测到上次程序异常退出，将优先执行未处理的id!" )
                self.redis.move_active_to_queue()

            while self.redis.queue_size() != 0:
                id = self.redis.fetch_from_queue()
                self.redis.put_in_active_list(id)
                self.fetch_and_save_to_db(id)

    def fetch_and_save_to_db(self, uid):
        #用户信息
        user_info = self.fetch_and_save_user_info_to_db(uid)

        #位置信息
        self.fetch_and_save_location_to_db(uid, user_info)

        #设备信息
        self.fetch_and_save_device_info_to_db(uid, user_info)

        self.redis.remove_from_active_list(uid)

    def fetch_and_save_device_info_to_db(self, uid, user_info):
        device_info_json = self.connector.get_device_info(user_info.imei)
        if self.repo.get_device_info_by_user_id(uid):
            self.repo.save_device_info(device_info_json, uid)
        else:
            self.repo.update_device_info(device_info_json, uid)

    def fetch_and_save_location_to_db(self, uid, user_info):
        location_info_json = self.connector.get_location(user_info.imei)

        if self.repo.count_location_by_user_id(user_info.uid) > 0:
            self.repo.update_location(location_info_json, uid)
        else:
            self.repo.save_location(location_info_json, uid)

    def fetch_and_save_user_info_to_db(self, uid):
        user_info_json = self.connector.get_user_info(uid)
        user_info_json_dict = json.loads(user_info_json)
        user_info_json_dict['IMEI']

        user_info = self.repo.get_user_by_id(uid)

        if user_info:
            self.repo.update_user_info(user_info_json, uid)
        else:
            user_info = self.repo.save_user_info(user_info_json, uid)
        return user_info

    def generate_ids_put_in_redis(self, top_id, count=10000):
            for i in xrange(top_id+1, top_id+1+count):
                self.redis.put_in_queue(i)


class YouxiaCrawlerException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message



