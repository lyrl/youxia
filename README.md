
# Youxia Crawler 

通过机车游侠接口获取用户、用户位置，当前时速、设备基本信息等等

## Environment ##

- **python 2.7**

## Dependency

```shell
pip install -r requirements.txt
```

## Configuration

**下载**
```shell
git clone https://github.com/lyrl/youxia.git
cd youxia
```
**运行**

YouxiaCrawler 需要传入两个参数
- sqlite3数据库文件路径
- redis ip
- create_table 是否自动创建表 默认False

```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import sys
import os
path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)
import compoents.youxia_crawler_compoent as yxc

if __name__ == '__main__':	  #sqlite3	  #redis ip
    yxcrawler = yxc.YouxiaCrawler("youxia.db", localhost, create_table=False)
    yxcrawler.run()

```



## Features


* Redis控制任务，可以多实例一起运行提升速度



