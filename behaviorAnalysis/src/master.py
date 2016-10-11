#_____________________________master.py_____________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : master
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-09-20 16:53
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
import logging
import logging.config
import logging.handlers
import hashlib
from operator import add , itemgetter
#External Moduls
import redis

"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
if len(sys.argv) < 1:
    print("---> Program needs 1 argument.\nExit...")
    print("sys.argv: " + str(sys.argv))
    sys.exit(1)
opts,args = getopt.getopt(sys.argv[1:] , "d:")
work_dir = ""
for opt,val in opts :
    if "-d" == opt :
        work_dir = str(val)
    else :
        print("Arguments ERROR.")
        print("opt:\t" + str(opt))
        print("val:\t" + str(val))
        sys.exit(1)

src_path = work_dir + "/src"
tools_path = src_path + "/tools"
sys.path.append(src_path)
sys.path.append(tools_path)
#Cumtomize Moduls
import settings
from tools.Platform import *
from tools.MD5 import *
from tools.Log import *
from tools.MultiProcess import *
from tools.StringTool import *
from tools.Network import *
script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

#work_dir = "./"
log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/htmlSpider.log"
logger = Log(log_dir , log_file)
logger.init()

#----------------------------------------------------------------------------------
#-----------------------------------Ready------------------------------------------
#----------------------------------------------------------------------------------

class Monitor() :
    def __init__(self) :
        self.slaves = []
