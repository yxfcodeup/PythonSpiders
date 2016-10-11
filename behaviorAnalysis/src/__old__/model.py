#_____________________________model.py___________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : model
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-07-06 14:43
# End time      :
# Function      : 
# Operation     :
#-----------------------------------------------------------------------------------

import os
import sys
import time
import datetime
import multiprocessing
import re
import getopt
import urllib
import requests
import json
import logging
import logging.config
import logging.handlers
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
#External moduls
import settings
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]


#-----------------------------------Reading arguments-------------------------------
"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
if len(sys.argv) < 2 :
    print("---> Program needs 2 argument.\nExit...")
    print("sys.argv: " + str(sys.argv))
    sys.exit(1)
#-p: path
#-t: time
opts,args = getopt.getopt(sys.argv[1:] , "p:t:")
work_dir = ""
in_time= ""
for opt,val in opts :
    if "-p" == opt :
        work_dir = str(val) 
    elif "-t" == opt :
        in_time = str(val)
    else :
        print("Arguments error.")
        print("opt: " + str(opt))
        print("val: " + str(val))
        print("Exit...")
        sys.exit(1)


log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/log.log"
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


class myModel() :
    def __init__(self , spider_info , files_info , pages_info) :
        pass

    def run(self) :
        pass

    def update(self) :
        pass


if __name__ == "__main__" :
    spi = {}    #spider_info
    fin = {}    #files_info
    pai = {}    #pages_info
    g = myModel(spi , fin , pai)
    g.run()
    logger.info("afdfa")
