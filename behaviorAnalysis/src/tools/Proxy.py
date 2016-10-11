import os
import sys
import re
import time
import inspect
import datetime
import multiprocessing
import getopt
import shutil
import tempfile
import random
import json
import math
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

"""
# get proxies from proxies file
# @ string file_path : proxies file storing path
"""
def getProxies(file_path) :
    if not os.path.exists(file_path) :
        print("getProxies() ERROR: the file path(" + str(file_path) + ") do not exist.")
        return False 
    all_proxies = []
    with open(file_path , "r") as f :
        proxies_list = f.readlines()
        for p in proxies_list :
            p = p.replace("\n" , "").split(";")
            if 3 == len(p) :
                all_proxies.append(p)
    return all_proxies

def diffDatetime(dt_a , dt_b , res_type=1) :
    dt_now = datetime.datetime.now()
    if type(dt_now)!=type(dt_a) or type(dt_now)!=type(dt_b) :
        print("diffDatetime() ERROR: dt_a and dt_b must be <class 'datetime.datetime'>.")
        return False
    diff_dt = dt_b - dt_a
    diff_sec = diff_dt.total_seconds()
    if 1 == res_type :
        return diff_sec
    elif 2 == res_type :
        return diff_sec / 60.0
    elif 3 == res_type :
        return diff_sec / 3600.0
    else :
        print("diffDatetime() ERROR: res_type must be 1/2/3.")
        return False


def diffProxies(file_path , all_proxies) :
    if not os.path.exists(file_path) :
        print("proxiesMonitor() ERROR: the file path(" + str(file_path) + ") do not exist.")
        return False
    file_proxies = getProxies(file_path)
    if len(all_proxies) != len(file_proxies) :
        return False
    for p in file_proxies :
        if p not in all_proxies :
            return False
    return True


"""
# get a proxy randomly
# @ string file_path : proxies file storing path
# @ list all_proxies : a list of all proxies
# @ int ex_time : if now time equal to the ex_time,get proxies from proxies file again
"""
#def rotateProxies(file_path , all_proxies , ex_time=None) :
#pre_time,now_time:datetime.datetime.now()
#diff_time is some minutes
def rotateProxies(file_path , all_proxies , pre_time , now_time , diff_time) :
    if not os.path.exists(file_path) :
        print("getProxies() ERROR: the file path(" + str(file_path) + ") do not exist.")
        return False 
    """
    exchange_time = datetime.datetime.now().hour
    if ex_time == exchange_time :
        all_proxies = getProxies(file_path)
    """
    dt = diffDatetime(pre_time , now_time , res_type=2)
    if type(dt)==type(float()) and dt>=diff_time:
        all_proxies = getProxies(file_path)
    proxy = None
    if len(all_proxies) > 0 :
        proxy_label = random.randint(0 , len(all_proxies)-1)
        proxy = all_proxies[proxy_label]
    else :
        proxy = ["" , "" , ""]
    return proxy


#proxy:["http" , "202.43.147.226" , "3128"]
def checkProxy(proxy , check_target="https://www.baidu.com" , selenium_or_requests=1) :
    if 1 == selenium_or_requests :
        try :
            display = Display(visible=0 , size=(1024,768))
            display.start()
            browser_profile = webdriver.FirefoxProfile()
            browser_profile.set_preference("network.proxy.type" , 2)
            proxy_url = proxy[0] + "://" + proxy[1] + ":" + proxy[2]
            browser_profile.set_preference("network.proxy.autoconfig_url" , proxy_url)
            browser_profile.update_preferences()
            browser = webdriver.Firefox(firefox_profile=browser_profile)
        except Exception as e :
            print("checkProxy() ERROR: " + str(e))
            print("checkProxy() ERROR: browser profile is error!")
            return False
        #get url
        page_html = ""
        try :
            browser.get(check_target)
            browser.implicitly_wait(30)
            page_html = browser.page_source
        except Exception as e :
            print("checkProxy() ERROR: get url error.")
            return False
        browser.quit()
        display.stop()
        div_rex = "<div"
        div_mh = re.findall(re.compile(div_rex) , str(page_html))
        if len(div_mh) < 5 :
            print("checkProxy WARNING: This proxy(" + str(proxy) + ") is error.")
            return False
        else :
            return True
    elif 2 == selenium_or_requests :
        requests.adapters.DEFAULT_RETRIES = 5
        headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
        if 3 != len(proxy) :
            print("checkProxy() ERROR: proxy is error(" + str(proxy) + ").")
        proxies = proxy[0] + "://" + proxy[1] + ":" + proxy[2]
        response = None
        page_html = ""
        try :
            response = requests.get(check_target , timeout=5 , headers=headers , proxies=proxies)
            page_html = response.text
        except Exception as e :
            print("checkProxy() ERROR: " + str(e))
            print("proxy: " + str(proxy))
            return False 
        div_rex = "<div"
        div_mh = re.findall(re.compile(div_rex) , str(page_html))
        if len(div_mh) < 5 :
            print("checkProxy WARNING: This proxy(" + str(proxy) + ") is error.")
            return False
        else :
            return True
    else :
        print("checkProxy() ERROR: selenium_or_requests must be 1 or 2.")
        return False


def checkAllProxies(file_path , ex_time=3) :
    if not os.path.exists(file_path) :
        print("getProxies() ERROR: the file path(" + str(file_path) + ") do not exist.")
        return False 
    all_proxies = getProxies(file_path)
    exchange_time = datetime.datetime.now().hour
    if exchange_time>=0 and exchange_time<=ex_time :
        print("checkAllProxies() WARNING: There is new proxies input.")
        return True
    usable_proxies = []
    for proxy in all_proxies :
        print("checkAllProxies() INFO:\t" + str(proxy))
        usable = checkProxy(proxy)
        if usable :
            print("checkAllProxies() INFO:\tSuccess!")
            usable_proxies.append(proxy)
    with open(file_path , "w") as f :
        f.write("")
    with open(file_path , "a") as f :
        for proxy in usable_proxies :
            f.write(str(proxy[0] + ";" + str(proxy[1] + ";" + str(proxy[2]) + "\n")))
    return usable_proxies


if __name__ == "__main__" :
    pa = "/home/ployo/data/dataResults/freeProxy/proxies.txt"
    print(getProxies(pa))
