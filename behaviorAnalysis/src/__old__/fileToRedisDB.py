#_____________________________redisDB.py____________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : redisDB
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-17 15:22
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

#redis_pool = redis.ConnectionPool(host="192.168.1.111" , port=6379 , db=0)
#sredis = redis.StrictRedis(connection_pool=redis_pool)


#sredis.hmset("hmtest" , {"a":1 , "b":2})
#409,教育,40903,学术科研,http://www.sciencenet.cn/,中国科学网,83
url_2_type = {}
type_2_url = {}
with open("./res2.csv" , "r") as f :
    for line in f.readlines() :
        line = line.replace("\n" , "").split(",")
        url_split = line[4].split("/")
        url = ""
        for i in range(2 , len(url_split)) :
            if 2 == i :
                url += url_split[i]
            else :
                url += "/" + url_split[i]
        utype = line[2]
        if "5" == utype[0] :
            continue

        if url in url_2_type :
            if utype not in url_2_type[url] :
                url_2_type[url] = url_2_type[url] + "," + utype
        else :
            url_2_type[url] = utype

        if utype in type_2_url :
            if url not in type_2_url[utype] :
                type_2_url[utype] = type_2_url[utype] + "," + url
        else :
            type_2_url[utype] = url


def setUrl2Type(host , port , db_num) :
    redis_pool = redis.ConnectionPool(host="192.168.1.111" , port=6379 , db=0)
    sredis = redis.StrictRedis(connection_pool=redis_pool)
    for url,utypes in url_2_type.items() :
        if 0 == len(utypes.split(",")) :
            print("ERROR: " + url + "\t"+ utypes)
            continue
        elif 1 == len(utypes.split(",")) :
            utypes += ",,"
        elif 2 == len(utypes.split(",")) :
            utypes += ","
        sredis.set(url , utypes)


def setType2Url(host , port , db_num) :
    redis_pool = redis.ConnectionPool(host="192.168.1.111" , port=6379 , db=1)
    sredis = redis.StrictRedis(connection_pool=redis_pool)
    for utype,urls in type_2_url.items() :
        sredis.set(utype , urls)


setUrl2Type()
setType2Url()

