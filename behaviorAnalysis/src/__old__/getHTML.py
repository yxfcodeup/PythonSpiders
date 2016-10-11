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
log_file = log_dir + "/getHTML.log"
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

class HTMLS() :
    def __init__(self) :
        pass

    def getHTML(self , num_data , pn) :
        proxies_path = "/home/ployo/data/dataResults/freeProxy/proxies.txt"
        all_proxies = getProxies(proxies_path)
        proxy = rotateProxies(proxies_path , all_proxies , ex_time=3)
        proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
        sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
        sesp.startSelenium()
        rotation = 0
        rotation_top = random.randint(30 , 80)
        for num in num_data :
            time.sleep(0.5)
            url = "http://www.autohome.com.cn/all/" + str(num) + "/#liststart"
            #url = "http://www.autohome.com.cn/all/669/#liststart"
            logger.info(str(pn)+ "\t" +str(url))
            if rotation >= rotation_top :
                proxy = rotateProxies(proxies_path , all_proxies , ex_time=3)
                proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
                sesp.stopSelenium()
                sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
                sesp.startSelenium()
            rotation += 1
            sesp.getWebsite(url)
            page_mh = sesp.getElementsByXpath("//div[contains(@class,\"article-wrapper\")]//li")
            if type(page_mh) != type(list()) :
                continue
            pas = []
            for pa in page_mh :
                pa_html = sesp.getPageSource(browser_or_element=2 , element=pa)
                pas.append(pa_html)
            for pa_html in pas :
                #pa_html = sesp.getPageSource(browser_or_element=2 , element=pa)
                href_rex = "href=\"(.{20,100})\">"
                href_mh = re.findall(re.compile(href_rex) , str(pa_html))
                if 1 != len(href_mh) :
                    continue
                href = str(href_mh[0]).split("#")[0]
                fname_rex = "/(.{1,20})/([0-9]{1,10})/([0-9\-]{1,10}\.html)"
                fname_mh = re.findall(re.compile(fname_rex) , str(href))
                if 1 != len(fname_mh) :
                    logger.info(href)
                    continue
                if 3 != len(fname_mh[0]) :
                    logger.info(href)
                    continue
                fname = fname_mh[0][0] + "_" + fname_mh[0][1] + "_" + fname_mh[0][2]
                rotation += 1
                print(str(pn) + "\t" + str(url) + "\t" + str(href))
                sesp.getWebsite(href)
                time.sleep(1)
                allpage = sesp.getElementByXpath("//section[contains(@class,\"wrapper\")]//article[contains(@class,\"news-details\")]//div[contains(@class,\"page\")]")
                if type(allpage)==type(list()) and 0!=len(allpage):
                    href_split = href.split("/")
                    new_href = ""
                    for i in range(len(href_split)-1) :
                        new_href += href_split[i] + "/"
                    new_href += href_split[-1].split(".") + "-all.html"
                    print("Again: " + str(pn) + "\t" + str(url) + "\t" + str(new_href))
                    sesp.getWebsite(new_href)
                    time.sleep(1)
                pasou = sesp.getPageSource(browser_or_element=1)
                if False == pasou :
                    logger.info("pasou is False")
                    continue
                with open("./dataResults/htmls/"+fname , "w") as f :
                    f.write(pasou)
                break
            break
        sesp.stopSelenium()
            
        

    def run(self) :
        sep_list = []
        data = []
        for i in range(1,1000) :
            data.append(i)
        sep_list = splitList(data , 3)
        multiProcessGo(func=self.getHTML , args_tuple=() , sep_data=sep_list , pn_start=1 , pn_end=4)


if __name__ == "__main__" :
    h = HTMLS()
    h.run()
