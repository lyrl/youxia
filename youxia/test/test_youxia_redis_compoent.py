#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import unittest
import youxia.compoents.youxia_redis_compoent as redis



class YouxiaRedisTestCase(unittest.TestCase):

    def test_create_table(self):
        redis.YouxiaRedisImpl('127.0.0.1')


if __name__ == '__main__':
    unittest.main()