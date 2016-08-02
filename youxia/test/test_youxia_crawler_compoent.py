#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import unittest
import youxia.compoents.youxia_crawler_compoent as youxia


class PrimesTestCase(unittest.TestCase):
    def test_is_five_prime(self):
        self.assertRaises(youxia.NoBaiduAppKeyError, lambda: youxia.YouxiaCratwler())


if __name__ == '__main__':
    unittest.main()