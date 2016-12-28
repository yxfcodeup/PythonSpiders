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

"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
if len(sys.argv) < 1:
    print("---> Master program needs 1 argument.\nExit...")
    print("sys.argv: " + str(sys.argv))
    sys.exit(1)
opts,args = getopt.getopt(sys.argv[1:] , "d:")
work_dir = ""
for opt,val in opts :
    if "-d" == opt :
        work_dir = str(val)
    else :
        print("Arguments ERROR.")
        print("opt:\t" + str(opt))
        print("val:\t" + str(val))
        sys.exit(1)

#script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
#work_dir = script_path
src_path = work_dir + "/src"
tools_path = src_path + "/tools"
sys.path.append(src_path)
sys.path.append(tools_path)
#Cumtomize Moduls
import service_pb2
import settings
import slaveSpider
from tools.Log import *
from tools.Platform import *

log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/slave.log"
logger = Log(log_dir , log_file)

_MGR_ = multiprocessing.Manager()
_CPU_NUM_ = cpuCount()

_ONE_DAY_IN_SECONDS_ = 60 * 60 * 24
#_LOCAL_IP_ = socket.gethostbyname(socket.gethostname())
_MASTER_IP_ = settings.master_ip
_CONFIGS_ = _MGR_.dict()
_PROCESS_INFO_ = _MGR_.dict()

#
_SSP_ = slaveSpider.SlaveSpider(work_dir)


def getConnection(time_out=10):
    channel = grpc.insecure_channel(_MASTER_IP_ + ":50051")
    stub = service_pb2.ConnectionServiceStub(channel)
    is_conn = False
    for i in range(time_out) :
        response = stub.getCon(service_pb2.conRequest(req="register"))
        logger.info("getConnection response:\t" + str(response))
        if "yes" == response.allowed :
            is_conn = True
            return is_conn
        time.sleep(1)
    return is_conn


def detectSlave(pn) :
    channel = grpc.insecure_channel(_MASTER_IP_ + ":50052")
    stub = service_pb2.DetectorServiceStub(channel)
    is_slave_alive = False
    while True :
        response = stub.detectSlave(service_pb2.deRequest(req="report"))
        #print(response.master_status)
        if "alive" == response.master_status :
            is_slave_alive = True
        else :
            is_slave_alive = False
            return is_slave_alive
        time.sleep(1)


def getTask(return_req , s_finished_task , s_return_json , s_remark_json) :
    channel = grpc.insecure_channel(_MASTER_IP_ + ":50053")
    stub = service_pb2.TaskServiceStub(channel)
    response = stub.sendTask(service_pb2.tRequest(req=return_req , return_task=s_finished_task , return_json=s_return_json , remark_json=s_remark_json))
    return response.rep , response.task_info

class SlaveManager() :
    def __init__(self) :
        self.__process_dict = {}

    def __connectionManager(self) :
        logger.info("Start connectionManager...")
        is_conn = getConnection(10)
        if is_conn :
            logger.info("Connection master[" + str(_MASTER_IP_) + "] succeeded!")
        else :
            logger.error("Connection master[" + str(_MASTER_IP_) + "] failed!")
            logger.error("Exit...")
            sys.exit(1)

    def __detectorManager(self) :
        logger.info("Start detectorManager...")
        self.__process_dict[1] = multiprocessing.Process(target=detectSlave , args=(1 , ))
        self.__process_dict[1].daemon = True
        self.__process_dict[1].start()
        _PROCESS_INFO_["__detectorManager"] = self.__process_dict[1].pid

    def __runTask(self , pn) :
        task_go = True
        req = ""    #req
        rtt = ""    #return_task
        rtj = ""    #return_json
        rmj = ""    #remark_json
        while task_go :
            time.sleep(1)
            req = "task"
            rep , task = getTask(req , rtt , rtj , rmj)
            if "end" == rep :
                logger.info("There is no task!\nCloss spider...")
                task_go = False
            else :
                #req , rtt , rtj , rmj = _SSP_.run(task)
                pass

    def __taskManager(self) :
        logger.info("Start taskManager...")
        self.__process_dict[2] = multiprocessing.Process(target=self.__runTask , args=(2 , ))
        self.__process_dict[2].daemon = True
        self.__process_dict[2].start()
        _PROCESS_INFO_["__taskManager"] = self.__process_dict[2].pid 

    def run(self) :
        self.__connectionManager()
        self.__detectorManager()
        self.__taskManager()
        logger.info("Process info:\t" + str(_PROCESS_INFO_))
        for pn,p in self.__process_dict.items() :
            p.join()


if __name__ == '__main__':
    s = SlaveManager()
    s.run()
