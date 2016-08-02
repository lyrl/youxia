#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json
import unittest
import youxia.compoents.youxia_crawler_compoent as youxia
import youxia.compoents.youxia_connector_compoent as yc
import youxia.compoents.model as model
import youxia.compoents.youxia_compoent as yxc
import datetime



class YouxiaTestCase(unittest.TestCase):

    def test_defrred_database(self):
        pass

    def test_create_table(self):
        model.deferred_db.init("sqlite3.db")

        model.UserInfo.drop_table()
        model.DeviceInfo.drop_table()
        model.Location.drop_table()

        model.UserInfo.create_table()
        model.DeviceInfo.create_table()
        model.Location.create_table()

    def test_get_top_user_id(self):
        a = yxc.YouxiaCompoentImpl("sqlite3.db")
        print a.get_top_user_id()

    def test_get(self):
        a = yxc.YouxiaCompoentImpl("sqlite3.db")
        print a.get_user_by_id(1000271860)

    def test_count(self):
        a = yxc.YouxiaCompoentImpl("sqlite3.db")
        print a.count_location_by_user_id(1000271860)


if __name__ == '__main__':
    unittest.main()