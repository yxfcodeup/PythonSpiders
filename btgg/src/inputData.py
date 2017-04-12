#----------------------------------------------------------------------------------
#-----------------------------------Ready------------------------------------------
#----------------------------------------------------------------------------------
#System Moduls
import os
import sys
import time
import datetime
import multiprocessing
import configparser
import re
import getopt
import urllib
import random
import json
import pickle
import socket
import logging
import logging.config
import logging.handlers
import hashlib
from operator import add , itemgetter
from concurrent import futures
#External Moduls
import redis
import database

#-------------------------------Global params---------------------------------------
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
_WORK_DIR_ = script_path
_FILE_NAME_ = os.path.split(os.path.realpath(__file__))[-1]

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

def inputDataToRedis(url=None) :
    rdb = database.initRedis("192.168.1.111" , "6379" , 7)
    root_link = "http://bt.gg/?page="
    if None == url :
        for i in range(3327) :
            url = root_link + str(i)
            hm = hashlib.md5()
            hm.update(url.encode("utf-8"))
            md5k = hm.hexdigest()
            rdb.set(md5k , url)
    else :
        hm = hashlib.md5()
        hm.update(url.encode("utf-8"))
        md5k = hm.hexdigest()
        rdb.set(md5k , url)
    return rdb.dbsize()

if __name__ == "__main__" :
    res = inputDataToRedis()
    print(res)
