#_____________________________spiders.py____________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : spiders
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-25 09:10
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
import logging
import logging.config
import logging.handlers
import hashlib
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
if len(sys.argv) < 1:
    print("---> Program needs 1 argument.\nExit...")
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
log_file = log_dir + "/htmlSpider.log"
logger = Log(log_dir , log_file)
logger.init()

#----------------------------------------------------------------------------------
#-----------------------------------Ready------------------------------------------
#----------------------------------------------------------------------------------

class Spiders() :
    def __init__(self , conf_path="./spider.conf" , in_configs=None) :
        self.config_path = conf_path
        self.configs = in_configs
        self.redis_pool = None
        self.redisdb = None

    def readConfig(self) :
        self.configs = {}
        try :
            conf = configparser.ConfigParser()
            conf.read(self.config_path)
        except Exception as e :
            logger.error("readConfig() ERROR: " + str(e))
            logger.error("Exit...")
            exit(1)

        ent = "entrance"
        sig = "single"
        mut = "multi"
        sps = "spider_setting"
        try :
            #Entrance
            self.configs["is_single"] = conf.get(ent , "is_single")
            self.configs["is_log"] = conf.get(ent , "is_log")
            self.configs["log_root"] = conf.get(ent , "log_root")

            #Single url to single html file
            self.configs["process_num"] = conf.get(sig , "process_num")
            self.configs["req_sele"] = conf.get(sig , "req_sele")
            self.configs["urls_data_path"] = conf.get(sig , "urls_data_path")
            self.configs["htmls_path"] = conf.get(sig , "htmls_path")

            #Single url to plenty of html files
            self.configs["leader_url"] = conf.get(mut , "leader_url")
            self.configs["filter_word"] = conf.get(mut , "filter_word")
            self.configs["spider_way"] = conf.get(mut , "spider_way")
            self.configs["redis_host"] = conf.get(mut , "redis_host")
            self.configs["redis_port"] = conf.get(mut , "redis_port")
            self.configs["redis_db"] = conf.get(mut , "redis_db")
            self.configs["multi_htmls_path"] = conf.get(mut , "multi_htmls_path")

            #Basic spider setting
            self.configs["proxies_path"] = conf.get(sps , "proxies_path")
            self.configs["sleep_wait"] = float(conf.get(sps , "sleep_wait"))
            self.configs["is_next"] = conf.get(sps , "is_next")
            self.configs["next_xpath"] = conf.get(sps , "next_xpath")
            self.configs["unfold_all"] = conf.get(sps , "unfold_all")
            self.configs["unfold_xpath"] = conf.get(sps , "unfold_xpath")
        except Exception as e :
            logger.error("readConfig() ERROR: " + str(e))
            logger.error("Exit...")
            exit(1)

    def loadConfig(self) :
        if None == self.configs :
            if os.path.exists(self.config_path) :
                self.readConfig()
                logger.info("Configs: " + str(self.configs))
            else :
                logger.error("loadConfig() ERROR: self.config_path(" + str(self.config_path) + ") is not existed!")
                logger.error("Exit...")
                exit(1)
        elif type(dict())==self.configs and 0!=len(self.configs) :
            if "is_single" in self.configs \
            and "is_log" in self.configs \
            and "log_root" in self.configs \
            and "proxies_path" in self.configs \
            and "sleep_wait" in self.configs \
            and "is_next" in self.configs \
            and "next_xpath" in self.configs \
            and "unfold_all" in self.configs \
            and "unfold_xpath" in self.configs :
                if '1' == self.configs["is_single"] \
                and "process_num" in self.configs \
                and "req_sele" in self.configs \
                and "urls_data_path" in self.configs \
                and "htmls_path" in self.configs :
                    pass
                elif '0' == self.configs["is_single"] \
                and "leader_url" in self.configs \
                and "filter_word" in self.configs \
                and "spider_way" in self.configs \
                and "redis_host" in self.configs \
                and "redis_port" in self.configs \
                and "redis_db" in self.configs \
                and "multi_htmls_path" in self.configs :
                    pass
                else :
                    logger.error("loadConfig() ERROR: self.configs is imcomplete.")
                    logger.error("Exit...")
                    exit(1)
                logger.info("Configs: " + str(self.configs))
            else :
                logger.error("loadConfig() ERROR: self.configs is incomplete.")
                logger.error("Exit...")
                exit(1)
        else :
            logger.error("loadConfig() ERROR: self.configs(" + str(self.configs) + ") is error!")


    def dlog(self , log_str , level=1) :
        if "1" == self.configs["is_log"] :
            if 1 == level :
                logger.info(log_str)
            elif 2 == level :
                logger.warning(log_str)
            else : # level >=3 or level<=0
                logger.error(log_str)
        else :
            return False

    def seleniumHTML(self , sep_data=[] , pn=0) :
        base_time = datetime.datetime.now()
        proxies_path = self.configs["proxies_path"]
        #all_proxies = getProxies(proxies_path)
        all_proxies = checkAllProxies(proxies_path , ex_time=6)
        proxy = rotateProxies(proxies_path , all_proxies , ex_time=6)
        proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
        sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
        sesp.startSelenium()
        res = []
        rotation = 0
        rotation_top = random.randint(30 , 80)
        for line in sep_data :
            url = line[0]
            next_page = True
            href = url
            while next_page :
                time.sleep(self.configs["sleep_wait"])
                self.dlog(str(pn) + "\t" + href)
                url_split = href.split("/")
                html_name = ""
                for i in range(2 , len(url_split)) :
                    html_name += url_split[i] + "_"
                html_name = html_name[:-1]
                if rotation >= rotation_top :
                    proxy = rotateProxies(proxies_path , all_proxies , ex_time=6)
                    proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
                    sesp.restartSelenium(proxy_dict , is_browser_profile=True)
                rotation += 1
                sesp.getWebsite(href)
                page_html = sesp.getPageSource(1)
                html_sto = str(self.configs["htmls_path"]) + str(html_name)
                with open(html_sto , "a") as f :
                    f.write(str(page_html))
                href = ""
                if "1" == self.configs["unfold_all"] :
                    pagination_mh = sesp.getElementByXpath(self.configs["unfold_xpath"])
                    if False == pagination_mh :
                        with open(self.configs["log_root"]+"htmlSpider_seleniumHTML.log" , "a") as f :
                            f.write(str(line) + "\n")
                        next_page = False
                    else :
                        #pagination_html = sesp.getPageSource(2 , pagination_mh)
                        href = pagination_mh.get_attribute("href")
                        if None==href or ""==href :
                            next_page = False
                elif "1"!=self.configs["unfold_all"] and "1"==self.configs["is_next"] :
                    pagination_mh = sesp.getElementByXpath(self.configs["next_xpath"])
                    if False == pagination_mh :
                        with open(self.configs["log_root"]+"htmlSpider_seleniumHTML.log" , "a") as f :
                            f.write(str(line) + "\n")
                        next_page = False
                    else :
                        href = pagination_mh.get_attribute("href")
                        if None==href or ""==href :
                            next_page = False
                elif "0"==self.configs["unfold_all"] and "0"==self.configs["is_next"] :
                    next_page = False
                else :
                    self.dlog("spider_setting ERROR: please check the is_next and unfold_all" , 3)
                    next_page = False
        sesp.stopSelenium()


    def requestsHTML(self , url) :
        try :
            req = RequestsSpider()
            #content_or_text:content-->2    text-->1
            page_html = req.startRequests(url)
            url_split = url.split("/")
            html_name = ""
            for i in range(2 , len(url_split)) :
                html_name += url_split[i] + "_"
            html_name = html_name[:-1]
            with open(self.configs["htmls_path"] + html_name , "w") as f :
                f.write(page_html)
        except Exception as e :
            self.dlog("requestsHTML() ERROR: " + str(e) , 3)
            return False
        return True

    def getHTMLs(self , sep_data=[] , pn=0) :
        if "1" == self.configs["req_sele"] :
            for line in sep_data :
                url = line[0]
                self.dlog("Process[" + str(pn) + "]: " + str(url) , 1)
                res = self.requestsHTML(url)
                if not res :
                    self.dlog("get html failed: " + str(url) , 3)
        elif "2" == self.configs["req_sele"] :
            self.seleniumHTML(sep_data , pn)
        else :
            self.dlog("getHTMLs() ERROR: re_se is not 1 or 2!" , 3)
            self.dlog("Exit..." , 3)
            exit(1)


    def singleSpider(self , data_path=None , process_num=None) :
        data_list = []
        if None == data_path :
            data_path = self.configs["urls_data_path"]
        if None == process_num :
            process_num = self.configs["process_num"]
        if not process_num.isdigit() :
            logger.error("singleSpider() ERROR: process_num(" + str(process_num) + ") is not digit.")
            logger.error("Exit...")
            exit(1)
        #if there need single data
        if not os.path.exists(data_path) :
            logger.error("singleSpider() ERROR: there is no urls data.")
            logger.error("Exit...")
            exit(1)
        with open(data_path , "r") as f :
            for line in f.readlines() :
                split_rex = "(.*)"
                #industry types
                for i in range(5) :
                    split_rex += ",(\d{0,5})"
                #behavior types
                for i in range(5) :
                    split_rex += ",(\d{0,5})"
                line = line.replace("\n" , "")
                line_mh = re.findall(re.compile(split_rex) , line)
                if 1 == len(line_mh) :
                    line = list(line_mh[0])
                else :
                    logger.error("singleSpider() ERROR: line is error!\t" + str(line))
                    continue
                data_list.append(line)
        
        #multi process num
        p_num = int(process_num)
        if 1 == p_num :
            self.getHTMLs(sep_data=data_list , pn=0)
        elif p_num > 1 :
            sep_list = []
            sep_list = splitList(data_list=data_list , cpy_num=p_num)
            multiProcessGo(func=self.getHTMLs , args_tuple=() , sep_data=sep_list , pn_start=1 , pn_end=p_num+1)
        else :
            logger.error("singleSpider() ERROR: process num(" + str(self.configs["process_num"]) + ") is error!")
            logger.error("Exit...")
            exit(1)


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
        for md5k in keys :
            r = []
            md5k = md5k.decode("utf-8")
            r.append(md5k)
            #finished:0 --> not finished ; 1 --> finished ; 2 --> error
            try :
                r.append(self.redisdb.hget(md5k , "url").decode("utf-8"))
                r.append(self.redisdb.hget(md5k , "finished").decode("utf-8"))
                r.append(self.redisdb.hget(md5k , "time").decode("utf-8"))
            except Exception as e : 
                self.redisdb.delete(md5k)
                print("redisdb.delete(" + str(md5k) + ")")
                continue
            res.append(r)
        return res

    def getHrefs(self , undone_list , pn="") :
        base_time = datetime.datetime.now()
        proxies_path = self.configs["proxies_path"]
        all_proxies = getProxies(proxies_path)
        #all_proxies = checkAllProxies(proxies_path , ex_time=6)
        proxy = rotateProxies(proxies_path , all_proxies , base_time , base_time , 30)
        proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
        sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
        sesp.startSelenium()
        rotation = 0
        rotation_top = random.randint(30 , 80)
        for line in undone_list :
            md5_name = line[0]
            url = line[1]
            is_finished = line[2]
            finish_time = line[3]
            time.sleep(int(self.configs["sleep_wait"]))
            self.dlog(str(pn) + "\t" + url)
            if rotation >= rotation_top :
                now_time = datetime.datetime.now()
                proxy = rotateProxies(proxies_path , all_proxies , base_time , now_time , 30)
                base_time = now_time
                proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
                sesp.restartSelenium(proxy_dict , is_browser_profile=True)
            rotation += 1
            is_get = sesp.getWebsite(url)
            if not is_get :
                self.redisdb.hset(md5_name , "url" , url)
                self.redisdb.hset(md5_name , "finished" , "2")
                self.redisdb.hset(md5_name , "time" , datetime.datetime.now().strftime("%Y%m%d%H%M"))
                continue
            html_page = sesp.getPageSource(browser_or_element=1)
            if not os.path.exists(self.configs["multi_htmls_path"]) :
                os.mkdir(self.configs["multi_htmls_path"])
            with open(self.configs["multi_htmls_path"]+md5_name+".html" , "w") as f :
                f.write(html_page)
            hrefs = sesp.getAttributesOfElements(att="href" , tag="" , ele="href")
            for href in hrefs :
                sw = self.configs["spider_way"]
                hm = hashlib.md5()
                hm.update(href.encode("utf-8"))
                href_md5 = hm.hexdigest()
                if '1' == sw :
                    pass
                elif '2' == sw :
                    if len(href)<len(self.configs["filter_word"]) or href[:len(self.configs["filter_word"])]!=self.configs["filter_word"] :
                        continue
                elif '3' == sw :
                    if self.configs["filter_word"] not in href :
                        continue
                if self.redisdb.exists(href_md5) :
                    continue
                else :
                    self.redisdb.hset(href_md5 , "url" , href)
                    self.redisdb.hset(href_md5 , "finished" , "0")
                    self.redisdb.hset(href_md5 , "time" , "")
            self.redisdb.hset(md5_name , "url" , url)
            self.redisdb.hset(md5_name , "finished" , "1")
            self.redisdb.hset(md5_name , "time" , datetime.datetime.now().strftime("%Y%m%d%H%M"))
        sesp.stopSelenium()

    def subMultiSpider(self , undone_list) :
        sep_list = splitList(undone_list , cpy_num=4)
        multiProcessGo(func=self.getHrefs , args_tuple=() , sep_data=sep_list , pn_start=1 , pn_end=5)

    def multiSpider(self , process_num=None) :
        if None==process_num :
            process_num = self.configs["process_num"]
        if not process_num.isdigit() :
            self.dlog("multiSpider() ERROR: process number(" + str(process_num) + ") is error!" , 3)
            self.dlog("Exit...")
            exit(1)
        self.initRedis(self.configs["redis_host"] , self.configs["redis_port"] , self.configs["redis_db"])
        leader_url = self.configs["leader_url"]
        dm = hashlib.md5()
        dm.update(leader_url.encode("utf-8"))
        leader_url_md5 = dm.hexdigest()
        undone_list = [[leader_url_md5 , leader_url , "0" , ""] , ]
        self.getHrefs(undone_list)
        go_on = True
        while go_on :
            redis_urls = self.getDataFromRedis()
            undone_list = []
            for line in redis_urls :
                if '1' == line[2] :
                    continue
                elif '0' == line[2] :
                    undone_list.append(line)
                elif '2' == line[2] :
                    self.dlog("delete?\t" + str(line) , 1)
                else :
                    self.dlog("error line: " + str(line) , 3)
            self.subMultiSpider(undone_list)


    """
    " run the spider
    " @is_single: '1' --> singleSpider()
    "             '0' --> multiSpider()
    """
    def run(self , is_single=None) :
        self.loadConfig()
        if None == is_single :
            is_single = self.configs["is_single"]
        if '1' == is_single :
            self.singleSpider()
        elif '0' == is_single :
            self.multiSpider()
        else :
            logger.error("run() ERROR: " + str(e))
            logger.error("Exit...")
            exit(1)


if __name__ == "__main__" :
    s = Spiders(conf_path=src_path+"/spider.conf") 
    s.run()
