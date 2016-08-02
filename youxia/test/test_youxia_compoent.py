#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json
import unittest
import youxia.compoents.youxia_crawler_compoent as youxia
import youxia.compoents.youxia_connector_compoent as yc
import youxia.compoents.Model as model
import datetime



class YouxiaTestCase(unittest.TestCase):

    def test_defrred_database(self):
        model.deferred_db.init("sqlite3.db")
        u = model.UserInfo()
        u.create_time = datetime.datetime.today()
        u.uid = 100000
        u.save()

        uu = model.UserInfo()
        uu.create_time = datetime.datetime.today()
        uu.save()

    def test_create_table(self):
        model.deferred_db.init("sqlite3.db")
        model.UserInfo.create_table()


if __name__ == '__main__':
    unittest.main()