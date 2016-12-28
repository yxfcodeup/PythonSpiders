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

log_dir = script_path + settings.folder_path["log"]
log_file = log_dir + "/slaveSpider.log"
logger = Log(log_dir , log_file)

def readConfig(conf_path="./spider.conf") :
    if not os.path.exists(conf_path) :
        logger.error("readConfig() ERROR: config file is not existed!")
        sys.exit(1)
    try :
        conf = configparser.ConfigParser()
        conf.read(conf_path)
    except Exception as e :
        logger.error("readConfig() ERROR: " + str(e))
        logger.error("Exit...")
        sys.exit(1)
    
    ent = "entrance"
    sig = "single"
    mut = "multi"
    sps = "spider_setting"
    try :
        #Entrance
        _CONFIGS_["is_single"] = conf.get(ent , "is_single")
        _CONFIGS_["is_log"] = conf.get(ent , "is_log")
        _CONFIGS_["log_root"] = conf.get(ent , "log_root")

        #Single url to single html file
        _CONFIGS_["process_num"] = conf.get(sig , "process_num")
        _CONFIGS_["req_sele"] = conf.get(sig , "req_sele")
        _CONFIGS_["urls_data_path"] = conf.get(sig , "urls_data_path")
        _CONFIGS_["htmls_path"] = conf.get(sig , "htmls_path")

        #Single url to plenty of html files
        _CONFIGS_["leader_url"] = conf.get(mut , "leader_url")
        _CONFIGS_["filter_word"] = conf.get(mut , "filter_word")
        _CONFIGS_["spider_way"] = conf.get(mut , "spider_way")
        _CONFIGS_["redis_host"] = conf.get(mut , "redis_host")
        _CONFIGS_["redis_port"] = conf.get(mut , "redis_port")
        _CONFIGS_["redis_db"] = conf.get(mut , "redis_db")
        _CONFIGS_["multi_htmls_path"] = conf.get(mut , "multi_htmls_path")

        #Basic spider setting
        _CONFIGS_["proxies_path"] = conf.get(sps , "proxies_path")
        _CONFIGS_["sleep_wait"] = float(conf.get(sps , "sleep_wait"))
        _CONFIGS_["is_next"] = conf.get(sps , "is_next")
        _CONFIGS_["next_xpath"] = conf.get(sps , "next_xpath")
        _CONFIGS_["unfold_all"] = conf.get(sps , "unfold_all")
        _CONFIGS_["unfold_xpath"] = conf.get(sps , "unfold_xpath")
    except Exception as e :
        print("readConfig() ERROR: " + str(e))
        print("Exit...")
        sys.exit(1)

def loadConfig(conf_path="./spider.conf" , in_configs=None) :
    if None == in_configs :
        readConfig(conf_path)
    else :
        try :
            for k,v in in_configs.items() :
                _CONFIGS_[k] = v
        except Exception as e :
            print("loadConfig() ERROR: " + str(e))
            print("Exit...")
            sys.exit(1)

def checkPid(pid) :
    try :
        os.kill(pid , 0)
    except OSError as e :
        return False 
    else :
        return True

class SlaveSpider() :
    def __init__(self , work_dir) :
        self.work_dir = work_dir

    def run(self , task) :
        print("tcrun:\t" + str(task))
        time.sleep(2)
        rtt = "test"
        rtj = "" 
        rmj = ""
        return json.dumps(rtt) , json.dumps(rtj) , json.dumps(rmj)


if __name__ == "__main__" :
    bt = datetime.datetime.now()
