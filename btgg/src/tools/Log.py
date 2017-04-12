
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
import logging
import logging.config
import logging.handlers
import hashlib
from operator import add , itemgetter


class Log() :
    def __init__(self , log_dir , log_file , basic_way=False , log_level="NOTSET") :
        try :
            if False == os.path.exists(log_dir) :
                os.mkdir(log_dir)
            if False == os.path.exists(log_file) :
                with open(log_file , "w") as f :
                    f.write("")
        except Exception as e :
            print("Log __init__ ERROR: " + str(e))
            print("Exit...")
            exit(1)
        self.log_dir = log_dir
        self.log_file = log_file
        self.logger = None
        if basic_way :
            logging.basicConfig(
                level=logging.NOTSET ,
                format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
                datefmt = "%a, %Y%m%d %H:%M:%S" ,
                filename = self.log_file ,
                filemode = "a")
            self.logger = logging.getLogger()
        else :
            logging_config_dict = {
                "version":1 , 
                "disable_existing_loggers":False , 
                "formatters":{
                    "standard":{
                        "format":"%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" 
                        } , 
                    } , 
                "handlers":{
                    "handler_root":{
                        "level":"NOTSET" , 
                        "formatter":"standard" , 
                        "class":"logging.handlers.RotatingFileHandler" , 
                        "filename":self.log_file , 
                        "maxBytes":1024*1024 , 
                        "backupCount":0 , 
                        } , 
                    "handler_stderr":{
                        "level":"INFO" , 
                        "formatter":"standard" , 
                        "class":"logging.StreamHandler" , 
                        "stream":"ext://sys.stderr"
                        } , 
                    } , 
                "root":{
                    "handlers":["handler_root" , "handler_stderr"] ,  
                    "level":log_level
                    } , 
                }
            logging.config.dictConfig(logging_config_dict)
            self.logger = logging.getLogger()
    
    def info(self , info_str) :
        self.logger.info(str(info_str))

    def error(self , err_str) :
        self.logger.error(str(err_str))

    def warning(self , war_str) :
        self.logger.warning(str(war_str))
