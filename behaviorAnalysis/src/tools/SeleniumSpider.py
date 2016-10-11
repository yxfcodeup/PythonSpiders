#_____________________________seleniumSpider.py_____________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : seleniumSpider
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-11 10:01
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
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.wait import *



class SeleniumSpider() :
    def __init__(self , proxy_dict=None , is_browser_profile=False) :
        self.display = None
        self.browser = None
        self.is_browser_profile = False
        self.proxy_type = 2
        #self.proxy_dict = {"nettype":"http" , "ip":"211.100.29.195" , "port":"82"}
        self.proxy_dict = None
        if is_browser_profile :
            self.is_browser_profile = is_browser_profile
            if type(proxy_dict)!=type(dict()) or 3!=len(proxy_dict) :
                print("seleniumSpider init ERROR: proxy_dict error,please check it(" + str(proxy_dict) + ")!")
                print("Exit...")
                sys.exit(1)
            else :
                if "http"!=proxy_dict["nettype"] and "https"!=proxy_dict["nettype"] :
                    print("seleniumSpider init ERROR: nettype is not the \"http\" or \"https\".")
                    print("seleniumSpider init ERROR: " + str(proxy_dict))
                    print("Exit...")
                    sys.exit(1)
                ip_rex = "([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})"
                ip_mh = re.findall(re.compile(ip_rex) , proxy_dict["ip"])
                if 1 != len(ip_mh) :
                    print("seleniumSpider init ERROR: ip is error!")
                    print("seleniumSpider init ERROR: " + str(proxy_dict))
                    print("Exit...")
                    sys.exit(1)
                if not proxy_dict["port"].isdigit() :
                    print("seleniumSpider init ERROR: port is error!")
                    print("seleniumSpider init ERROR: " + str(proxy_dict))
                    print("Exit...")
                    sys.exit(1)
                self.proxy_dict = proxy_dict
        else :
            self.is_browser_profile = False

    def startSelenium(self) :
        try :
            #self.display = Display(visible=0 , size=(1024,768))
            self.display = Display(visible=0 , size=(1920,1080))
            self.display.start()
            if self.is_browser_profile :
                #Plan A:
                browser_profile = webdriver.FirefoxProfile()
                browser_profile.set_preference("network.proxy.type" , self.proxy_type)
                #{"nettype":"http" , "ip":"211.100.29.195" , "port":"82"}
                proxy_url = str(self.proxy_dict["nettype"]) + "://" + str(self.proxy_dict["ip"]) + ":" + str(self.proxy_dict["port"])
                browser_profile.set_preference("network.proxy.autoconfig_url" , proxy_url)
                browser_profile.update_preferences()
                """
                #Plan B:
                proxy_url = str(self.proxy_dict["nettype"]) + "://" + str(self.proxy_dict["ip"]) + ":" + str(self.proxy_dict["port"])
                browser_profile = Proxy({
                        "proxyType":ProxyType.MANUAL , 
                        "httpProxy":proxy_url , 
                        "ftpProxy":proxy_url , 
                        "sslProxy":proxy_url , 
                        "noProxy":"" , 
                    })
                """
                self.browser = webdriver.Firefox(firefox_profile=browser_profile)
            else :
                self.browser = webdriver.Firefox()
        except Exception as e :
            print("startSelenium() ERROR: " + str(e))
            print("startSelenium() ERROR: browser start error!")
            return False

    def stopSelenium(self) :
        self.browser.quit()
        self.display.stop()

    def restartSelenium(self , proxy_dict=None , is_browser_profile=False , ) :
        self.stopSelenium()
        self.browser = None
        self.__init__(proxy_dict , is_browser_profile)
        self.startSelenium()

    def refresh(self) :
        self.browser.refresh()

    def getWebsite(self , url , stop_try=5) :
        browser_get = True
        try_again = True
        try_times = 0
        if type(stop_try)!=type(int()) and stop_try<=0 :
            stop_try = 1
        while try_again :
            try :
                self.browser.get(url)
                self.browser.implicitly_wait(30)
                #self.browser.set_page_load_timeout(30)
                #self.browser.set_script_timeout(30)
            except Exception as e :
                print("getWebsite() ERROR: " + str(e))
                time.sleep(2)
                try_times += 1
                if try_times <= stop_try :
                    continue
                else :
                    print("getWebsite() ERROR: " + str(url))
                    browser_get = False
            try_again = False
        if browser_get :
            return True
        else :
            return False
    
    def getElementByXpath(self , xpath) :
        try :
            #elements_wait = WebDriverWait(self.browser , 30)
            #elements = elements_wait.until(lambda driver:driver.find_elements_by_xpath(xpath))
            elements = self.browser.find_elements_by_xpath(xpath)
        except Exception as e :
            print("getElementByXpath(): " + str(e))
            return False
        if 0 == len(elements) : 
            print("getElementByXpath(): Zero element found,please check the xpath(" + str(xpath) + ")!")
            return False
        elif len(elements) > 1 :
            print("getElementByXpath(): More than one element,please check the xpath(" + str(xpath) + ")!")
            return False
        return elements[0]

    def getElementsByXpath(self , xpath , number_of_elements=None) :
        try :
            #elements_wait = WebDriverWait(self.browser , 30)
            #elements = elements_wait.until(lambda driver:driver.find_elements_by_xpath(xpath))
            elements = self.browser.find_elements_by_xpath(xpath)
        except Exception as e :
            print("getElementsByXpath(): " + str(e))
            return False
        if 0 == len(elements) :
            print("getElementsByXpath(): Zero element found,please chech the xpath(" + str(xpath) + ")!")
            return False
        elif None!=number_of_elements and number_of_elements!=len(elements) :
            print("getElementsByXpath(): Not the number of elements(" + str(number_of_elements) +") input,please check the xpath(" + str(xpath) + ")!")
            return False
        return elements

    def getElements(self , tag="" , ele="" , xpath=None) :
        if None == xpath :
            xpath = ""
            if ""==tag and ""==ele :
                xpath = "//*"
            elif ""!=tag and ""==ele :
                xpath = "//" + tag + "[@*]"
            elif ""==tag and ""!=ele :
                xpath = "//*[@" + ele + "]"
            elif ""!=tag and ""!=ele :
                xpath = "//" + tag + "[@" + ele + "]"
            else :
                print("getElements() ERROR: tag(" + str(tag) + ") and ele(" + str(ele) + ") is error!")
                return False
        try :
            elements = self.browser.find_elements_by_xpath(xpath)
        except Exception as e :
            print("getElements() ERROR: " + str(e))
            return False
        return elements

    def getAttributesOfElements(self , att=None , tag="" , ele="" , xpath=None) :
        if None == att :
            print("getAttributesOfElements() ERROR: att(" + str(att) + ") is error!")
            return False
        if None == xpath :
            xpath = ""
            if ""==tag and ""==ele :
                xpath = "//*"
            elif ""!=tag and ""==ele :
                xpath = "//" + tag + "[@*]"
            elif ""==tag and ""!=ele :
                xpath = "//*[@" + ele + "]"
            elif ""!=tag and ""!=ele :
                xpath = "//" + tag + "[@" + ele + "]"
            else :
                print("getAttributesOfElements() ERROR: tag(" + str(tag) + ") and ele(" + str(ele) + ") is error!")
                return False
        results = []
        elems = self.browser.find_elements_by_xpath(xpath)
        for elem in elems :
            try :
                att_res = elem.get_attribute(att)
                results.append(att_res)
            except Exception as e :
                print("getAttributesOfElements() ERROR: " + str(e))
                continue
        return results

    def getPageSource(self , browser_or_element , element=None) :
        page_html = ""
        if 1 == browser_or_element :
            try :
                page_html = self.browser.page_source
            except Exception as e :
                print("getPageSource(): " + str(e))
                return False
        elif 2 == browser_or_element :
            if None == element :
                print("getPageSource(): element is None.")
                return False
            try :
                page_html = element.get_attribute("innerHTML")
            except Exception as e :
                print("getPageSource(): " + str(e))
                return False
        return page_html
    


if __name__ == "__main__" :
    url = "http://www.autohome.com.cn/use/"
    #http;111.13.136.46;80
    proxy_dict = {"nettype":"http" , "ip":"111.13.136.46" , "port":"80"}
    sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
    sesp.startSelenium()
    sesp.getWebsite(url)
    elements = sesp.getElements(tag="" , ele="href")
    urls = []
    for ele in elements :
        u = ele.get_attribute("href")
        urls.append(u)
        print(u)
