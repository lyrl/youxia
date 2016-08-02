#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
from abc import ABCMeta, abstractmethod
import urllib2
import peewee


class YouxiaCompoent:
    __metaclass__ = ABCMeta

    @abstractmethod
    def save_base_info(self, base_info):
        pass

    @abstractmethod
    def save_location(self, location):
        pass

    @abstractmethod
    def save_user_info(self, location):
        pass


class YouxiaCompoentImpl(YouxiaCompoent):
    def __init__(self):
        pass

    def save_user_info(self, location):
        pass

    def save_location(self, location):
        pass

    def save_base_info(self, base_info):
        pass


