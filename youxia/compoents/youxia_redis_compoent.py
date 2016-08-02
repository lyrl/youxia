#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
from abc import ABCMeta, abstractmethod
import util
import redis


logger = util.get_logger("YouxiaRedis")
QUEUE_REDIS_KEY = 'queue' # 队列中等待抓取的
ACTIVE_REDIS_KEY = 'active' # 激活中，正在抓取的


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
       Returns:
           int: redis 队列长度
       """
        self.redis.lpush(QUEUE_REDIS_KEY, id)

    def fetch_from_queue(self):
        """  从队列中取出一个值

       Returns:
           int: 用户id
       """
        return self.redis.rpop(QUEUE_REDIS_KEY)

    def queue_size(self):
        """  获取redis队列长度

       Returns:
           int: redis 队列长度
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
        self.redis.lpush(ACTIVE_REDIS_KEY, id)

    def active_size(self):
        return self.redis.llen(ACTIVE_REDIS_KEY)

    def fetch_from_active_list(self):
        return self.redis.rpop(ACTIVE_REDIS_KEY)

    def move_active_to_queue(self):
        while self.active_size() > 0:
            self.redis.rpush(QUEUE_REDIS_KEY, self.fetch_from_active_list())

    def remove_from_active_list(self, uid):
        self.redis.lrem(ACTIVE_REDIS_KEY, 1, uid)


class YouxiaRedisException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


