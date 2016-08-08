#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import sys
import os
path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)
import compoents.youxia_crawler_compoent as yxc

if __name__ == '__main__':
    run_as = sys.argv[1] if sys.argv[1] else 'crawler'
    yxcrawler = yxc.YouxiaCrawler("youxia.db",redis_host='localhost',appkey='AB7yQP2hSzYOHWwLqPp9YXEKcToqzPtq', create_table=False)
    yxcrawler.run(run_as)
