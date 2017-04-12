#_____________________________master.py_____________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : master
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.6
# Start time    : 2016-09-22 14:30
# End time      :
# Function      : 
# Operation     :
#-----------------------------------------------------------------------------------

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

#-------------------------------Global params---------------------------------------
"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
if len(sys.argv) < 2 :
    print("ERROR: argments of master.py is absent.")
    print("sys.argv: " + str(sys.argv))
    print("Usage:")
    print("Exit...")
    sys.exit(1)
    
opts , args = getopt.getopt(sys.argv[1:] , "d:")
_WORK_DIR_ = ""
_FILE_NAME_ = (sys.argv[0]).split("/")[-1]
for opt,val in opts :
    if "-d" == opt :
        _WORK_DIR_ = str(val)
    else :
        print("Arguments ERROR.")
        print("opt:\t" + str(opt))
        print("val:\t" + str(val))
        sys.exit(1)

#script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
#work_dir = script_path
src_path = _WORK_DIR_ + "/src"
tools_path = src_path + "/tools"
sys.path.append(src_path)
sys.path.append(tools_path)
#Cumtomize Moduls
import service_pb2
import settings
import masterSpider
from tools.Log import *

#----------------> log settings
log_dir = _WORK_DIR_ + "/logs"
log_file = log_dir + "/" + _FILE_NAME_[:_FILE_NAME_.index(_FILE_NAME_.split(".")[-1]) - 1] + ".log"
logger = Log(log_dir , log_file)

#----------------> multiprocessing.Manager() settings
_MGR_ = multiprocessing.Manager()
_SLAVES_ = _MGR_.dict()                 #key: slave ip  val: last connection time
_TASKS_ = _MGR_.dict()                  #key: slave ip  val: json of task

#----------------> masterSpider object
_MSP_ = masterSpider.MasterSpider(_WORK_DIR_)

#----------------> other settings
_ONE_DAY_IN_SECONDS_ = 60 * 60 * 24
#_LOCAL_IP_ = socket.gethostbyname(socket.gethostname())
_MASTER_IP_ = settings.master_ip


class ConnectionService(service_pb2.ConnectionServiceServicer) :
    def getCon(self, request, context):
        global _SLAVES_
        global _TASKS_
        ip_info = context.peer()
        ip_info_split = ip_info.split(":")
        if 3 != len(ip_info_split) :
            logger.error("Connection error: ip_info --> " + str(ip_info))
            return service_pb2.conReply(allowed="no")
        client_ip = ip_info_split[1]
        client_port = ip_info_split[2]
        if "register" == request.req :
            #connected slave register to this master
            conn_time = datetime.datetime.now()
            _SLAVES_[client_ip] = conn_time
            _TASKS_[client_ip] = ""      #Init the task of slave
            logger.info("New slave connect this master: " + str(conn_time.strftime("%Y%m%d%H%M%S")) + " ==> " + str(ip_info_split[0])  + ":"+ str(client_ip) + ":" + str(client_port))
            logger.info("Show all slaves: " + str(_SLAVES_))
            return service_pb2.conReply(allowed="yes")
        else :
            return service_pb2.conReply(allowed="no")

def connectionMachine(work_dir , pn):
    logger.info("Activate connectionMachine...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2.add_ConnectionServiceServicer_to_server(ConnectionService() , server)
    server.add_insecure_port("[::]:50051")
    #server.add_insecure_port("192.168.1.111:50051")
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS_)
    except Exception as e :
        server.stop(0)


class DetectorService(service_pb2.DetectorServiceServicer) :
    def detectSlave(self , request , context) :
        ip_info = context.peer()
        ip_info_split = ip_info.split(":")
        if 3 != len(ip_info_split) :
            logger.error("Error detector: ip_info --> " + str(ip_info))
            return service_pb2.deReply(master_status="Network ERROR: " + str(ip_info))
        client_ip = ip_info_split[1]
        client_port = ip_info_split[2]
        #update the connnetion time
        _SLAVES_[client_ip] = datetime.datetime.now()
        #logger.info("Detect:\t" + str(client_ip) + ":" + str(client_port))
        return service_pb2.deReply(master_status="alive")

def detectorMachine(pn) :
    logger.info("Activate detectorMachine...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2.add_DetectorServiceServicer_to_server(DetectorService() , server)
    server.add_insecure_port("[::]:50052")
    server.start()
    try :
        while True :
            #detector all the slaves every 5 seconds
            dnow = datetime.datetime.now()
            for client_ip,dtime in _SLAVES_.items() :
                delta = dnow - dtime
                if delta.total_seconds() > 10 :
                    _SLAVES_.pop(client_ip , False)
                    logger.warning("There is a slave disconnected from this master?")
                    logger.warning("Delete this slave.IP is " + str(client_ip))
                    logger.info("Show all slaves: " + str(_SLAVES_))
            time.sleep(5)
    except Exception as e :
        server.stop(0)


#_DICT_ = _MGR_.dict()
class TaskService(service_pb2.TaskServiceServicer) :
    def sendTask(self , request , context) :
        global _SLAVES_
        global _TASKS_
        ip_info = context.peer()
        ip_info_split = ip_info.split(":")
        if 3 != len(ip_info_split) :
            logger.error("Send task to the slave failed!This ip_info[" + str(ip_info) + "] is error!")
            return service_pb2.tReply(task_info="Network ERROR: " + str(ip_info))
        client_ip = ip_info_split[1]
        client_port = ip_info_split[2]
        #standard functions run the task
        logger.info(":::_SLAVES_ " + str(_SLAVES_))
        logger.info(":::_TASKS_  " + str(_TASKS_))
        _TASKS_ , reply , new_task = _MSP_.run(_TASKS_ , client_ip , request.req , request.return_task , request.result_json , request.remark_json)
        if "disallow" == reply and client_ip in _SLAVES_ :
            logger.warning("The client[" + str(client_ip) + "] is illigal.We will pop it!")
            _SLAVES_.pop(client_ip , False)
        return service_pb2.tReply(rep=reply , task_info=new_task)

def taskMachine(pn) :
    logger.info("Activate taskMachine...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2.add_TaskServiceServicer_to_server(TaskService() , server)
    server.add_insecure_port("[::]:50053")
    server.start()
    try :
        while True :
            time.sleep(_ONE_DAY_IN_SECONDS_)
    except Exception as e :
        server.stop(0)



class MasterManager() :
    def __init__(self) :
        self.__process_dict = {}

    def __checkPort(self) :
        import socket
        s = socket.socket()
        s.settimeout(0.5)
        try :
            if s.connect_ex(("localhost" , 50051)) == 0 :
                logger.error("The port 50051 is open,please check it!\nExit...")
                exit(1)
            if s.connect_ex(("localhost" , 50052)) == 0 :
                logger.error("The port 50052 is open,please check it!\nExit...")
                exit(1)
            if s.connect_ex(("localhost" , 50053)) == 0 :
                logger.error("The port 50053 is open,please check it!\nExit...")
                exit(1)
        finally :
            s.close()

    def __connectionManager(self) :
        global _WORK_DiR_
        self.__process_dict[0] = multiprocessing.Process(target=connectionMachine , args=(_WORK_DIR_ , 0))
        self.__process_dict[0].daemon = True
        self.__process_dict[0].start()

    def __detectorManager(self) :
        self.__process_dict[1] = multiprocessing.Process(target=detectorMachine , args=(1 , ))
        self.__process_dict[1].daemon = True
        self.__process_dict[1].start()

    def __taskManager(self) :
        self.__process_dict[2] = multiprocessing.Process(target=taskMachine , args=(2 , ))
        self.__process_dict[2].daemon = True
        self.__process_dict[2].start()

    def run(self) :
        self.__checkPort()
        self.__connectionManager()
        self.__detectorManager()
        self.__taskManager()
        for pn,p in self.__process_dict.items() :
            p.join()



if __name__ == "__main__" :
    m = MasterManager()
    m.run()
