#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json
import urllib2
from abc import ABCMeta, abstractmethod
import util
import redis

logger = util.get_logger("GpsReverse")

class GpsReverse:
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_gps_reverse_query(self, log, lat):
        pass


class GpsReverseImpl(GpsReverse):
    def __init__(self, appkey):
        if not appkey:
            raise GpsReverseException('appkey 不能为空')

        self.appkey = appkey
        self.connetor = BaiduConnector(appkey)

    def send_gps_reverse_query(self, log, lat):

        """
        发送经纬度反查请求

        Args:
            log (double): 经度
        Args:
            lat (double): 纬度

        Returns:
            dict: 字典
        """
        return self.connetor.send_gps_reverse_query(log, lat);




class GpsReverseException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class BaiduConnector(GpsReverse):
    def __init__(self,appkey):
        self.query_uri = "http://api.map.baidu.com/geocoder/v2/?ak=%s&location=%s,%s&output=json"
        self.appkey = appkey

    def send_gps_reverse_query(self, log, lat):
        """
        发送经纬度反查请求

        Args:
            log (double): 经度
        Args:
            lat (double): 纬度

        Returns:
            dict: 字典
        """
        try:
            content = urllib2.urlopen(self.query_uri % (self.appkey, lat, log)).read()
        except Exception:
            logger.error("[GPS反查] - 查询失败 %s ！")

        gps_dict = json.loads(content)

        addressComponent = gps_dict['result']['addressComponent']
        formatted_address = gps_dict['result']['formatted_address']
        city = addressComponent['city']
        country = addressComponent['country']
        district = addressComponent['district']
        province = addressComponent['province']

        logger.debug("[GPS反查] - 查询位置 log %s lat %s 返回 %s ！", log, lat, gps_dict)

        return {
            'country': country,
            'province': province,
            'city': city,
            'district': district,
            'formatted_address': formatted_address
        }