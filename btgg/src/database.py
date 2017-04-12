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

def initRedis(redis_host , redis_port , redis_db_num) :
    host_rex = "([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})" 
    host_mh = re.findall(re.compile(host_rex) , redis_host)
    if 1 != len(host_mh) :
        logger.error("host must be a ipv4 format!\nExit...")
        sys.exit(1)
    if type(int()) != type(redis_port) and (not str(redis_port).isdigit()) :
        logger.error("port be digit!\nExit...")
        sys.exit(1)
    if type(int()) != type(redis_port) and (not str(redis_db_num).isdigit()) :
        logger.error("db number must be digit!\nExit...")
        sys.exit(1)
    try :
        redis_pool = redis.ConnectionPool(host=redis_host , port=redis_port , db=redis_db_num)
        redisdb = redis.StrictRedis(connection_pool=redis_pool)
    except Exception as e :
        logger.error(str(e))
        logger.error("Exit...")
        sys.exit(1)
    logger.info("Init Redis: " + str(redisdb))
    return redisdb

if __name__ == "__main__" :
    initRedis("192.168.1.111" , '6379' , 0)
