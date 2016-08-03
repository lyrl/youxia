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
    version = peewee.CharField(null=True)

    create_time = peewee.DateTimeField(null=True)
    update_time = peewee.DateTimeField(null=True)
    last_fetch_time = peewee.DateTimeField(null=True)


class Location(BaseModel):
    user = peewee.ForeignKeyField(UserInfo, to_field='uid')
    longitude = peewee.DoubleField(null=True)
    latitude = peewee.DoubleField(null=True)
    speed = peewee.DoubleField(null=True)
    time = peewee.DateTimeField(null=True)

    create_time = peewee.DateTimeField(null=True)
    update_time = peewee.DateTimeField(null=True)
    last_fetch_time = peewee.DateTimeField(null=True)


class DeviceInfo(BaseModel):
    user = peewee.ForeignKeyField(UserInfo, to_field='uid')
    gsm = peewee.CharField(null=True)
    gps = peewee.CharField(null=True)
    gps_ok = peewee.CharField(null=True)
    check_power = peewee.CharField(null=True)
    check_mswitch = peewee.CharField(null=True)
    device_status = peewee.CharField(null=True)
    gps_status = peewee.CharField(null=True)
    haiba = peewee.DoubleField(null=True)
    sensity = peewee.IntegerField(null=True)
    longitude = peewee.DoubleField(null=True)
    latitude = peewee.DoubleField(null=True)
    power = peewee.IntegerField(null=True)
    bufang = peewee.CharField(null=True)
    status2 = peewee.CharField(null=True)

    create_time = peewee.DateTimeField(null=True)
    update_time = peewee.DateTimeField(null=True)
    last_fetch_time = peewee.DateTimeField(null=True)

