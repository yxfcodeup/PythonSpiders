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

script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
src_path = script_path + "/src"
tools_path = script_path + "/tools"
sys.path.append(script_path)
sys.path.append(tools_path)
#Cumtomize Moduls
import settings
from tools.Log import *
from tools.SeleniumSpider import *
from tools.Proxy import *

#----------------> log settings
log_dir = script_path + settings.folder_path["log"]
log_file = log_dir + "/masterSpider.log"
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

    def getTask(self) :
        reply = "reply"
        new_task = json.dumps(new_task)
        return reply , new_task

    def getNewTask(self) :
        reply , new_task = self.getTask()
        return reply , new_task

    def reinputTask(self) :
        reply , new_task = self.getTask()
        return reply , new_task

    #--------------------------------------------------------------------------
    # 对客户端发布任务
    # @param task_pool 任务池,包含ip对应的任务列表,{ip:{task:start_time,...},...}
    # @param client_ip 请求任务的客户端ip
    # @param req request.req 客户端请求信息
    # @param return_task request.return_task 客户端返回的已完成任务,约定json格式打包
    # @param return_json request.return_info 客户端返回的任务结果,约定json格式打包
    # @param remark_json request.remark_info 客户端返回的备注信息,约定json格式打包
    # @return task_pool 更新后的任务池,约定任务以json格式打包
    # @return reply 返回信息
    # @retrun new_task 此次客户端请求的新任务,约定任务以json格式打包
    # NOTICE: 此函数内统一不作json处理，在其调用函数内作好json处理
    #--------------------------------------------------------------------------
    def run(self , task_pool , client_ip , req , return_task , return_json , remark_json) :
        new_task = ""
        reply = ""
        task_dict = {}
        if client_ip in task_pool :
            task_dict = task_pool[client_ip]
        else :
            logger.warning("The client{" + str(client_ip) + "} is not in the task pool{" + str(task_pool) + "}")

        if 0 == len(task_dict) :
            logger.info("Send first task to client{" + str(client_ip) + "}")
            reply , new_task = self.getTask() 
        else :
            if return_task in task_dict :
                logger.info("Get new task.")
                reply , new_task = self.getNewTask()
            else :
                logger.error("Task{" + str(return_task) + "} returned from client{" + str(client_ip) + "} is not in task list{" + str(task_dict) + "}")
                logger.warning("Reinput task{" + str(task_dict) + "}")
                reply , new_task = self.reinputTask()

        task_dict[new_task] = datetime.datetime.now()
        task_pool[client_ip] = task_dict

        return task_pool , reply , new_task

        """
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
        """
