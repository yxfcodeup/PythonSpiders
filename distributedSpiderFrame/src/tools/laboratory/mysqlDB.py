#_____________________________mysqlDB.py____________________________________________
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

#External
import pymysql


class MysqlDB() :
    def __init__(self , in_host="localhost" , in_user="root" , in_passwd=None , in_db=None , in_port=3306 , in_charset="utf8") :
        try :
            self.conn = pymysql.connect(host=in_host , user=in_user , passwd=in_passwd , db=in_db , port=in_port , charset=in_charset)
        except Exception as e :
            print("MysqlDB init ERROR: " + str(e))
            print("Exit...")
            exit(1)

