#_____________________________MicroDB.py_______________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : MicroDB
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.6
# Start time    : 2017-04-12 10:17
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
import configparser
import re
import getopt
import urllib
import random
import json
import pickle
import socket
import logging
import logging.config
import logging.handlers
import hashlib
from operator import add , itemgetter
from concurrent import futures
#External Moduls

#-------------------------------Global params---------------------------------------
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
_WORK_DIR_ = script_path
_FILE_NAME_ = os.path.split(os.path.realpath(__file__))[-1]

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

def MicroDB() :
    def __init__(self , cache_root_dir) :
        if os.path.isdir(cache_root_dir) :
            self.__root_dir = cache_root_dir
        else :
            self.__root_dir = _WORK_DIR_ + "/cache"
            if not os.path.exists(self.__root_dir) :
                os.mkdir(self.__root_dir)
        self.DB = {}

    def __loadCache(self) :
        pass
