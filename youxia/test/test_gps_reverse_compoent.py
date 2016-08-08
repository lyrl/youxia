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
import youxia.compoents.youxia_gps_reverse_compoent as gps


class GpsReverseTestCase(unittest.TestCase):

    def test_baidu_reverse(self):
        bgr = gps.BaiduConnector("AB7yQP2hSzYOHWwLqPp9YXEKcToqzPtq")
        print ','.join(bgr.send_gps_reverse_query(110, 31))

if __name__ == '__main__':
    unittest.main()