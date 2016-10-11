#_____________________________redisDB.py____________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : redisDB
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-26 14:29
# End time      :
# Function      : 
# Operation     :
#-----------------------------------------------------------------------------------

import os
import sys
import re
import time
import inspect
import datetime
import multiprocessing
import getopt
import random
import json
import math
import logging
import logging.config
import logging.handlers

import redis


class RedisDB() :
    def __init__(self , in_host , in_port , in_db_num) :
        host_rex = "([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})"
        host_mh = re.findall(re.compile(host_rex) , in_host)
        if 1 != len(host_mh) :
            print("RedisDB init ERROR: host is error!\nExit...")
            sys.exit(1)
        if not in_port.isdigit() :
            print("RedisDB init ERROR: port is error!\nExit...")
            sys.exit(1)
        if not in_db_num.isdigit() :
            print("RedisDB init ERROR: db num is error!\nExit...")
            sys.exit(1)
        try :
            self.redis_pool = redis.ConnectionPool(host=in_host , port=in_port , db=in_db_num)
            self.redisdb = redis.StrictRedis(connection_pool=self.redis_pool)
        except Exception as e :
            print("RedisDB init ERROR: " + str(e))
            print("Exit...")
            sys.exit(1)

    def urlFileToDB(self , file_path , split_tag="," , split_rex=None) :
        #Csv文件格式为: 
        #URL|行业分类1|行业分类2|行业分类3|行业分类4|行业分类5|行为分类1|行为分类2|行为分类3|行为分类4|行为分类5
        if None == split_rex :
            split_rex = "(.*)"
            for i in range(5) :
                split_rex += split_tag + "(\d{0,5})"
            for i in range(5) :
                split_rex += split_tag + "(\d{0,5})"
        data = None
        with open(file_path , "r") as f :
            data = f.readlines()
        for line in data :
            line = line.replace("\n" , "")
            line_mh = re.findall(re.compile(split_rex) , line)
            if 1 == len(line_mh) :
                line = line_mh[0]
            else :
                with open("./logs/urlFileToDB.log" , "a") as f :
                    f.write(line + "\n")
                continue
            url = line[0].replace("http://" , "").replace("https://" , "").replace("ftp://" , "")
            utypes = ""
            for i in range(1 , len(line)) :
                utypes += line[i] + ","
            utypes = utypes[:-1]
            self.redisdb.set(url , utypes)


if __name__ == "__main__" :
    r = RedisDB("192.168.1.111" , "6379" , "0")
    r.urlFileToDB("./dataSources/url_20160902.csv")
