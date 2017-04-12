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
import database
from tools.Log import *
from tools.SeleniumSpider import *
from tools.Proxy import *

#----------------> log settings
log_dir = _WORK_DIR_ + settings.folder_path["log"]
log_file = log_dir + "/" + _FILE_NAME_[:_FILE_NAME_.index(_FILE_NAME_.split(".")[-1]) - 1] + ".log"
logger = Log(log_dir , log_file)


class MasterSpider() :
    def __init__(self , work_dir) :
        self.work_dir = work_dir
        self.storage = None     #存储方式
        self.undone = self.__loadDatabase(1 , settings.data_base["redis"]["undone"])      #未完成的任务集
        self.finished = self.__loadDatabase(1 , settings.data_base["redis"]["finished"])    #已完成的任务集 

    #------------------------------------------------------------------------------
    # 加载数据库
    # @param db_type 数据库类型。默认为redis
    # @return bool True，加载成功；False，加载失败
    # NOTICE:
    #------------------------------------------------------------------------------
    def __loadDatabase(self , db_type=None , db_config=None) :
        if None == db_type or "redis" == db_type or 1 == db_type :
            self.storage = 1
            self.undone = database.initRedis(
                    db_config["host"] , 
                    db_config["port"] ,
                    db_config["db"]
                    )
            self.finished = database.initRedis(
                    db_config["host"] , 
                    db_config["port"] ,
                    db_config["db"]
                    )
            return True
        elif "mysql" == db_type or 2 == db_type :
            self.storage = 2
            logger.warning("BOOM!")
            return False
        elif "mariadb" == db_type or 3 == db_type :
            self.storage = 3
            logger.warning("BOOM!")
            return False
        elif "oracle" == db_type or 4 == db_type :
            self.storage = 4
            logger.warning("BOOM!")
            return False
        else :
            logger.error("Dose not support this kind of database!")
            logger.warning("You can choose a kind of database type from database list.")
            logger.warning("Database list:")
            logger.warning("\t1. 'redis'/1")
            logger.warning("\t2. 'mysql'/2")
            logger.warning("\t3. 'mariadb'/3")
            logger.warning("\t4. 'oracle'/4")
            return False

    def __getNewTask(self) :
        reply = "reply"
        new_task = ""
        task_dict = {}
        for i in range(10) :
            _key = (self.undone.randomkey()).decode("utf-8")
            _val = (self.undone.get(_key)).decode("utf-8")
            task_dict[_key]  = _val
            self.undone.delete(_key)
        new_task = json.dumps(task_dict)
        return reply , new_task

    def __changeTask(self , return_task , result_info , remark_info) :
        task_res = json.loads(result_info)
        end_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
        for _key , _val in task_res.items() :
            self.finished.hset(_key , "url" , _val[0])
            self.finished.hset(_key , "finished" , _val[1])
            self.finished.hset(_key , "result" , _val[2])
            self.finished.hset(_key , "time" , end_time)
            self.finished.hset(_key , "remark" , remark_info)
        reply , new_task = self.__getNewTask()
        return reply , new_task
    
    def __reinputTask(self , retask) :
        old_task = json.loads(retask)
        for _key , _val in old_task.items() :
            self.undone.set(_key , _val)
        reply , new_task = self.__getNewTask()
        return reply , new_task

    def __finishTask(self) :
        if 1 == self.storage :
            if 0 == self.undone.dbsize() :
                return True
            else :
                return False
        return True

    #------------------------------------------------------------------------------
    # 对客户端发布任务
    # @param task_dict 任务集,包含ip对应的任务列表,{ip:task , ...}
    # @param client_ip 请求任务的客户端ip
    # @param req request.req 客户端请求信息
    # @param return_task request.return_task 客户端返回的已完成任务,约定json格式打包
    # @param result_json request.result_info 客户端返回的任务结果,约定json格式打包
    # @param remark_json request.remark_info 客户端返回的备注信息,约定json格式打包
    # @return task_dict 更新后的任务集,约定任务以json格式打包
    # @return reply 返回信息，用于标记约定信息
    # @retrun new_task 此次客户端请求的新任务,约定任务以json格式打包
    # NOTICE: 此函数内统一不作json处理，在其调用函数内作好json处理
    #------------------------------------------------------------------------------
    def run(self , task_dict , client_ip , req , return_task , result_info , remark_info) :
        reply = ""
        new_task = ""
        if client_ip not in task_dict :
            logger.warning("The client[" + str(client_ip) + "] is not in the task dict[" + str(task_dict) + "].We will throw it away!")
            reply = "disallow"
            return task_dict , reply , new_task

        if "" == task_dict[client_ip] :
            logger.info("Send first task to client[" + str(client_ip) + "]")
            reply , new_task = self.__getNewTask()
        else :
            if return_task == task_dict[client_ip] :
                logger.info("Get new task.")
                reply , new_task = self.__changeTask(return_task , result_info , remark_info)
            else :
                logger.error("Task[" + str(return_task) + "] returned from client[" + str(client_ip) + "] is not equal to task dict info[" + str(task_dict[client_ip]) + "]")
                logger.warning("Reinput task[" + str(task_dict[client_ip]) + "]")
                reply , new_task = self.__reinputTask(task_dict[client_ip])

        if self.__finishTask() :
            logger.info("All tasks are finished in the redis db[" + str(self.undone) + "]")
            reply = "end"
            task_dict = {}
        else :
            task_dict[client_ip] = new_task
        return task_dict , reply , new_task
