#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
from abc import ABCMeta, abstractmethod
import util
import redis


logger = util.get_logger("YouxiaRedis")
QUEUE_REDIS_KEY = 'queue' # 抓取队列中等待抓取的
QUEUE_ACTIVE_REDIS_KEY = 'queue_active' # 抓取激活中，正在抓取的
RECENTLY_REDIS_KEY = 'recently' # 最近活动的用户列表
RECENTLY_ACTIVE_REDIS_KEY = 'recently_active' # 正在更新中的最近活动的用户
RECENTLY_5_MIN_REDIS_KEY = 'recently_5_min' # 5分钟内有活动的

DO_NOT_QUERY_IN_24_HOURS_PREFIX = "DO_NOT_QUERY_IN_24_HOURS_PREFIX:"

class YouxiaRedis:
    __metaclass__ = ABCMeta

    @abstractmethod
    def queue_size(self):
        pass

    @abstractmethod
    def put_in_queue(self, id):
        pass

    @abstractmethod
    def fetch_from_queue(self):
        pass

    @abstractmethod
    def put_in_active_list(self, id):
        pass

    @abstractmethod
    def active_size(self):
        pass

    @abstractmethod
    def fetch_from_active_list(self):
        pass

    @abstractmethod
    def move_active_to_queue(self):
        pass


class YouxiaRedisImpl(YouxiaRedis):
    def put_in_queue(self, id):
        """  将id放置到redis队列
        Args:
            id (str): 用户id
       """
        self.redis.lpush(QUEUE_REDIS_KEY, id)

    def fetch_from_queue(self):
        """ 从队列中取出一个值
        现进先出原则

       Returns:
           int: 用户id
       """
        return self.redis.rpop(QUEUE_REDIS_KEY)

    def queue_size(self):
        """  获取redis中queue列表的长度

       Returns:
           int: redis queue列表长度
       """
        return self.redis.llen(QUEUE_REDIS_KEY)

    def __init__(self, host='localhost', port=6379, db=0):
        """
        Youxia redis访问类
        redis

        Args:
            host (str): redis 服务器地址
            port (str): redis 服务端口 默认6379
            db (str): redis 数据库 默认 0
        """

        try:
            self.redis = redis.StrictRedis(host=host, port=port, db=db)
            self.redis.dbsize()
        except redis.ConnectionError as e:
            logger.error(u"[RedisCompoent] - redis连接失败")
            raise YouxiaRedisException('Redis连接失败: ' + e.message.encode())

    def put_in_active_list(self, id):
        """
        将id放入redis的 active 列表中
        active列表中维护的都是正在进行抓取的用户id

        Args:
            id (int): 用户ID
        """
        self.redis.lpush(QUEUE_ACTIVE_REDIS_KEY, id)

    def active_size(self):
        """
        返回active列表长度

        Args:
            id (int): 用户ID
        Returns:
           int: active列表长度
        """
        return self.redis.llen(QUEUE_ACTIVE_REDIS_KEY)

    def fetch_from_active_list(self):
        """
        从active列表中取出一条数据

        Returns:
           int: 用户ID
        """
        return self.redis.rpop(QUEUE_ACTIVE_REDIS_KEY)

    def move_active_to_queue(self):
        """
        将active列表中所有数据移到queue列表
        """
        while self.active_size() > 0:
            self.redis.rpush(QUEUE_REDIS_KEY, self.fetch_from_active_list())

    def remove_from_active_list(self, uid):
        """
        将用户id为uid的数据从active列表中移除

        Args:
            id (int): 要移除的用户ID
        """
        self.redis.lrem(QUEUE_ACTIVE_REDIS_KEY, 1, uid)

    def put_in_recently_list(self, uid, high_priority=False):
        """
        用用户uid放到最近活动的列表中

        Args:
            uid (int): 用户id
        """
        if high_priority:
            self.redis.rpush(RECENTLY_REDIS_KEY, uid)
        else:
            self.redis.lpush(RECENTLY_REDIS_KEY, uid)

    def fetch_from_recently_list(self):
        """
        从最近活动的列表中取出一个用户id进行抓取

        Returns:
           int: 用户ID
        """
        return self.redis.rpop(RECENTLY_REDIS_KEY)

    def fetch_from_recently_active_list(self):
        """
        从最近活动的列表中取出一个用户id

        """
        return self.redis.rpop(RECENTLY_ACTIVE_REDIS_KEY)

    def put_in_recently_active_list(self, uid):
        """
        用用户uid放到最近活动更新中列表

        Args:
            uid (int): 用户id
        """
        self.redis.lpush(RECENTLY_ACTIVE_REDIS_KEY, uid)

    def remove_from_recently_list(self, uid):
        """
        从最近活动的列表中取出一个用户id进行抓取

        Args:
            uid (int): 用户id
        """
        self.redis.lrem(RECENTLY_REDIS_KEY, 1, uid)

    def remove_from_recently_active_list(self, uid):
        """
        从最近活动抓取列表中取出一个用户id进行抓取

        Args:
            uid (int): 用户id
        """
        self.redis.lrem(RECENTLY_ACTIVE_REDIS_KEY, 1, uid)

    def recently_active_size(self):
        """
        返回recently active列表长度

        Returns:
           int: recently active列表长度
        """
        return self.redis.llen(RECENTLY_ACTIVE_REDIS_KEY)

    def recently_size(self):
        """
        返回recently 列表长度

        Returns:
           int: recently 列表长度
        """
        return self.redis.llen(RECENTLY_REDIS_KEY)

    def move_recently_active_to_recently_list(self):
        """
        将最近活动抓取中列表中的数据移到最近活动列表中准备
        重新抓取
        """

        while self.recently_active_size():
            self.put_in_recently_list(self.fetch_from_recently_active_list())

    def register(self, key, expire):
        self.redis.set(key, key)
        self.redis.expire(key, expire)

    def put_in_recently_5_min_list(self, uid):
        self.redis.lpush(RECENTLY_5_MIN_REDIS_KEY, uid)

    def fetch_from_recently_5_min_list(self):
        return self.redis.rpop(RECENTLY_5_MIN_REDIS_KEY)

    def recently_5_min_size(self):
        return self.redis.llen(RECENTLY_5_MIN_REDIS_KEY)

    def expire(self,key,seconds):
        self.expire(key, seconds)

    def do_not_query_with_in_hours(self, uid, hours):
        self.redis.set(DO_NOT_QUERY_IN_24_HOURS_PREFIX+str(uid), uid, ex=hours * 60 * 60)

    def is_in_do_not_query_list(self,uid):
        return True if self.redis.get(DO_NOT_QUERY_IN_24_HOURS_PREFIX+str(uid)) else False

class YouxiaRedisException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


