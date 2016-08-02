#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import peewee
deferred_db = peewee.SqliteDatabase(None)


class BaseModel(peewee.Model):
    class Meta:
        database = deferred_db


class UserInfo(BaseModel):
    uid = peewee.IntegerField(unique=True, index=True)
    start_time = peewee.DateTimeField(null=True)
    end_time = peewee.DateTimeField(null=True)
    nick_name = peewee.CharField(null=True)
    mid = peewee.IntegerField(null=True)
    imei = peewee.CharField(null=True)
    avator_url = peewee.CharField(null=True)

    create_time = peewee.DateTimeField(null=True)
    update_time = peewee.DateTimeField(null=True)
    fetch_time = peewee.DateTimeField(null=True)


class Location(BaseModel):
    user = peewee.ForeignKeyField(UserInfo)
    longitude = peewee.DoubleField()
    latitude = peewee.DoubleField()
    speed = peewee.DoubleField()

    create_time = peewee.DateTimeField(null=True)
    update_time = peewee.DateTimeField(null=True)
    fetch_time = peewee.DateTimeField(null=True)



class DeviceInfo(BaseModel):
    user = peewee.ForeignKeyField(UserInfo)
    gsm = peewee.CharField()
    gps = peewee.CharField()
    gps_ok = peewee.CharField()
    check_power = peewee.CharField()
    check_mswitch = peewee.CharField()
    device_status = peewee.CharField()
    gps_status = peewee.CharField()
    haiba = peewee.DoubleField()
    sensity = peewee.IntegerField()
    longitude = peewee.DoubleField()
    latitude = peewee.DoubleField()
    power = peewee.IntegerField()
    bufang = peewee.CharField()
    status2 = peewee.CharField()

    create_time = peewee.DateTimeField(null=True)
    update_time = peewee.DateTimeField(null=True)
    fetch_time = peewee.DateTimeField(null=True)

