#_____________________________bs4Spider.py__________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : bs4Spider
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-08-10 11:40
# End time      :
# Function      : 
# Operation     :
#-----------------------------------------------------------------------------------

import os
import sys
import time
import datetime
import random
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


class BS4Spider() :
    def __init__(self) :
        self.soup = None

    def createSoup(self , html) :
        self.soup = BeautifulSoup(str(html) , "lxml")

    def matchOne(self , fname , fattrs=None) :
        soup_match = None
        if None == fattrs :
            try :
                soup_match = self.soup.find_all(name=fname)
            except Exception as e :
                print("matchOne(): " + str(e))
                return False
        else :
            if type(fattrs)==type(dict()) and len(fattrs)>0 :
                soup_match = self.soup.find_all(name=fname , attrs=fattrs)
            else :
                print("matchOne(): The fattrs is not dict or lenght is 0.")
                return False
        if 1 == len(soup_match) :
            try :
                soup_match = soup_match[0]
            except Exception as e :
                print("matchOne(): " + str(e))
                return False
        elif 0 == len(soup_match) :
            print("matchOne(): No one result matched,please check the fname(" + str(name) + ") and the fattrs(" + str(fattrs) + ")!")
            return False
        else :
            print("matchOne(): More than one result matched,please check the fname(" + str(fname) + ") and the fattrs(" + str(fattrs) + ")!")
            #return False
            return soup_match[0]
        return soup_match

    def matchAll(self , fname , fattrs=None) :
        soup_match = None
        if None == fattrs :
            try :
                soup_match = self.soup.find_all(name=fname)
            except Exception as e :
                print("matchAll(): " + str(e))
                return False
        else :
            if type(fattrs)==type(dict()) and len(fattrs)>0 :
                soup_match = self.soup.find_all(name=fname , attrs=fattrs)
            else :
                print("matchAll(): The fattrs is not dict or lenght is 0.")
                return False
        return soup_match
        
