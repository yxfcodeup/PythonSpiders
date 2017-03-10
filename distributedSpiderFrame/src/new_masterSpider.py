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
import grpc
import redis

#-------------------------------Global params---------------------------------------
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
_WORK_DIR_ = script_path
_FILE_NAME_ = os.path.split(os.path.realpath(__file__))[-1]
src_path = _WORK_DIR_ + "/src"
tools_path = _WORK_DIR_ + "/tools"
sys.path.append(_WORK_DIR_)
sys.path.append(tools_path)
#Cumtomize Moduls
import settings
from tools.Log import *
from tools.SeleniumSpider import *
from tools.Proxy import *

#----------------> log settings
log_dir = _WORK_DIR_ + settings.folder_path["log"]
log_file = log_dir + "/" + _FILE_NAME_[:_FILE_NAME_.index(_FILE_NAME_.split(".")[-1]) - 1] + ".log"
logger = Log(log_dir , log_file)

def initRedis(redis_host , redis_port , redis_db_num) :
    host_rex = "([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})" 
    host_mh = re.findall(re.compile(host_rex) , redis_host)
    if 1 != len(host_mh) :
        logger.error("initRedis() ERROR: host is error!\nExit...")
        sys.exit(1)
    if not redis_port.isdigit() :
        logger.error("initRedis() ERROR: port is error!\nExit...")
        sys.exit(1)
    if not redis_db_num.isdigit() :
        logger.error("initRedis() ERROR: db num is error!\nExit...")
        sys.exit(1)
    try :
        redis_pool = redis.ConnectionPool(host=redis_host , port=redis_port , db=redis_db_num)
        redisdb = redis.StrictRedis(connection_pool=redis_pool)
    except Exception as e :
        logger.error("initRedis() ERROR: " + str(e))
        logger.error("Exit...")
        sys.exit(1)
    logger.info("Init Redis:\t" + str(redisdb))
    return redisdb

class MasterSpider() :
    def __init__(self , work_dir) :
        self.work_dir = work_dir
        self.undone = initRedis(settings.data_base["redis"]["undone"]["host"] , settings.data_base["redis"]["undone"]["port"] , settings.data_base["redis"]["undone"]["db"])
        self.finished = initRedis(settings.data_base["redis"]["finished"]["host"] , settings.data_base["redis"]["finished"]["port"] , settings.data_base["redis"]["finished"]["db"])

    def __loadDatabase(self , db_type=None) :
        if None == db_type or "redis" == db_type :
            pass
        elif "mysql" == db_type :
            return False
        elif "mariadb" == db_type :
            return False
        elif "oracle" == db_type :
            return False
        else :
            logger.error("Dose not support this kind of database!")
            logger.warning("Database list:")
            logger.warning("\t1. redis")
            logger.warning("\t2. mysql")
            logger.warning("\t3. mariadb")
            logger.warning("\t4. oracle")
            return False

    def __loadControlers(self) :
        pass

    def run(self , task_dict , client_ip , req , return_task , return_info , remark_info) :
        new_task = ""
        if "" == task_dict[client_ip] :
            logger.info("Send first task to client[" + str(client_ip) + "]")
        else :
            if return_task == task_dict[client_ip] :
                logger.info("Get new task.")
                #masterSpider.changeTask
            else :
                logger.error("Task[" + str(return_task) + "] returned from client[" + str(client_ip) + "] is not equal to task dict info[" + str(task_dict[client_ip]) + "]")
                logger.warning("Reinput task[" + str(task_dict[client_ip]) + "]")
                #masterSpider.reinputTask

        if 0 == self.undone.dbsize() :
            logger.info("No task in the undone redis db[" + str(self.undone) + "]")
            new_task = json.dumps("ending")
            return task_dict , new_task
        else :
            new_task = "test"
            #masterSpider.getTask
            task_dict[client_ip] = json.dumps(new_task)
            logger.info("Send task to client[" + str(client_ip) + "]\nTask --> " + str(new_task))
            return task_dict , new_task
