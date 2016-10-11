#_____________________________getClassification.py__________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : getClassification
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
from seleniumSpider import *
from bs4Spider import *
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
import tools

work_dir = "./"
log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/geturls.log"
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


class getClassification() :
    def __init__(self) :
        pass

    def getType(self) :
        url = "http://www.baiwanzhan.com/"
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
        proxies_path = "/home/ployo/data/dataResults/freeProxy/proxies.txt"
        all_proxies = tools.getProxies(proxies_path)
        subtypes = []
        with open("./dataSources/baiwanzhantype/s" + str(pn) + ".txt" , "r") as f :
            sts = f.readlines()
            for st in sts :
                subtypes.append((st.replace("\n" , "").split("\t")))
        proxy = tools.rotateProxies(proxies_path , all_proxies , ex_time=3)
        proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
        s = SeleniumSpider(proxy_dict , is_browser_profile=True)
        s.startSelenium()
        res = {}
        rotation = 0
        rotation_top = random.randint(30 , 80)
        for sty in subtypes :
            number = int(sty[0])
            name = sty[1]
            url = sty[2]
            s.getWebsite(url)
            pagination_mh = s.getElementByXpath("//div[contains(@class,\"con_other\")]//div[contains(@id,\"dRListBox\")]//div[contains(@class,\"clear\")]")
            if False == pagination_mh :
                continue
            pagination_html = s.getPageSource(2 , pagination_mh)
            pag_rex = "共([0-9]{1,5})页"
            pag_mh = re.findall(re.compile(pag_rex) , str(pagination_html))
            pagination = int(pag_mh[0])
            nres = []
            for pag in range(1 , pagination+1) :
                time.sleep(1)
                purl = url + "p" + str(pag)
                logger.info(str(pn)+"\t"+str(number)+"\t"+str(name)+"\t"+str(purl))
                if rotation >= rotation_top :
                    proxy = tools.rotateProxies(proxies_path , all_proxies , ex_time=3) 
                    proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
                    s.stopSelenium()
                    s = SeleniumSpider(proxy_dict , is_browser_profile=True)
                    s.startSelenium()
                rotation += 1
                s.getWebsite(purl)
                subbox_mh = s.getElementsByXpath("//div[contains(@class,\"con_other\")]//div[contains(@id,\"dRListBox\")]//ul")
                if False == subbox_mh :
                    continue
                for box in subbox_mh :
                    try :
                        subbox = s.getPageSource(2 , box)
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
            with open("./dataResults/w" + str(pn) + ".json" , "a") as f :
                f.write(json.dumps({number:[number , name , url , nres]}))
                f.write("\n")
        s.stopSelenium()
        


    def runBaiwanzhan(self) :
        process_dict = {}
        for i in range(1,7) :
            process_dict[i] = multiprocessing.Process(target=self.getUrls , args=(i , ))
        for pn,p in process_dict.items() :
            p.daemon = True
            p.start()
        for pn,p in process_dict.items() :
            p.join()

    def getDomain(self , doleader , pn) : 
        proxies_path = "/home/ployo/data/dataResults/freeProxy/proxies.txt"
        all_proxies = tools.getProxies(proxies_path)
        proxy = tools.rotateProxies(proxies_path , all_proxies , ex_time=3)
        proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
        s = SeleniumSpider(proxy_dict , is_browser_profile=True)
        s.startSelenium()
        res = []
        rotation = 0
        rotation_top = random.randint(30 , 80)
        for sty in doleader :
            #101,音乐,10101,在线听歌,http://www.baiwanzhan.com/site/t160640/,追梦音乐网,66
            time.sleep(0.5)
            name = sty[5]
            url = sty[4]
            logger.info(str(pn)+"\t"+str(name)+"\t"+str(url))
            if rotation >= rotation_top :
                proxy = tools.rotateProxies(proxies_path , all_proxies , ex_time=3)
                proxy_dict = {"nettype":proxy[0] , "ip":proxy[1] , "port":proxy[2]}
                s.stopSelenium()
                s = SeleniumSpider(proxy_dict , is_browser_profile=True)
                s.startSelenium()
            rotation += 1
            s.getWebsite(url)
            pagination_mh = s.getElementsByXpath("//div[contains(@class,\"content\")]//table[contains(@id,\"tSiteBox\")]//tbody//tr//td[contains(@class,\"tdContent3\")]")
            name = sty[1]
            if False == pagination_mh :
                continue
            pagination_html = s.getPageSource(2 , pagination_mh[0])
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
            sty[4] = re_url
            res.append(sty)
            logger.info(sty)
            with open("./res2.csv" , "a") as f :
                f.write("{0},{1},{2},{3},{4},{5},{6}".format(sty[0] , sty[1] , sty[2] , sty[3] , sty[4] , sty[5] , sty[6]))
                f.write("\n")
        s.stopSelenium()

    def runDomain(self) :
        domain_leaders = []
        with open("./dataSources/baiwanzhantype/res.csv" , "r") as f :
            a = f.readlines()
            for b in a :
                c = b.replace("\n" , "").split(",")
                domain_leaders.append(c)
        process_dict = {}
        for i in range(1,7) :
            doleader = []
            for d in domain_leaders :
                if str(i) == d[0][0] :
                    doleader.append(d)
            process_dict[i] = multiprocessing.Process(target=self.getDomain , args=(doleader , i))
        for pn,p in process_dict.items() :
            p.daemon = True
            p.start()
        for pn,p in process_dict.items() :
            p.join()

    def runDomain(self) :
        domain_leaders = []
        with open("./dataSources/baiwanzhantype/res.csv" , "r") as f :
            a = f.readlines()
            for b in a :
                c = b.replace("\n" , "").split(",")
                domain_leaders.append(c)
        sep_list = []
        for i in range(1 , 7) :
            doleader = []
            for d in domain_leaders :
                if str(i) == d[0][0] :
                    doleader.append(d)
            sep_list.append(doleader)
        tools.multiProcessGo(func=self.getDomain , args_tuple=() , sep_data=sep_list , pn_start=1 , pn_end=7)



    def run(self) :
        #self.getType()
        #self.getSubType()
        self.runBaiwanzhan()
        #self.runDomain()


if __name__ == "__main__" :
    g = getClassification()
    g.run()
