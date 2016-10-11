#_____________________________getWebsiteInfo.py_____________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : getWebsiteInfo
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-18 15:02
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

class WebsiteInfo() :
    def __init__(self) :
        pass

    def getInfo(self , url) :
        try :
            req = RequestsSpider()
            #content_or_text:content-->2    text-->1
            page_html = req.startRequests(url)
            soup = BS4Spider()
            soup.createSoup(str(page_html).lower())
            title = ""
            keywords = ""
            desc = ""
            try :
                title_mh = soup.matchOne(fname="title")
                title_match = re.findall(re.compile("<title>(.*)</title>") , str(title_mh))
                if 1 == len(title_match) :
                    title = title_match[0]
            except Exception as e :
                logger.error(e)
                title = ""
            
            try :
                keywords_mh = soup.matchOne(fname="meta" , fattrs={"name":"keywords"})
                keywords_match = re.findall(re.compile("<.*content=\"([^\"]*)\".*>") , str(keywords_mh))
                if 1 == len(keywords_match) :
                    keywords = keywords_match[0]
            except Exception as e :
                logger.error(e)
                keywords = ""
            
            try :
                desc_mh = soup.matchOne(fname="meta" , fattrs={"name":"description"})
                desc_match = re.findall(re.compile("<.*content=\"([^\"]*)\".*>") , str(desc_mh))
                if 1 == len(desc_match) :
                    desc = desc_match[0]
            except Exception as e :
                logger.error(e)
                desc = ""
        except Exception as e :
            logger.error(str(e))
            return False
        #print(title , "\n" , keywords , "\n" , desc)
        res = [title , keywords , desc]
        return res

    def multiProcessRun(self , sep_winfo , pn) :
        i = 0
        swlen = len(sep_winfo)
        redis_pool = redis.ConnectionPool(host="192.168.1.111" , port=6379 , db=2)
        sredis = redis.StrictRedis(connection_pool=redis_pool)
        for url,info in sep_winfo.items() :
            res = []
            i += 1
            logger.info("Process[" + str(pn) + "]: " + str(i) + "/" + str(swlen) + "\t" + str(url) + "\t" + str(info))
            sto_url = ""
            url_split = url.split("/")
            for i in range(2 , len(url_split)) :
                if 2 == i :
                    sto_url += url_split[i]
                else :
                    sto_url += "/" + url_split[i]
            if sredis.exists(sto_url) :
                continue
            res = self.getInfo(url)
            if type(list()) == type(res) :
                #sep_winfo[url] = sep_winfo[url] + res
                res = sep_winfo[url] + res
                for r in res :
                    sredis.lpush(sto_url , r)
                """
                with open("./dataResults/winfo_results.json" , "a") as f :
                    f.write(json.dumps({url:sep_winfo[url]}))
                    f.write("\n")
                """

    def run(self) :
        #506,浙江,50610,教育大学,http://www.zjiet.edu.cn,浙江经贸职业技术学院,78
        winfo = {}
        with open("./dataSources/baiwanzhantype/winfo.csv" , "r") as f :
            for line in f.readlines() :
                line = line.replace("\n" , "").split(",")
                winfo[line[4]] = [line[2] , line[5] , line[6]]

        sep_list = []
        data = {}
        i = 0
        wlen = len(winfo)
        iend = int(wlen/1 + 1)
        tag = 0
        for url,info in winfo.items() :
            data[url] = info
            i += 1
            tag += 1
            if i >= iend :
                sep_list.append(data)
                data = {}
                i = 0
            if tag >= wlen :
                sep_list.append(data)

        multiProcessGo(func=self.multiProcessRun , args_tuple=() , sep_data=sep_list , pn_start=1 , pn_end=2)


if __name__ == "__main__" :
    w = WebsiteInfo() 
    #res = w.getInfo("http://www.piaodown.com")
    w.run()

