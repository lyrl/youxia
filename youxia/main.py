#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import youxia.compoents.youxia_crawler_compoent as yxc

if __name__ == '__main__':
    yxcrawler = yxc.YouxiaCrawler("youxia.db", create_table=True)
    yxcrawler.run()
