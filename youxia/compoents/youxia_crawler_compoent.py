#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34


class YouxiaCrawler(object):
    def __init__(self, baidu_api_key=None):
        if baidu_api_key is None:
            raise NoBaiduAppKeyError("请提供百度GeoCoding访问key，详情见 http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding")


class YouxiaException(Exception):
    pass


class NoBaiduAppKeyError(YouxiaException):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message