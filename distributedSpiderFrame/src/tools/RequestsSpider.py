#_____________________________requestsSpider.py____________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : requestsSpider
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-11 14:20
# End time      :
# Function      : 
# Operation     :
#-----------------------------------------------------------------------------------

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
#External Moduls
import requests


class RequestsSpider() :
    def __init__(self , headers=None) :
        self.headers = {
                "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0" , 
                }
        if None != headers :
            self.headers = headers

    def startRequests(self , url , try_times=5 , in_timeout=20 , content_or_text=1 , default_code_type="utf-8" , code_type_rex=None) :
        #content_or_text:content-->2    text-->1
        #code_type_rex:utf-8 , utf8 , gb2312 , gb-2312 , big5 , big-5 , ansi
        requests.adapters.DEFAULT_RETRIES = try_times
        page_html = ""
        try :
            response = requests.get(url , timeout=in_timeout , headers=self.headers)
            page_html = response.content
        except Exception as e :
            print("startRequests() ERROR: " + str(e))
            return False
        try :
            if None == code_type_rex :
                code_type_rex = "<meta.{0,500}charset=[\'\"]{0,1}(utf-8|utf8|gb2312|gb-2312|big5|big-5|ansi)[\'\"]{0,1}"
            code_type_mh = re.findall(re.compile(code_type_rex) , str(page_html).lower())
            code_type = default_code_type
            if 0 == len(code_type_mh) :
                print("startRequests(): code type is default!")
            elif 1 == len(code_type_mh) :
                code_type = code_type_mh[0]
            else :
                code_type = code_type_mh[0]
                print("startRequests() WARNING: More than one code type(" + str(code_type_mh) + ")!")
            print("startRequests(" + str(url) + ") code type is " + str(code_type))
            response.encoding = code_type
            if 2 == content_or_text :
                page_html = response.content
            elif 1 == content_or_text :
                page_html = response.text
            else :
                print("startRequests() ERROR: content_or_text is not 1 or 2.")
        except Exception as e :
            print("startRequests() ERROR: " + str(e))
            return False
        return page_html
