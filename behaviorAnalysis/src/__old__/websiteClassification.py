#_____________________________websiteClassification.py______________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : websiteClassification
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-07-25 14:00
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
import jieba
import numpy as np
import matplotlib as mpl

#Cumtomize Moduls
import settings
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
#import tools

work_dir = "./"
log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/spider.log"
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

class HostCnt() :
    def __init__(self , file_path) :
        self.file_path = file_path
        self.url_dict = {}
        self.url_list = []
        self.hurl_dict = {}
        self.hurl_list = []

    def run(self) :
        hostcnt = None
        with open(self.file_path , "rb") as f :
            hostcnt = pickle.load(f)
        for line in hostcnt :
            url = line[0]
            url_num = line[1]
            if type(url_num)==type(int()) or str(url_num).isdigit() :
                url_num = int(url_num)
            else :
                url_num = 1
            if "" == url :
                continue
            self.url_dict[url] = url_num
            hurl = ""
            rex_1 = "(f|ht){1}(tp|tps){1}(:\/\/)([0-9a-zA-Z\-\.]*)(\/){0,1}"
            rex_2 = "([0-9a-zA-Z\-\.]*)(\/){0,1}"
            url_mh_1 = re.findall(re.compile(rex_1) , url)
            url_mh_2 = re.findall(re.compile(rex_2) , url)
            if 0 != len(url_mh_1) :
                if 0 != len(url_mh_1[0]) :
                    for um in url_mh_1[0] :
                        if "/" == um :
                            break
                        hurl += um
            elif 0 != len(url_mh_2) :
                if 0 != len(url_mh_2[0]) :
                    for um in url_mh_2[0] :
                        if "/" == um :
                            break
                        hurl += um
            else :
                continue
            if hurl in self.hurl_dict :
                self.hurl_dict[hurl] = self.hurl_dict[hurl] + url_num
            else :
                self.hurl_dict[hurl] = url_num
        self.url_list = sorted(self.url_dict.items() , key=itemgetter(1) , reverse=True)
        self.hurl_list = sorted(self.hurl_dict.items() , key=itemgetter(1) , reverse=True)


class WebsiteClassification() :
    def __init__(self , url_list) :
        self.res_texts = []
        self.urls = url_list
        self.classification_tree = {}
        self.classification_dict = {}


    def getInfo(self , url) :
        requests.adapters.DEFAULT_RETRIES = 5
        headers = {
                "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0" , 
                #"User-Agent":"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36" ,
                }
        page_html = ""
        try :
            response = requests.get(url , timeout=10 , headers=headers)
            page_html = response.content
        except Exception as e :
            logger.error(str(e))
            return False
        #soup = BeautifulSoup(str(page_html).lower() , "lxml")
        #title = soup.head.title.get_text()
        #if None==soup.head or ""==soup.head :
        #    return False
        try :
            code_type_rex = "<meta.{0,500}charset=[\'\"]{0,1}(utf-8|utf8|gb2312|gb-2312|big5|big-5|ansi)[\'\"]{0,1}"
            code_type_mh = re.findall(re.compile(code_type_rex) , str(page_html).lower())
            code_type = "utf-8"
            if len(code_type_mh) >= 1:
                code_type = code_type_mh[0]
            response.encoding = code_type
            page_html = response.text
            #page_html = page_html.decode(code_type)
            soup = BeautifulSoup(str(page_html).lower() , "lxml")
            title_match = soup.find_all(name="title")
            keywords_match = soup.find_all(name="meta" , attrs={"name":"keywords"})
            desc_match = soup.find_all(name="meta" , attrs={"name":"description"})
            title = ""
            keywords = ""
            desc = ""
            if 1 == len(title_match) :
                title_match = re.findall(re.compile("<title>(.*)</title>") , str(title_match[0]))
                if 1 == len(title_match) :
                    title = title_match[0]
            if 1 == len(keywords_match) :
                keywords_match = re.findall(re.compile("<.*content=\"([^\"]*)\".*>") , str(keywords_match[0]))
                if 1 == len(keywords_match) :
                    keywords = keywords_match[0]
            if 1 == len(desc_match) :
                desc_match = re.findall(re.compile("<.*content=\"([^\"]*)\".*>") , str(desc_match[0]))
                if 1 == len(desc_match) :
                    desc = desc_match[0]
        except Exception as e :
            logger.error(str(e))
            return False
        #print(title , "\n" , keywords , "\n" , desc)
        res = []
        if ""!=title and None!=title:
            res.append(title)
        if ""!=keywords and None!=keywords:
            res.append(keywords)
        if ""!=desc and None!=desc:
            res.append(desc)
        if 0 == len(res) :
            return False
        return res

    def getJson(self) :
        classification_base = []
        with open("./classification_base.json" , "r") as f :
            classification_base = f.readlines()
        for cb in classification_base :
            for k,v in json.loads(cb).items() :
                self.classification_tree[k] = v
                names = []
                for name,num in v[1].items() :
                    #names.append(name)
                    self.classification_dict[name] = num
                #self.classification_dict[k] = names
        print(self.classification_dict)

    def splitInfo(self , input_str) :
        seg_list = jieba.cut(input_str)
        res = []
        for s in seg_list :
            smatch = re.findall(re.compile("([0-9a-zA-Z\u4e00-\u9fa5]+)") , s)
            if 0 != smatch :
                res += smatch
        return res

    def run(self) :
        dsource_path = "/home/ployo/workspace/pythonCodes/xdrProject/dataSources/dir001" 
        d_files = os.listdir(dsource_path)
        source_files = {} #{name:website_list}
        for dfile in d_files :
            f_path = dsource_path + "/" + dfile
            with open(f_path , "r") as f :
                source_files[dfile] = json.loads((f.readlines())[0])
        for fname , url_list in source_files.items() :
            sto_dict = {}
            for url in url_list :
                #url = "www.sportscn.com"
                if "https://" not in url or "http://" not in url :
                    url = "http://" + url
                #url = "http://www.51bestfood.com/"
                res = self.getInfo(url)
                if False != res :
                    sto_dict[url] = res
                with open("/home/ployo/workspace/pythonCodes/xdrProject/dataResults/dir001/"+str(fname) , "a") as f :
                    f.write(json.dumps({url:res}))
                    f.write("\n")
        """
        self.getJson()
        hostcnt_path = "./hostcnt"
        hostcnt = HostCnt(hostcnt_path)
        hostcnt.run()
        for line in hostcnt.hurl_list :
            url = line[0]
            sn = line[1]
            res = self.getInfo(url)
            time.sleep(0.5)
            if False == res :
                continue
            words = []
            for rstr in res :
                words += self.splitInfo(rstr)
            print(url)
            print(words)
            with open("./webwords.json" , "a") as f :
                f.write(json.dumps({url:[sn , words]}))
                f.write("\n")
            classification_list = []
            for name,num in self.classification_dict.items() :
                classification_list.append(name)
            #b = Bayes(classification_list , words)
            #b.run()
        """



if __name__ == "__main__" :
    url_list = ["http://bbs.yikao88.com/front/topic/topicInfor/12" , "http://gou.jd.com/exp4?cu=true&utm_source=vip.baidu.com&utm_medium=tuiguang&utm_campaign=t_298046589_&utm_term=e9fab82f73104371b4fb2102f9559305" , "https://www.jd.com/"]
    w = WebsiteClassification(url_list)
    w.run()
