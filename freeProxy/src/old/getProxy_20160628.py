#_____________________________getProxy.py___________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : getProxy
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-06-27 14:54
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


"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"""
if len(sys.argv) < 3 :
    print("---> Program needs 3 argument.\nExit...")
    print("sys.argv: " + str(sys.argv))
    sys.exit(1)
opts,args = getopt.getopt(sys.argv[1:] , "p:l:s:")
"""
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
work_dir = ""
log_dir = ""
external_settings = ""
for opt,val in opts :
    if "-p" == opt :
        work_dir = str(val) 
    elif "-l" == opt :
        log_dir = str(val)
    elif "-s" == opt :
        external_settings = str(val)
    else :
        print("Arguments error.")
        print("opt: " + str(opt))
        print("val: " + str(val))
        print("Exit...")
        sys.exit(1)


script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
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
                "filename":log_dir , 
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


class getProxy() :
    def __init__(self , spider_info , files_info , pages_info) :
        if "home_page" not in pages_info :
            logger.error("No pages info.\npages_info: " + str(pages_info) + "\nExit...")
            sys.exit(1)
        self.home_page = pages_info["home_page"]

    def checkProxy(self , proxy_ip , proxy_port , url) :
        requests.adapters.DEFAULT_RETRIES = 5
        headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
        proxies_dict = {
                "http":{"http":"http://" + proxy_ip + ":" + proxy_port} , 
                "https":{"https":"https://" + proxy_ip + ":" + proxy_port} , 
                }
        net_type_match = []
        for net_type,proxies in proxies_dict.items() :
            response = None 
            page_html = ""
            try :
                response = requests.get(url , timeout=5 , headers=headers , proxies=proxies)
                page_html = response.text
            except Exception as e :
                logger.error(str(e))
                logger.error(net_type)
                logger.error(proxies)
                logger.error(url)
                continue
            soup = BeautifulSoup(str(page_html) , "lxml")
            div_match = soup.find_all(name="div")
            if len(div_match) < 2:
                logger.error(str(page_html))
            else :
                net_type_match.append(net_type)
        return net_type_match

    def run(self) :
        display = Display(visible=0 , size=(1024,768))
        display.start()
        browser = webdriver.Firefox()
        requests.adapters.DEFAULT_RETRIES = 5
        headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
        is_continue = True
        retries = 0
        page_html = ""
        while is_continue :
            response = None
            try :
                print(self.home_page)
                response = requests.get(self.home_page , timeout=10 , headers=headers)
                page_html = response.text
                if "" != page_html :
                    break
            except Exception as e :
                logger.error(str(e))
                retries += 1
                logger.error("Retry: " + str(retries))
                if 5 < retries :
                    break
                else :
                    time.sleep(5)
                    continue
        soup = BeautifulSoup(str(page_html) , "lxml")
        table_match = soup.find_all(name="tbody")
        table_soup = BeautifulSoup(str(table_match) , "lxml")
        items_match = table_soup.find_all(name="tr")
        proxy_info = []
        print(page_html)
        for item in items_match :
            """
            ip_rex = ">\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</span>"
            port_rex = ">\s*(\d{1,5})\s*</span>"
            used_time_rex = ">\s*(\d{1,3})天\s*</span>"
            ip_match = re.findall(re.compile(ip_rex) , str(item))
            port_match = re.findall(re.compile(port_rex) , str(item))
            used_time_match = re.findall(re.compile(used_time_rex) , str(item))
            if 1==len(ip_match) and 1==len(port_match) and 1==len(used_time_match) :
                proxy_info.append([ip_match[0] , port_match[0] , used_time_match[0]])
            else :
                logger.error("ip_match: " + str(ip_match))
                logger.error("port_match: " + str(port_match))
                logger.error("used_time_match: " + str(used_time_match))
            """
            ip_rex = ">\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>"
            port_rex = ">\s*(\d{1,5})\s*</td>"
            net_type_rex  = ">\s*([A-Z]{1,10})\s*</td>"
            response_time_rex = ">([0-9]{0,1}\.{0,1}[0-9]{0,1})秒</td>"
            ip_match = re.findall(re.compile(ip_rex) , str(item))
            port_match = re.findall(re.compile(port_rex) , str(item))
            net_type_match = re.findall(re.compile(net_type_rex) , str(item))
            response_time_match = re.findall(re.compile(response_time_rex) , str(item))
            print(ip_match)
            print(port_match)
            print(net_type_match)
            print(response_time_match)
        sys.exit(1)
        proxy_info = sorted(proxy_info , key=lambda info:int(info[2]) , reverse=True)
        check_target_url = [
                "https://www.baidu.com/" , 
                "http://www.jd.com/" , 
                "https://www.zhihu.com/" , 
                "http://www.bilibili.com/" , 
                "https://www.taobao.com/" , 
                ]
        urls_match_proxies = {}
        for url in check_target_url :
            url = "http://www.jd.com/"
            url_matches_proxies = []
            for pinfo in proxy_info :
                net_types = self.checkProxy(pinfo[0] , pinfo[1] , url)
                if 1 == len(net_types) :
                    url_matches_proxies.append([net_types[0] , pinfo[0] , pinfo[1]])
                elif 2 == len(net_types) :
                    url_matches_proxies.append([net_types[0] , net_types[1] , pinfo[0] , pinfo[1]])
                else :
                    logger.error("No proxies matched.")
                    continue
            urls_match_proxies[url] = url_matches_proxies
        for url,proxies in urls_match_proxies.items() :
            print(url)
            for p in proxies :
                print("\t\t" + str(p))




if __name__ == "__main__" :
    spi = {}    #spider_info
    fin = {}    #files_info
    pai = {}    #pages_info
    pai["home_page"] = "http://www.kuaidaili.com/free/inha/"

    g = getProxy(spi , fin , pai)
    g.run()
