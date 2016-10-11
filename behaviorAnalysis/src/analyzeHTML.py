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
import hashlib
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

"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
if 1 != len(sys.argv) :
    print("---> Program needs 1 argument.\nExit...")
    print("sys.argv: " + str(sys.argv))
    sys.exit(1)
opts,args = getopt.getopt(sys.argv[1:] , "d:")
work_dir = ""
for opt,val in opts :
    if "-p" == opt :
        work_dir = str(val)
    else :
        print("Arguments ERROR.")
        print("opt:\t" + str(opt))
        print("val:\t" + str(val))
        sys.exit(1)

src_path = work_dir + "/src"
tools_path = src_path + "/tools"
sys.path.append(src_path)
sys.path.append(tools_path)
#Cumtomize Moduls
import settings
from tools.Platform import *
from tools.MD5 import *
from tools.Log import *
from tools.SeleniumSpider import *
from tools.BS4Spider import *
from tools.RequestsSpider import *
from tools.Proxy import *
from tools.ListTool import *
from tools.MultiProcess import *
from tools.StringTool import *
from tools.Network import *
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

#work_dir = "./"
log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/analyzeHTML.log"
logger = Log(log_dir , log_file)
logger.init()
#----------------------------------------------------------------------------------
#-----------------------------------Ready------------------------------------------
#----------------------------------------------------------------------------------


class AnalyzeHTML() :
    def __init__(self , conf_path="./spider.conf" , in_configs=None) :
        self.configs = in_configs
        self.redis_pool = None
        self.redisdb = None

    def readConfig(self) :
        self.config = {}
        try :
            conf = configparser.ConfigParser()
            conf.read(self.config_path)
        except Exception as e :
            logger.error("readConfig() ERROR: " + str(e))
            logger.error("Exit...")
            exit(1)

        ent = "entrance"
        try :
            #Entrance
            self.configs[""]

    def analyzeHTML(self , html) :
        res = []
        soup = BeautifulSoup(str(html) , "lxml")
        head = soup.findAll("head")
        body = soup.findAll("body")
        soup = BeautifulSoup(str(body) , "lxml")
        [script.extract() for script in soup.findAll("script")]
        [style.extract() for style in soup.findAll("style")]
        reg = re.compile("<[^>]*>")
        content = reg.sub("" , soup.prettify())
        reg2 = re.compile("\s")
        content = reg2.sub("" , str(content))
        res.append(content)
        #...............title,keywords,desc
        soup = BS4Spider()
        #soup.createSoup(str(head).lower())
        soup.createSoup(str(html).lower())
        title = ""
        keywords = ""
        desc = ""
        address = ""
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

        try :
            addrs_mh = soup.matchOne(fname="div" , fattrs={"class":"breadnav fn-left"})
            soup2 = BeautifulSoup(str(addrs_mh) , "lxml")
            addrs_text = soup2.get_text()
            addrs_list = addrs_text.split("\xa0>\xa0")
            if len(addrs_list)>=2 and "首页" in addrs_list[0] :
                address = addrs_list[1]
            else :
                address = ""
        except Exception as e :
            logger.error(e)
            address = ""
        res = [address , title , keywords , desc] + res
        return res

    def initRedis(self , in_host , in_port , in_db_num) :
        host_rex = "([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})"
        host_mh = re.findall(re.compile(host_rex) , in_host)
        if 1 != len(host_mh) :
            print("initRedis() ERROR: host is error!\nExit...")
            sys.exit(1)
        if not in_port.isdigit() :
            print("initRedis() ERROR: port is error!\nExit...")
            sys.exit(1)
        if not in_db_num.isdigit() :
            print("initRedis() ERROR: db num is error!\nExit...")
            sys.exit(1)
        try :
            self.redis_pool = redis.ConnectionPool(host=in_host , port=in_port , db=in_db_num)
            self.redisdb = redis.StrictRedis(connection_pool=self.redis_pool)
        except Exception as e :
            print("initRedis() ERROR: " + str(e))
            print("Exit...")
            sys.exit(1)
    
    def getDataFromRedis(self) :
        res = []
        keys = self.redisdb.keys(pattern="*")
        for k in keys :
            r = []
            k = k.decode("utf-8")
            r.append(k)
            #finished:0 --> not finished ; 1 --> finished ; 2 --> error
            r.append(self.redisdb.hget(k , "finished").decode("utf-8"))
            r.append(self.redisdb.hget(k , "time").decode("utf-8"))
            res.append(r)
        return res

    def decodingUrl(self , undone_list , urls) :
        res = {}
        for url in urls :
            url = url[0]
            m = hashlib.md5()
            m.update(url.encode("utf-8"))
            md5_name = m.hexdigest()
            md5_name += ".html"
            if md5_name in undone_list :
                if md5_name not in res :
                    res[md5_name] = url
                else :
                    print(md5_name , res[md5_name] , url)
        return res

    def multiAnalyze(self , md5_url_dict , pn) :
        print("Process[" + str(pn) + "] go!")
        for file_name , url in md5_url_dict.items() :
            h = ""
            with open("./dataResults/htmls/"+file_name , "r") as f :
                h = f.read()
            res = self.analyzeHTML(h)
            with open("./dataResults/djson/"+file_name[:-5]+".json", "a") as f :
                f.write(json.dumps([url,] + res))

    def run(self) :
        file_list = os.listdir("./dataResults/htmls")
        self.initRedis("192.168.1.111" , "6380" , "1")
        redis_urls = self.getDataFromRedis()
        md5_url_dict = self.decodingUrl(file_list , redis_urls)
        sep_list = splitDict(md5_url_dict , cpy_num=3)
        multiProcessGo(func=self.multiAnalyze , args_tuple=() , sep_data=sep_list , pn_start=0 , pn_end=3)



if __name__ == "__main__" :
    a = AnalyzeHTML()
    a.run()
