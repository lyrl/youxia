#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json

import time

import datetime

import youxia_connector_compoent as connector_compoent
import youxia_compoent as youxia_repository
import youxia_redis_compoent as yxredis
import util
import sys

logger = util.get_logger("YouxiaCrawler")

GENERATE_SIZE = 10000 # 每次自动生成的id数量
IDS_INIT_START = 1000000000


class YouxiaCrawler(object):
    def __init__(self, sqlite_file, redis_host='localhost', create_table=False):
        self.sqlite_file = sqlite_file
        self.connector = connector_compoent.YouxiaConnectorCompoentImpl()
        self.repo = youxia_repository.YouxiaCompoentImpl(self.sqlite_file, create_table)
        self.redis = yxredis.YouxiaRedisImpl(redis_host)

    def run(self, run_as):
        while True:
            if run_as == 'crawler':
                logger.debug("[爬虫进程] - 初始化成功!")
                self.youxia_new_user_crawler()
            elif run_as == 'updater':
                logger.debug("[位置更新] - 初始化成功!")
                self.rencently_active_user_location_updater()
            else:
                logger.error("[主进程] - run_as 参数错误!")
                sys.exit()

    def youxia_new_user_crawler(self):

        tm = time.time()

        # active & queue 列表中数据为空
        if self.redis.queue_size() == 0 and self.redis.active_size() == 0:
            top_id = self.repo.get_top_user_id()

            if top_id == 0:
                top_id = IDS_INIT_START
                logger.debug("[爬虫进程] - 程序第一次启动将自动从%s开始生成id!" % IDS_INIT_START)
            self.generate_ids_put_in_redis(top_id, GENERATE_SIZE)

        # 将active列表中的数据移到queue中重新进行抓取
        if self.redis.active_size() > 0:
            logger.debug("[爬虫进程] - 检测到上次程序异常退出，将优先执行未处理的id!")
            self.redis.move_active_to_queue()

        logger.debug("[爬虫进程] - 正在进行抓取!")
        while self.redis.queue_size() != 0:
            id = self.redis.fetch_from_queue()
            self.redis.put_in_active_list(id)
            self.fetch_and_save_to_db(id)

            self.redis.register('crawler:' + str(tm), 5)

    def rencently_active_user_location_updater(self):

        tm = time.time()

        # 最近活动的数据
        if self.redis.recently_size() == 0 and self.redis.recently_active_size() == 0:
            recent_active_user_list = self.repo.get_recent_active_user()
            logger.debug("[爬虫进程] - 近一天活动的用户 %s " % (recent_active_user_list.count()))

            if recent_active_user_list.count():
                for i in recent_active_user_list:
                    self.redis.put_in_recently_list(i.user.uid)

        if self.redis.recently_active_size():
            logger.debug("[爬虫进程] - 将上次抓取未完成的记录 %s 移动到recently" % self.redis.recently_active_size())
            self.redis.move_recently_active_to_recently_list()

        if self.redis.recently_5_min_size():
            logger.debug("[爬虫进程] - 最近5分钟更新用户 %s 条，将优先抓取 " % (self.redis.recently_5_min_size()))
            while self.redis.recently_5_min_size():
                id = self.redis.fetch_from_recently_5_min_list()
                self.redis.put_in_recently_list(id, True)

        logger.debug("[爬虫进程] - 开始更新 %s 条 !" % self.redis.recently_size())
        while self.redis.recently_size():
            id = self.redis.fetch_from_recently_list()
            self.redis.put_in_recently_active_list(id)

            user = self.repo.get_user_by_id(id)

            self.fetch_and_save_location_to_db(id, user)
            self.redis.register('updater:'+str(tm), 5)

    def fetch_and_save_to_db(self, uid):
        #用户信息
        user_info = self.fetch_and_save_user_info_to_db(uid)

        #位置信息
        self.fetch_and_save_location_to_db(uid, user_info)

        #设备信息
        self.fetch_and_save_device_info_to_db(uid, user_info)

        self.redis.remove_from_active_list(uid)

    def fetch_and_save_device_info_to_db(self, uid, user_info):
        try:
            device_info_json = self.connector.get_device_info(user_info.imei)
            json.loads(device_info_json)
        except Exception:
            return

        if self.repo.get_device_info_by_user_id(uid):
            self.repo.update_device_info(device_info_json, uid)
        else:
            self.repo.save_device_info(device_info_json, uid)

    def fetch_and_save_location_to_db(self, uid, user_info, caller='updater'):
        try:
            location_info_json = self.connector.get_location(user_info.imei)
            json.loads(location_info_json)
        except Exception:
            return

        if self.repo.count_location_by_user_id(user_info.uid) > 0:
            location = self.repo.update_location(location_info_json, uid)
        else:
            location = self.repo.save_location(location_info_json, uid)

        if caller == 'updater':
            if location.speed > 0:
                last_time = location.time
                now = datetime.datetime.now()
                min5 = datetime.timedelta(minutes=5)
                min5_ago = now - min5

                if min5_ago <= last_time <= now:
                    self.redis.put_in_recently_5_min_list(location.user.uid)

            self.redis.remove_from_recently_active_list(uid)

    def fetch_and_save_user_info_to_db(self, uid):
        try:
            user_info_json = self.connector.get_user_info(uid)
            json.loads(user_info_json)
        except Exception:
            return

        user_info_json_dict = json.loads(user_info_json)
        try:
            user_info_json_dict['IMEI']
        except Exception:
            self.redis.remove_from_active_list(uid)
            return

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



