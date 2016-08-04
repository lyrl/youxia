#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import unittest
import youxia.compoents.youxia_crawler_compoent as youxia
import sys

class PrimesTestCase(unittest.TestCase):
    def test_run(self):
        ycrawler = youxia.YouxiaCrawler("sqlite3.db")
        # ycrawler.run()

if __name__ == '__main__':
    unittest.main()