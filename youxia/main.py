#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import sys
import os

path = '/root/youxia'

if path not in sys.path:
    sys.path.append(path)
import compoents.youxia_crawler_compoent as yxc

if __name__ == '__main__':
    yxcrawler = yxc.YouxiaCrawler("youxia.db", create_table=True)
    yxcrawler.run()
