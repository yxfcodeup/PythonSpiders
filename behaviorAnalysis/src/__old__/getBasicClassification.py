#_____________________________getBasicClassification.py_____________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : getBasicClassification
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

work_dir = "./"
log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/getBasicClassification.log"
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

class BasicClassification() :
    def __init__(self) :
        self.home_page = "http://www.baiwanzhan.com/"
        self.sleep_wait = 0.5

    def getType(self) :
        url = self.home_page
        s = SeleniumSpider()
        s.startSelenium()
        s.getWebsite(url)
        dbox = s.getElementByXpath("//div[contains(@class,\"main\")]/div[contains(@class,\"dbox2\")]")
        dbox_html = s.getPageSource(2 , dbox)
        s.stopSelenium()

        bs = BS4Spider()
        bs.createSoup(dbox_html)
        tname = bs.matchAll(fname="div" , fattrs={"class":"dbox2_c"})
        for i in range(len(tname)) :
            type_rex = "<a href=\"(.*)\">(.{1,10})</a>"
            type_mh = re.findall(re.compile(type_rex) , str(tname[i]))
            with open("./dataResults/" + str(i+1) + ".txt" , "a") as f :
                for j in range(len(type_mh)) :
                    f.write(str(100*(i+1)+j+1) + "\t" + type_mh[j][1] + "\t" + type_mh[j][0])
                    f.write("\n")


    def getSubType(self):
        s = SeleniumSpider()
        s.startSelenium()
        for i in range(1,7) :
            types = []
            with open("./dataSources/baiwanzhantype/" + str(i) + ".txt" , "r") as f :
                lines = f.readlines()
                for line in lines :
                    types.append(line.replace("\u3000" , "").replace("\n" , "").replace(" " , "").split("\t"))

            stypes = []
            for ty in types :
                number = int(ty[0])
                name = ty[1]
                url = ty[2]
                #s = SeleniumSpider()
                #s.startSelenium()
                logger.info(str(i)+"\t"+str(number)+"\t"+str(name)+"\t"+str(url))
                s.getWebsite(url)
                sub_mh = s.getElementsByXpath("//div[contains(@id,\"dRList\")]//ul/li")
                for si in range(len(sub_mh)) :
                    sub = s.getPageSource(2 , sub_mh[si])
                    rex = "<a href=\"(.*)\">(.{1,10})</a>"
                    mh = re.findall(re.compile(rex) , str(sub))
                    snum = number*100 + si + 1
                    stypes.append(str(snum) + "\t" + mh[0][1] + "\t" + mh[0][0])
                #s.stopSelenium()
            with open("./dataResults/s" + str(i) + ".txt" , "a") as f :
                for st in stypes :
                    f.write(st)
                    f.write("\n")
        s.stopSelenium()



    def getUrls(self , pn) :
        subtypes = []
        with open("./dataSources/baiwanzhantype/baiwanzhanClass.txt" , "r") as f :
            sts = f.readlines()
            for st in sts :
                line = st.replace("\n" , "").split(",")
                if str(pn) == line[0] :
                    subtypes.append(line)
        proxies_path = "/home/ployo/data/dataResults/freeProxy/proxies.txt"
        all_proxies = getProxies(proxies_path)
        proxy = rotateProxies(proxies_path , all_proxies , ex_time=3)
        proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
        sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
        sesp.startSelenium()
        res = {}
        rotation = 0
        rotation_top = random.randint(30 , 80)
        for sty in subtypes :
            #4,社会文化,413,综合网站,http://www.baiwanzhan.com/site/1449/,41306,微信,http://www.baiwanzhan.com/site/1449/1868/
            number = int(sty[5])
            name = sty[6]
            url = sty[7]
            sesp.getWebsite(url)
            pagination_mh  = ""
            failed = True
            for i in range(5) :
                pagination_mh = sesp.getElementByXpath("//div[contains(@class,\"con_other\")]//div[contains(@id,\"dRListBox\")]//div[contains(@class,\"clear\")]")
                if False == pagination_mh :
                    continue
                else :
                    failed = False
                    break
            if failed :
                logger.error("Page load error!")
                with open("./logs/pageLoadError.log" , "a") as f :
                    f.write(str(sty))
                    f.write("\n")
                continue
            pagination_html = sesp.getPageSource(2 , pagination_mh)
            pag_rex = "共([0-9]{1,5})页"
            pag_mh = re.findall(re.compile(pag_rex) , str(pagination_html))
            pagination = int(pag_mh[0])
            nres = []
            for pag in range(1 , pagination+1) :
                time.sleep(self.sleep_wait)
                purl = url + "p" + str(pag)
                logger.info(str(pn)+"\t"+str(number)+"\t"+str(name)+"\t"+str(purl))
                if rotation >= rotation_top :
                    proxy = rotateProxies(proxies_path , all_proxies , ex_time=3) 
                    proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
                    """
                    sesp.stopSelenium()
                    sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
                    sesp.startSelenium()
                    """
                    sesp.restartSelenium(proxy_dict , is_browser_profile=True)
                rotation += 1
                sesp.getWebsite(purl)
                subbox_mh = sesp.getElementsByXpath("//div[contains(@class,\"con_other\")]//div[contains(@id,\"dRListBox\")]//ul")
                if False == subbox_mh :
                    logger.error("subbox match error!")
                    with open("./logs/subboxMatchError.log" , "a") as f :
                        f.write(str(sty + [purl ,]))
                        f.write("\n")
                    continue
                for box in subbox_mh :
                    try :
                        subbox = sesp.getPageSource(2 , box)
                        bs = BS4Spider()
                        bs.createSoup(str(subbox))
                        mh_1 = bs.matchAll(fname="li" , fattrs={"class":"left p-bottom2"})
                        mh_2 = bs.matchOne(fname="li" , fattrs={"class":"right p-bottom2"})
                        mhrex = "<a href=\"(.*)\">(.*)</a>"
                        mh_1_mh = re.findall(re.compile(mhrex) , str(mh_1[1]))
                        mh_2_bs = BS4Spider()
                        mh_2_bs.createSoup(str(mh_2))
                        surl = mh_1_mh[0][0]
                        sname = mh_1_mh[0][1]
                        level = str(mh_2_bs.soup.get_text()).replace("\t" , "").replace("\n" , "").replace(" " , "")
                        if level.isdigit() :
                            nres.append([sname , surl , int(level)])
                        else :
                            nres.append([sname , surl , level])
                    except Exception as e :
                        logger.info(str(e))
                        logger.info("mh_1: " + str(mh_1))
                        logger.info("mh_1_mh: " + str(mh_1_mh))
                        continue
            res[number] = [number , name , url , nres]
            with open("./dataResults/urlLeader.json" , "a") as f :
                f.write(json.dumps({number:[number , name , url , nres]}))
                f.write("\n")
        sesp.stopSelenium()


    def getUrlLeader(self) :
        multiProcessGo(func=self.getUrls , args_tuple=() , sep_data=None , pn_start=1 , pn_end=5)

    def getDomain(self , doleader , pn) :
        proxies_path = "/home/ployo/data/dataResults/freeProxy/proxies.txt"
        #all_proxies = getProxies(proxies_path)
        all_proxies = checkAllProxies(proxies_path)
        proxy = rotateProxies(proxies_path , all_proxies , ex_time=3)
        proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
        sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
        sesp.startSelenium()
        res = []
        rotation = 0
        rotation_top = random.randint(30 , 80)
        for sty in doleader :
            #[11601, '视频短片', '天线视频(高清)网官方网站', 'http://www.openv.com', '\xa066\xa0']
            time.sleep(self.sleep_wait)
            name = sty[2]
            url = sty[3]
            logger.info(str(pn)+"\t"+str(name)+"\t"+str(url))
            if rotation >= rotation_top :
                proxy = rotateProxies(proxies_path , all_proxies , ex_time=3)
                proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
                """
                s.stopSelenium()
                s = SeleniumSpider(proxy_dict , is_browser_profile=True)
                s.startSelenium()
                """
                sesp.restartSelenium(proxy_dict , is_browser_profile=True)
            rotation += 1
            sesp.getWebsite(url)
            pagination_mh = sesp.getElementsByXpath("//div[contains(@class,\"content\")]//table[contains(@id,\"tSiteBox\")]//tbody//tr//td[contains(@class,\"tdContent3\")]")
            if False == pagination_mh :
                with open("./logs/errorSty.log" , "a") as f :
                    f.write(str(sty))
                    f.write("\n")
                continue
            pagination_html = sesp.getPageSource(2 , pagination_mh[0])
            #pagination_html = s.getPageSource(2 , pagination_mh)
            #rex = "href=\"(.*)\">"
            rex = ">[]</a>"
            rex = ">((https|http|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])</a>"
            mh = None
            re_url = ""
            try :
                mh = re.findall(re.compile(rex) , str(pagination_html))
                re_url = mh[0][0]
            except Exception as e :
                logger.error(str(e))
                logger.error(str(mh))
                continue
            sty[3] = re_url
            res.append(sty)
            logger.info(sty)
            with open("./dataResults/resDomain.csv" , "a") as f :
                #f.write("{0},{1},{2},{3},{4},{5},{6}".format(sty[0] , sty[1] , sty[2] , sty[3] , sty[4] , sty[5] , sty[6]))
                f.write(listFormatString(sty , separator=","))
                f.write("\n")
        sesp.stopSelenium()

    def runDomain(self) :
        domain_leaders = []
        with open("./dataResults/urlLeader.json" , "r") as f :
            a = f.readlines()
            for b in a :
                b = json.loads(b)
                for k,v in b.items() :
                    if "5" == str(k)[0] :
                        continue
                    c = [v[0] , v[1]]
                    for sty in v[3] :
                        d = c + sty
                        domain_leaders.append(d)
        sep_list = []
        print(len(domain_leaders))
        sep_list = splitList(data_list=domain_leaders , cpy_num=4)
        #multiProcessGo(func=self.getDomain , args_tuple=() , sep_data=sep_list , pn_start=1 , pn_end=5)

    def run(self) :
        #self.getUrlLeader()
        self.runDomain()

if __name__ == "__main__" :
    b = BasicClassification()
    b.run()
