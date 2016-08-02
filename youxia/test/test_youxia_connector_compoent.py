#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import json
import unittest
import youxia.compoents.youxia_crawler_compoent as youxia
import youxia.compoents.youxia_connector_compoent as yc


class YouxiaConnectorTestCase(unittest.TestCase):

    def test_get_imei(self):
        yci = yc.YouxiaConnectorCompoentImpl()
        content = yci.get_imei(1000271859)
        print content
        co = json.loads(content)
        print json.dumps(co)
        print co['IMEI']

    def test_get_gps(self):
        yci = yc.YouxiaConnectorCompoentImpl()
        content = yci.get_imei(1000271859)
        co = json.loads(content)
        print yci.get_location(co['IMEI'])

    def test_get_base_info(self):
        yci = yc.YouxiaConnectorCompoentImpl()
        content = yci.get_imei(1000271859)
        co = json.loads(content)
        c = yci.get_base_info(co['IMEI'])
        print c

    def test_docstr(self):
        u = yc.UserInfo()

if __name__ == '__main__':
    unittest.main()