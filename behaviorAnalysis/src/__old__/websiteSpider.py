#_____________________________websiteSpider.py______________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : websiteSpider
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-18 15:02
# End time      :
# Function      : We can get website details.
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
import re
import getopt
import urllib
import random
import json
import pickle
import logging
import logging.config
import logging.handlers
from operator import add , itemgetter
#External Moduls
import redis
import requests
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *

#Cumtomize Moduls
import settings
from tools.seleniumSpider import *
from tools.bs4Spider import *
from tools.requestsSpider import *
from tools.proxyTool import *
from tools.listTool import *
from tools.multiProcessTool import *
from tools.stringTool import *
from tools.networkTool import *
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
#import tools

work_dir = "./"
log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/getWebsiteInfo.log"
if False == os.path.exists(log_dir) :
    os.mkdir(log_dir)
if False == os.path.exists(log_file) :
    with open(log_file , "w") as f :
        f.write("")
logging_config_dict = {
        "version":1 , 
        "disable_existing_loggers":False , 
        "formatters":{
            "standard":{
                "format":"%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s ---> %(message)s"
                } , 
            } , 
        "handlers":{
            "handler_root":{
                "level":"NOTSET" , 
                "formatter":"standard" , 
                "class":"logging.handlers.RotatingFileHandler" , 
                "filename":log_file , 
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
            "level":"NOTSET"
            } , 
        }
logging.config.dictConfig(logging_config_dict)
logger = logging.getLogger()

#----------------------------------------------------------------------------------
#-----------------------------------Ready------------------------------------------
#----------------------------------------------------------------------------------

class WebsiteSpider() :
    def __init__(self) :
        self.proxies_path = "/home/ployo/data/dataResults/freeProxy/proxies.txt"
        self.redis_host = "192.168.1.111"
        self.redis_port = 6379
        self.redis_db = 4
        pass

    def Entrance(self , in_url , pn) :
        redis_pool = redis.ConnectionPool(host=self.redis_host , port=self.redis_port , db=self.redis_db)
        sredis = redis.StrictRedis(connection_pool=redis_pool)
        all_proxies = getProxies(self.proxies_path) 
        proxy = rotateProxies(self.proxies_path , all_proxies , ex_time=3)
        proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
        sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
        sesp.startSelenium()
        task_list = [in_url , ]
        rotation = 0
        rotation_top = random.randint(30 , 80)
        while is_continue :
            url = task_list.pop(0)
            logger.info(str(pn) + "\t" + str(url))
            if rotation >= rotation_top :
                proxy = rotateProxies(self.proxies_path , all_proxies , ex_time=3)
                proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}



if __name__ == "__main__" :
    pass
