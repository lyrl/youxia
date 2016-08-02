#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
from abc import ABCMeta, abstractmethod
import urllib2

import time

YOUXIA_ID_IMEI = "http://app1.moootooo.com:8001/api/getuserinfo.php?upid=%s"
YOUXIA_IMEI_GPS = "http://app1.moootooo.com:8001/api/getlatlng_baidu.php?imei=%s"
YOUXIA_IMEI_BASE_INFO = "http://app1.moootooo.com:8001/api/getdeviceall.php?imei=%s"
URLLIB2_TIMEOUT = 60


class YouxiaConnectorCompoent:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_imei(self, id):
        pass

    @abstractmethod
    def get_location(self, imei):
        pass

    @abstractmethod
    def get_base_info(self, imei):
        pass


class YouxiaConnectorCompoentImpl(YouxiaConnectorCompoent):
    def __init__(self):
        pass

    def get_base_info(self, imei):
        """获取基本信息
            Args:
                imei (str): 设备上手机卡的imei号

            Returns:
                str: Json形式的数据
                example:
                {
                  "gsm": "良",
                  "dianchi_img": "4.03",
                  "dianp_img": "12.54",
                  "gps": "正常(14颗卫星)",
                  "gps_ok": "定位成功",
                  "check_power": "正常",
                  "check_mswitch": "关闭",
                  "device_status": "设备进入休眠状态 ",
                  "gps_status": "差",
                  "haiba": "55.08",
                  "sensity": "9",
                  "long": 116.295708,
                  "lat": 40.053459,
                  "power": 0,
                  "check_lock": 1,
                  "check_fire_v": 0,
                  "check_fire": "点火",
                  "bufang": "自动",
                  "bufang_v": 1,
                  "chefang": "自动",
                  "chefang_v": 1,
                  "low": "11.8伏特",
                  "radius": "无",
                  "radius_v": 0,
                  "delay": "2秒",
                  "standby": "正常",
                  "standby_v": "0",
                  "status2": "休眠"
                }

            Raises:
                IOError: An error occurred accessing the bigtable.Table object.
            """
        return self.__youxia_read__(YOUXIA_IMEI_BASE_INFO % imei)

    def get_location(self, imei):
        """获取地理位置信息.

            Args:
                imei (str): 设备上手机卡的imei号

            Returns:
                str: JSON形式数据

                {
                  "lat": 116.3081913,
                  "lng": 40.060944,
                  "time": "2016-07-28 09:47:11",
                  "speed": "0.00"
                }

            Raises:
                IOError: An error occurred accessing the bigtable.Table object.
            """
        return self.__youxia_read__(YOUXIA_IMEI_GPS % imei)

    def get_imei(self, id):
        """通过id尝试获取imei号

            Args:
                id (int): 机车游侠平台的用户id

            Returns:
                str:
                {
                  "STARTTIME": "2016-04-10",
                  "ENDDATE": "2017-04-10",
                  "NICKNAME": null,
                  "AVATOR": null,
                  "MODEL": null,
                  "BRAND": null,
                  "MID": "56001167",
                  "VERSION": "k61",
                  "IMEI": "356802030712896",
                  "avator_url": "http://photo.moootooo.com/images/header.jpg"
                }

            Raises:
                IOError: An error occurred accessing the bigtable.Table object.
            """
        return self.__youxia_read__(YOUXIA_ID_IMEI % id)


    def __youxia_read__(self, url):
        try:
            resp = urllib2.urlopen(url, timeout=URLLIB2_TIMEOUT)
        except urllib2.URLError as e:
            raise YouxiaConnectorException(e.message)

        if not resp or resp.code != 200:
            raise YouxiaConnectorException("response code : " + resp.code)

        return resp.read()


class YouxiaConnectorException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message