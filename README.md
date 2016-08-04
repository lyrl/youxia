
# Youxia Crawler 

通过机车游侠接口获取用户、用户位置，当前时速、设备基本信息等等

## Environment ##

- **python 2.7**
- **Redis**

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


按下面模板创建一个main.py

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

if __name__ == '__main__':
    run_as = sys.argv[1] if sys.argv[1] else 'crawler'
    yxcrawler = yxc.YouxiaCrawler("youxia.db", create_table=False)
    yxcrawler.run(run_as)
```

**运行爬虫实例**

主要负责抓取新用户

```bash
python youxia/main.py crawler
```

**运行位置更新实例**

负责更新现有用户的位置信息

```bash
python youxia/main.py updater
```



## Features


* Redis控制任务，可以多实例一起运行提升速度



## Licensing

"The code in this project is licensed under MIT license."