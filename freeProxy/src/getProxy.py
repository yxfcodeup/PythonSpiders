#_____________________________getProxy.py___________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : getProxy
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-25 16:23
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


"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"""
if len(sys.argv) < 4 :
    print("---> Program needs 3 argument.\nExit...")
    print("sys.argv: " + str(sys.argv))
    sys.exit(1)
opts,args = getopt.getopt(sys.argv[1:] , "p:h:o:n:")
"""
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
work_dir = ""
log_dir = ""
external_settings = ""
redis_host = ""
redis_port = ""
redis_db = ""
for opt,val in opts :
    if "-p" == opt :
        work_dir = str(val) 
    elif "-h" == opt :
        redis_host = str(val)
    elif "-o" == opt :
        redis_port = str(val)
    elif "-n" == opt :
        redis_db = str(val)
    else :
        print("Arguments error.")
        print("opt: " + str(opt))
        print("val: " + str(val))
        print("Exit...")
        sys.exit(1)

src_path = work_dir + "/src"
tools_path = src_path + "/tools"
sys.path.append(src_path)
sys.path.append(tools_path)
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

#work_dir = "./"
log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/getProxy.log"
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

class ProxySpider() :
    def __init__(self) :
        wd_list = work_dir.split("/")
        self.storing_path = "/" + wd_list[1] + "/" + wd_list[2] + "/data/dataResults/freeProxy"
        self.home_page = "http://www.kuaidaili.com/free/inha/"
        self.proxies_dict = {}
        self.proxies_list = []
        self.redis_pool = None
        self.redisdb = None

    def getProxy(self) :
        sesp = SeleniumSpider()
        sesp.startSelenium()
        reading_proxies = None
        with open(self.storing_path+"/proxies.json" , "r") as f :
            reading_proxies = f.readlines()
        if 1 == len(reading_proxies) :
            self.proxies_dict = json.loads(reading_proxies[0])
        page_num = 100
        for i in range(page_num) :
            time.sleep(2)
            i += 1
            url = self.home_page + str(i)
            logger.info(url)
            sesp.getWebsite(url)
            peles = sesp.getElementsByXpath("//div[contains(@id,\"list\")]//table//tbody//tr")
            for ele in peles :
                phtml = sesp.getPageSource(browser_or_element=2 , element=ele)
                ip_rex = ">\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>"
                port_rex = ">\s*(\d{1,5})\s*</td>"
                net_type_rex = ">\s*([A-Z]{1,10})\s*</td>"
                retime_rex = ">([0-9]{0,1}\.{0,1}[0-9]{0,1})秒</td>"
                ip_mh = re.findall(re.compile(ip_rex) , str(phtml))
                port_mh = re.findall(re.compile(port_rex) , str(phtml))
                net_type_mh = re.findall(re.compile(net_type_rex) , str(phtml))
                retime_mh = re.findall(re.compile(retime_rex) , str(phtml))
                if 1==len(ip_mh) and 1==len(port_mh) and 1==len(net_type_mh) and 1==len(retime_mh) :
                    if isnumber(retime_mh[0].replace(" " , "")) and float(retime_mh[0])<=2.0 :
                        self.proxies_dict[ip_mh[0]] = [port_mh[0] , net_type_mh[0]]
        sesp.stopSelenium()

    def initRedis(self , in_host , in_port  , in_db_num) :
        host_rex = "([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})"
        host_mh = re.findall(re.compile(host_rex) , in_host)
        if 1 != len(host_mh) :
            print("dataToRedis() ERROR: host is error!\nExit...")
            sys.exit(1)
        if not in_port.isdigit() :
            print("dataToRedis() ERROR: port is error!\nExit...")
            sys.exit(1)
        if not in_db_num.isdigit() :
            print("dataToRedis() ERROR: db num is error!\nExit...")
            sys.exit(1)
        try :
            self.redis_pool = redis.ConnectionPool(host=in_host , port=in_port , db=in_db_num)
            self.redisdb = redis.StrictRedis(connection_pool=self.redis_pool)
        except Exception as e :
            print("dataToRedis() ERROR: " + str(e))
            print("Exit...")
            sys.exit(1)
    

    def dataToRedis(self) :
        for k,v in self.proxies_dict.items() :
            ip = k
            port = v[0]
            ntt = v[1]
            self.redisdb.hset(ip , "ip" , ip)
            self.redisdb.hset(ip , "ntt" , ntt.lower())
            self.redisdb.hset(ip , "port" , port)
            self.redisdb.hset(ip , "success" , "0")
            self.redisdb.hset(ip , "failed" , "0")
            self.redisdb.hset(ip , "usable" , "0")

    def getDataFromRedis(self) :
        res = []
        keys = self.redisdb.keys(pattern="*")
        for k in keys :
            r = []
            k = k.decode("utf-8")
            ip_rex = "(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            ip_mh = re.findall(re.compile(ip_rex) , str(k))
            if 1 != len(ip_mh) :
                self.redisdb.delete(k)
                logger.error(k + " is not proxy.")
                continue
            r.append(self.redisdb.hget(k , "ip").decode("utf-8"))
            r.append(self.redisdb.hget(k , "ntt").decode("utf-8"))
            r.append(self.redisdb.hget(k , "port").decode("utf-8"))
            r.append(self.redisdb.hget(k , "success").decode("utf-8"))
            r.append(self.redisdb.hget(k , "failed").decode("utf-8"))
            r.append(self.redisdb.hget(k , "usable").decode("utf-8"))
            res.append(r)
        return res

    def checkPingShell(self) :
        #ping.sh
        #> PING=`ping -c $1 $2`
        #> echo $PING
        try :
            shell_path = work_dir + "/sh"
            ping_shell = work_dir + "/sh/ping.sh"
            if not os.path.exists(shell_path) :
                print("ping() WARNING: " + shell_path + " do not exists!")
                os.mkdir(shell_path)
            if not os.path.exists(ping_shell) :
                print("ping() WARNING: " + ping_shell + " do not exists!")
                os.system("echo '#/bin/bash' >> ./sh/ping.sh")
                os.system("echo 'PING=`ping -c $1 $2`' >> ./sh/ping.sh")
                os.system("echo 'echo $PING' >> ./sh/ping.sh")
                os.system("chmod 755 ./sh/ping.sh")
        except Exception as e :
            return False
        return True

    def ping(self , url , times=10) :
        def isnumber(nstr) :
            if type(nstr) != type(str()) :
                print("isnumber(): " + str(nstr) + " is not string!Cannot judge it!")
                return False
            num_str = ""
            num_dot = 0
            for i in range(len(nstr)) :
                ns = nstr[i]
                if 0==i and ("0"==ns or "."==ns) :
                    return False
                if "0"!=ns and "1"!=ns and "2"!=ns and "3"!=ns and "4"!=ns and "5"!=ns\
                        and "6"!=ns and "7"!=ns and "8"!=ns and "9"!=ns and "."!=ns :
                    return False
                if "." == ns :
                    num_dot += 1
            if num_dot > 1 :
                return False
            return True

        #ping.sh
        #> PING=`ping -c $1 $2`
        #> echo $PING
        shell_path = work_dir + "/sh"
        ping_shell = work_dir + "/sh/ping.sh"
        if not os.path.exists(shell_path) :
            print("ping() WARNING: " + shell_path + " do not exists!")
            os.mkdir(shell_path)
        if not os.path.exists(ping_shell) :
            print("ping() WARNING: " + ping_shell + " do not exists!")
            os.system("echo '#/bin/bash' >> ./sh/ping.sh")
            os.system("echo 'PING=`ping -c $1 $2`' >> ./sh/ping.sh")
            os.system("echo 'echo $PING' >> ./sh/ping.sh")
            os.system("chmod 755 ./sh/ping.sh")
        print(ping_shell + " " + str(times) + " " + str(url))
        res = os.popen(ping_shell + " " + str(times) + " " + str(url)).read()
        min_avg_max_mdev_rex = "min/avg/max/mdev = ([\d\.]{1,10}/[\d\.]{1,10}/[\d\.]{1,10}/[\d\.]{1,10}) ms"
        pac_loss_rex = "([\d\.]{1,5})% packet loss"
        min_avg_max_mdev_mh = re.findall(re.compile(min_avg_max_mdev_rex) , str(res))
        pac_loss_mh = re.findall(re.compile(pac_loss_rex) , str(res))
        if 1 != len(min_avg_max_mdev_mh) :
            print("ping() ERROR!")
            print("ping() ERROR DETAILS:\n" + str(res))
            return False
        if 1 != len(pac_loss_mh) :
            print("ping() ERROR!")
            print("ping() ERROR DETAILS:\n" + str(res))
            return False
        min_avg_max_mdev = str(min_avg_max_mdev_mh[0]).split("/")
        avg_time = min_avg_max_mdev[1]
        pac_loss = pac_loss_mh[0]
        if isnumber(str(avg_time)) :
            avg_time = float(avg_time)
        if isnumber(str(pac_loss)) :
            pac_loss = float(pac_loss)
        return [avg_time , pac_loss]


    def checkPing(self , proxies_list , pn) :
        usable_list = []
        i = 0
        plen = len(proxies_list)
        for proxy in proxies_list :
            i += 1
            logger.info("Process[" + str(pn) + "]: ping " + str(i) + "/" + str(plen))
            pr = self.ping(proxy[0] , times=1)
            if type(pr)!=type(list()) or 2!=len(pr) :
                continue
            if int(pr[0])<=200 and '0'==pr[1]:
                usable_list.append(proxy)
            else :
                suc_time = int(proxy[3])
                failed_time = int(proxy[4]) + 1
                if failed_time-suc_time > 5 :
                    self.redisdb.delete(proxy[0])
                    logger.error(str(proxy) + " is deleted!")
                else :
                    self.redisdb.hset(proxy[0] , "failed" , str(failed_time))
                    self.redisdb.hset(proxy[0] , "usable" , "0")
                    logger.error(str(proxy) + " is failed again!")
        return usable_list

    """
    self.redisdb.hset(ip , "ip" , ip)
    self.redisdb.hset(ip , "ntt" , ntt.lower())
    self.redisdb.hset(ip , "port" , port)
    self.redisdb.hset(ip , "success" , "0")
    self.redisdb.hset(ip , "failed" , "0")
    self.redisdb.hset(ip , "usable" , "0")
    """
    def checkSelenium(self , proxy , check_target_urls) :
        #['39.184.132.11', 'http', '80', '0', '0', '0']
        try :
            browser_profile = webdriver.FirefoxProfile()
            browser_profile.set_preference("network.proxy.type" , 2)
            proxy_url = str(proxy[1]) + "://" + str(proxy[0]) + ":" + str(proxy[2])
            browser_profile.set_preference("network.proxy.autoconfig_url" , proxy_url)
            browser_profile.update_preferences()
            browser = webdriver.Firefox(firefox_profile=browser_profile)
        except Exception as e :
            logger.error("checkSelenium() ERROR: " + str(e))
            return False
        try :
            browser.get(check_target_urls)
            browser.implicitly_wait(10)
            page_html = browser.page_source
            if "百度一下，你就知道" not in str(page_html) :
                browser.quit()
                logger.error("There is not \"百度一下，你就知道\"")
                return False
            if "京ICP证030173号" not in str(page_html) :
                browser.quit()
                logger.error("There is not \"京ICP证030173号\"")
                return False
            soup = BeautifulSoup(str(page_html) , "lxml")
            div_match = soup.find_all(name="div")
            if len(div_match) < 5 :
                browser.quit()
                logger.error("There is less than 5 div.")
                return False
        except Exception as e :
            browser.quit()
            logger.error("checkSelenium() ERROR: " + str(e))
            return False
        browser.quit()
        return True

    def checkRequests(self , proxy , check_target_urls) :
        requests.adapters.DEFAULT_RETRIES = 5
        headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
        proxy = {proxy[1]:str(proxy[1]) + "://" + str(proxy[0]) + ":" + str(proxy[2])}
        response = None
        page_html = ""
        try :
            response = requests.get(check_target_urls , timeout=5 , headers=headers , proxies=proxy)
            page_html = response.content.decode("utf-8")
            if "百度一下，你就知道" not in str(page_html) :
                logger.error("There is not \"百度一下，你就知道\"")
                return False
            if "京ICP证030173号" not in str(page_html) :
                logger.error("There is not \"京ICP证030173号\"")
                return False
            soup = BeautifulSoup(str(page_html) , "lxml")
            div_match = soup.find_all(name="div")
            if len(div_match) < 5 :
                logger.error("There is less than 5 div.")
                return False
        except Exception as e :
            logger.error("checkRequests() ERROR: " + str(e))
            return False
        return True


    def checkProxy(self , proxies_list , pn) :
        check_target_urls = "https://www.baidu.com/" 
        proxies_list = self.checkPing(proxies_list , pn)
        usable_proxies = []
        display = Display(visible=0 , size=(1920,1080))
        display.start()
        i = 0
        plen = len(proxies_list)
        for proxy in proxies_list :
            i += 1
            logger.info("Process[" + str(pn) + "](" + str(i) + "/" + str(plen) + "): " + str(proxy))
            cs = self.checkSelenium(proxy , check_target_urls)
            cr = self.checkRequests(proxy , check_target_urls)
            suc_time = int(proxy[3])
            failed_time = int(proxy[4])
            if cs and cr :
                self.redisdb.hset(proxy[0] , "success" , str(suc_time+1))
                self.redisdb.hset(proxy[0] , "usable" , "1")
            else :
                if failed_time-suc_time >= 5 :
                    self.redisdb.delete(proxy[0])
                else :
                    self.redisdb.hset(proxy[0] , "failed" , str(failed_time+1))
                    self.redisdb.hset(proxy[0] , "usable" , "0")
        display.stop()

    def update(self) :
        redis_proxies = self.getDataFromRedis()
        proxies_list = redis_proxies
        p_num = 6
        sep_list = []
        step = int(len(proxies_list)/p_num+1)
        start = 0
        end = step
        for i in range(p_num) :
            if i != p_num-1 :
                sep_list.append(proxies_list[start:end])
                start += step
                end += step
            else :
                sep_list.append(proxies_list[start:])
        process_dict = {}
        for pn in range(1 , p_num+1) :
            process_dict[pn] = multiprocessing.Process(target=self.checkProxy , args=(sep_list[pn-1] , pn))
        for pn,p in process_dict.items() :
            p.daemon = True
            p.start()
        for pn,p in process_dict.items() :
            p.join()

    def run(self) :
        is_suc = self.checkPingShell()
        if is_suc :
            self.initRedis(redis_host , redis_port , redis_db)
            if 0 == len(self.redisdb.keys(pattern="*")) :
                self.getProxy()
                self.dataToRedis()
                self.update()
            else :
                self.update()
        else :
            logger.error("run() ERROR: checkPingShell() returns False!")


if __name__ == "__main__" :
    p = ProxySpider()
    p.run()
