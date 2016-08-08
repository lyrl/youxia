#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json

import time

import datetime

import youxia_connector_compoent as connector_compoent
import youxia_compoent as youxia_repository
import youxia_redis_compoent as yxredis
import youxia_gps_reverse_compoent as gps
import util
import sys

logger = util.get_logger("YouxiaCrawler")

GENERATE_SIZE = 5000 # 每次自动生成的id数量
IDS_INIT_START = 1000000000


class YouxiaCrawler(object):
    def __init__(self, sqlite_file, redis_host='localhost', appkey='', create_table=False):
        self.sqlite_file = sqlite_file
        self.connector = connector_compoent.YouxiaConnectorCompoentImpl()
        self.repo = youxia_repository.YouxiaCompoentImpl(self.sqlite_file, create_table)
        self.redis = yxredis.YouxiaRedisImpl(redis_host)
        self.reverser =  gps.GpsReverseImpl(appkey)

    def run(self, run_as):
        while True:
            if run_as == 'crawler':
                logger.debug("[爬虫进程] - 初始化成功!")
                self.youxia_new_user_crawler()
            elif run_as == 'updater':
                logger.debug("[位置更新] - 初始化成功!")
                self.rencently_active_user_location_updater()
            elif run_as == 'reverser':
                logger.debug("[GPS反查] - 初始化成功!")
                self.gps_reverse()
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

    def gps_reverse(self):
        tm = time.time()



        users = self.repo.find_need_gps_reverse_user()

        logger.debug("[GPS反查] - 有%s用户位置需要反查！" % users.count())

        for i in users:
            location = self.repo.get_last_location(i.uid)

            if location:
                info = self.reverser.send_gps_reverse_query(location.longitude, location.latitude)

                i.country = info['country']
                i.province = info['province']
                i.city = info['city']
                i.district = info['district']
                i.formatted_address = info['formatted_address']

                try:
                    i.save()
                except Exception:
                    logger.debug("[GPS反查] - 用户 %s 保存失败！" % (i.uid))
                logger.debug("[GPS反查] - 用户 %s %s 保存成功！" % (i.uid, ','.join(info)))

    def rencently_active_user_location_updater(self):

        tm = time.time()

        # 最近活动的数据
        if self.redis.recently_size() == 0 and self.redis.recently_active_size() == 0:
            recent_active_user_list = self.repo.get_recent_active_user()
            logger.debug("[爬虫进程] - 近一天活动的用户 %s " % (recent_active_user_list.count()))

            if recent_active_user_list.count():
                for i in recent_active_user_list:
                    self.redis.put_in_recently_list(i.user.uid)
            else: # 如果没有最近一天活动的记录，则更新全部用户信息
                logger.debug("[爬虫进程] - 没有最近一天活动的记录，将更新全部用户信息 ")
                all_user_list = self.repo.find_all()
                for u in all_user_list:
                    self.redis.put_in_recently_list(u.user.uid)

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
            location_info_json_dict_object = json.loads(location_info_json)
        except Exception:
            return

        if self.repo.count_location_by_user_id(user_info.uid) > 0:
            #last_location = self.repo.get_last_location(uid)
            # 数据库控制还是不可行
            #if last_location and self.location_is_same(last_location, location_info_json_dict_object):
            #   self.redis.remove_from_recently_active_list(uid)
            #    return

            location = self.repo.update_location(location_info_json, uid)
        else:
            location = self.repo.save_location(location_info_json, uid)

        if caller == 'updater':
            # 如果速度 > 0 则作为有效数据
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

    def location_is_same(self, last_location, location_info_json_dict_object):
        """
        判断数据库中最后一次位置信息 是否跟最新抓取的位置信息一样
        一样的话就不再保存
        """
        date_time_format = '%Y-%m-%d %H:%M:%S'

        speed_n = location_info_json_dict_object['speed']
        time_n = datetime.datetime.strptime(location_info_json_dict_object['time'], date_time_format)

        if last_location.time == time_n and last_location.speed == speed_n:
            return True

        return False


class YouxiaCrawlerException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message



