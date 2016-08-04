#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import datetime
import json
from abc import ABCMeta, abstractmethod
import youxia.compoents.model as model
import util


logger = util.get_logger("YouxiaDao")


class YouxiaCompoent:
    __metaclass__ = ABCMeta

    @abstractmethod
    def save_device_info(self, device_info, uid):
        pass

    @abstractmethod
    def update_device_info(self, device_info, uid):
        pass

    @abstractmethod
    def save_location(self, location, uid):
        pass

    @abstractmethod
    def update_location(self, location, uid):
        pass

    @abstractmethod
    def save_user_info(self, user_info, id):
        pass

    @abstractmethod
    def update_user_info(self, user_info, id):
        pass

    @abstractmethod
    def get_user_by_id(self, uid):
        pass

    @abstractmethod
    def get_device_info_by_user_id(self, uid):
        pass

    @abstractmethod
    def get_top_user_id(self):
        pass


class YouxiaCompoentImpl(YouxiaCompoent):
    def __init__(self, db_url, create_table=False):
        """
        Youxia 数据库访问层
        暂支持sqlite3

        Args:
            db_url (str): sqlite3数据库文件路径 eg: /root/sqlite3.db
            create_table (bool): 是否需要自动创建表
        """

        model.deferred_db.init(db_url)

        try:
            model.deferred_db.connect()
        except Exception as e:
            raise YouxiaException(u'数据库连接失败: ' + e.message)

        if create_table:
            model.UserInfo.create_table()
            model.Location.create_table()
            model.DeviceInfo.create_table()

    def save_user_info(self, user_info, id):
        """
        保存用户信息

        Args:
            user_info (str): 用户信息 json 形式
            id (int): 用户id

            eg:
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

        Returns:
            model.UserInfo: 用户对象
        """
        user_info_json_dict = json.loads(user_info)
        user_info = model.UserInfo()

        user_info.uid = id
        self.__fill_json_to_user_info__(user_info, user_info_json_dict)
        user_info.create_time = datetime.datetime.now()

        try:
            user_info.save()
        except Exception as e:
            logger.error(u"[数据库访问] - 保存用户信息失败 %s 用户id:%s" % (e.message, id))
            raise YouxiaDaoException(u"[数据库访问] - 保存用户信息失败 %s 用户id:%s" % (e.message, id))

        logger.debug(u"[数据库访问] - 保存用户信息成功 id:%s" % id)

        return user_info

    def save_location(self, location, uid):
        """
        保存位置信息、轨迹

        Args:
            location (str): 用户信息 json 形式
            uid (int): 用户id

        Returns:
            model.Location: 位置对象
        """
        user_info = self.get_user_by_id(uid)

        location_json_dict = json.loads(location)

        if not user_info:
            raise YouxiaDaoException(u"用户id %s 不存在，无法保存位置信息!" % uid)

        location = model.Location()
        self.__fill_json_to_location_info__(location, location_json_dict)
        location.user = user_info
        location.create_time = datetime.datetime.now()

        try:
            location.save()
        except Exception as e:
            logger.error(u"[数据库访问] - 保存位置信息失败 %s 用户id:%s" % (e.message, uid))
            raise YouxiaDaoException(u"[数据库访问] - 保存位置信息失败 %s 用户id:%s" % (e.message, uid))

        logger.debug(u"[数据库访问] - 保存位置信息成功 用户id:%s" % uid)

        return location

    def save_device_info(self, device_info, uid):
        """
        保存设备信息

        Args:
            device_info (str): 设备信息 json 形式
            uid (int): 用户id

        Returns:
            model.DeviceInfo: 设备信息对象
        """

        user_info = self.get_user_by_id(uid)
        device_info_json_dict = json.loads(device_info)

        if not user_info:
            raise YouxiaDaoException(u"用户id %s 不存在，无法保存位置信息!" % uid)

        device_info = model.DeviceInfo()
        self.__fill_json_to_device_info__(device_info, device_info_json_dict)
        device_info.create_time = datetime.datetime.now()
        device_info.user = user_info

        try:
            device_info.save()
        except Exception as e:
            logger.error(u"[数据库访问] - 保存设备信息失败 %s 用户id:%s" % (e.message, uid))
            raise YouxiaDaoException("[数据库访问] - 保存设备信息失败 %s 用户id:%s" % (e.message, uid))

        logger.debug(u"[数据库访问] - 保存设备信息成功 用户id:%s" % uid)

        return device_info

    def update_location(self, location, uid):
        """
        更新位置信息

        Args:
            uid (int): 用户唯一标识
            location (str): json形式的位置信息
        """
        location_json_dict = json.loads(location)
        user_info = self.get_user_by_id(uid)
        location = model.Location()

        location.user = user_info
        self.__fill_json_to_location_info__(location, location_json_dict)
        location.last_fetch_time = datetime.datetime.now()

        try:
            location.save()
        except Exception as e:
            logger.error(u"[数据库访问] - 保存位置信息失败 %s 用户id:%s" % (e.message, uid))
            raise YouxiaDaoException(u"[数据库访问] - 保存位置信息失败 %s 用户id:%s" % (e.message, uid))

        logger.debug(u"[数据库访问] - 保存位置信息成功 用户id:%s" % uid)

        return location

    def update_device_info(self, device_info, uid):
        device_info_json_dict = json.loads(device_info)
        device_info = self.get_device_info_by_user_id(uid)

        self.__fill_json_to_device_info__(device_info, device_info_json_dict)

        device_info.save()

    def update_user_info(self, user_info, id):
        user_info_json_dict = json.loads(user_info)
        user_info = self.get_user_by_id(id)

        self.__fill_json_to_user_info__(user_info, user_info_json_dict)
        user_info.save()

    def get_user_by_id(self, uid):
        """
        根据uid查询

        Args:
            uid (int): 用户唯一标识
        Returns:
            model.UserInfo: 用户对象
        """
        try:
            user_info = model.UserInfo.get(uid=uid)
        except Exception as e:
            logger.info(u"[数据库访问] - 用户不存在 id: %s" % uid)
            user_info = None
        return user_info

    def get_device_info_by_user_id(self, uid):
        """
        根据用户id查询设备信息

        Args:
            uid (int): 用户唯一标识
        Returns:
            model.DeviceInfo: 位置信息对象
        """
        try:
            device_info = model.DeviceInfo.get(user=uid)
        except:
            device_info = None

        return device_info

    def get_top_user_id(self):
        """
        获取数据库中最大的userid

        Returns:
            int: 用户id
        """
        try:
            user = model.UserInfo.select().order_by(model.UserInfo.uid.desc()).limit(1).get()
        except Exception as e:
            logger.info(u"[数据库访问] - 用户表为空 %s" % e)
            return 0

        if user:
            return user.uid
        else:
            return 0

    def count_location_by_user_id(self, uid):
        user = self.get_user_by_id(uid)
        return model.Location.select().where(model.Location.user == user).count()

    def get_recent_active_user(self):
        """
        获取最近活动的用户 默认 1 天内
        按用户id去重

        Returns:
            list[model.Location]: 用户列表
        """
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(1)
        return model.Location.select().where(model.Location.time.between(yesterday, today)).group_by(model.Location.user)

    def get_last_location(self, uid):
        """
        获得用户最后一次的位置信息

        Args:
            uid (int): 用户唯一标识
        Returns:
            model.Location: 位置信息
        """
        user = self.get_user_by_id(uid)

        if not user:
            return None

        try:
            last_location = model.Location.select().where(model.Location.user == user).order_by(model.Location.time.desc()).limit(1).get()
        except Exception:
            last_location = None
            logger.info(u"[数据库访问] - 用户 %s 没有任何位置记录!" % user.uid)

        return last_location


    def __fill_json_to_user_info__(self, user_info, user_info_json_dict):
        date_format = '%Y-%M-%d'
        user_info.start_time = datetime.datetime.strptime(user_info_json_dict['STARTTIME'], date_format)
        user_info.end_time = datetime.datetime.strptime(user_info_json_dict['ENDDATE'], date_format)
        user_info.nick_name = user_info_json_dict['NICKNAME']
        user_info.mid = user_info_json_dict['MID']
        user_info.version = user_info_json_dict['VERSION']
        user_info.imei = user_info_json_dict['IMEI']
        user_info.avator_url = user_info_json_dict['avator_url']
        user_info.update_time = datetime.datetime.now()
        user_info.last_fetch_time = datetime.datetime.now()

    def __fill_json_to_location_info__(self, location, location_json_dict):
        date_time_format = '%Y-%m-%d %H:%M:%S'
        location.longitude = location_json_dict['lat']
        location.latitude = location_json_dict['lng']
        location.speed = location_json_dict['speed']
        location.time = datetime.datetime.strptime(location_json_dict['time'], date_time_format)
        location.update_time = datetime.datetime.now()
        location.last_fetch_time = datetime.datetime.now()

    def __fill_json_to_device_info__(self, device_info, device_info_json_dict):
        device_info.gsm = device_info_json_dict['gsm']
        device_info.gps = device_info_json_dict['gps']
        device_info.gps_ok = device_info_json_dict['gps_ok']
        device_info.check_power = device_info_json_dict['check_power']
        device_info.check_mswitch = device_info_json_dict['check_mswitch']
        device_info.device_status = device_info_json_dict['device_status']
        device_info.gps_status = device_info_json_dict['gps_status']
        device_info.haiba = 0 if not '' else device_info_json_dict['haiba']
        device_info.sensity = device_info_json_dict['sensity']
        device_info.longitude = float(device_info_json_dict['lat'])
        device_info.latitude = float(device_info_json_dict['long'])
        device_info.power = device_info_json_dict['power']
        device_info.bufang = device_info_json_dict['bufang']
        device_info.status2 = device_info_json_dict['status2']
        device_info.create_time = datetime.datetime.now()
        device_info.update_time = datetime.datetime.now()
        device_info.last_fetch_time = datetime.datetime.now()




class YouxiaException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class YouxiaDaoException(YouxiaException):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


