#_____________________________md5.py________________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : mysqlDB
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-09-12 15:06
# End time      :
# Function      : 
# Operation     :
#-----------------------------------------------------------------------------------
# PREPARATION
# $ sudo pip3 install pymysql 
#-----------------------------------------------------------------------------------

import os
import sys
import time
import datetime
import multiprocessing
import re
import getopt
import urllib
import json
import logging
import logging.config
import logging.handlers
import hashlib


def getmd5(in_str) :
    res = ""
    md = hashlib.md5()
    md.update(in_str.encode("utf-8"))
    res = md.hexdigest()
    return res



if __name__ == "__main__" :
    a = "https://seleniumhq.github.io/selenium/docs/api/py/selenium/selenium.selenium.html#module-selenium.selenium"
    b = getmd5(a)
    print(b)
