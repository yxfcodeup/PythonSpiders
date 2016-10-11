#_____________________________xdrProject.py_________________________________________
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------
# Name          : xdrProject
# Version       : 1.0.0
# Author        : yxf
# Language      : Python 3.4.3
# Start time    : 2016-07-20 14:43
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
import json
import logging
import logging.config
import logging.handlers
from operator import add
#External Moduls
import cx_Oracle
from pyspark import SparkContext , SparkConf

#-----------------------------------Reading arguments-------------------------------
"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
if len(sys.argv) < 2 :
    print("---> Program needs 2 argument.\nExit...")
    print("sys.argv: " + str(sys.argv))
    sys.exit(1)
#-p: path
#-t: time
opts,args = getopt.getopt(sys.argv[1:] , "p:t:")
work_dir = ""
in_time= ""
for opt,val in opts :
    if "-p" == opt :
        work_dir = str(val) 
    elif "-t" == opt :
        in_time = str(val)
    else :
        print("Arguments error.")
        print("opt: " + str(opt))
        print("val: " + str(val))
        print("Exit...")
        sys.exit(1)

#Cumtomize Moduls
import settings
#script_path = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.append(work_dir+settings.folder_path["lib"])
import tools

log_dir = work_dir + settings.folder_path["log"]
log_file = log_dir + "/log.log"
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

#Global Functions and Variables
#Read only
#app_type = tools.readFileLinesToList(work_dir+settings.folder_path["dsource"]+"/apptype.txt" , "\t")
#app_subtype = tools.readFileLinesToList(work_dir+settings.folder_path["dsource"]+"appsubtype.txt" , "\t")

#----------------------------------------------------------------------------------
#-----------------------------------Ready------------------------------------------
#----------------------------------------------------------------------------------
def getKV(line) :
    res_key = str(line[0])
    val_list = line[1]
    res_val = {}
    for ele in val_list :
        subty = int(ele[1])
        print(subty)
        if subty in res_val :
            res_val[subty].append(str(ele[2]))
        else :
            res_val[subty] = [str(ele[2])]
    return {res_key:res_val}



def matchURL(url) :
    res_url = ""
    rex_1 = "(f|ht){1}(tp|tps){1}(:\/\/)([0-9a-zA-Z\-\.]*)(\/){0,1}"
    rex_2 = "([0-9a-zA-Z\-\.]*)(\/){0,1}"
    url_mh_1 = re.findall(re.compile(rex_1) , url)
    url_mh_2 = re.findall(re.compile(rex_2) , url)
    if 0 != len(url_mh_1) :
        if 0 != len(url_mh_1[0]) :
            for um in url_mh_1[0] :
                if "/" == um :
                    break
                res_url += um
    elif 0 != len(url_mh_2) :
        if 0 != len(url_mh_2[0]) :
            for um in url_mh_2[0] :
                if "/" == um :
                    break
                res_url += um
    return res_url

def filtData(line) :
    try :
        line = line.split("~,~")
    except UnicodeDecodeError as e :
        return False
    if 118 != len(line) :
        return False
    if ""==line[22] or False==line[22].isdigit() or ""==line[23] or False==line[23].isdigit() :
        return False
    url = matchURL(line[83])
    if "" == url :
        return False
    return True

def splitLine(line) :
    line = line.split("~,~")
    url = matchURL(line[83])
    return [line[22] , line[23] , url]

def test(m , n) :
    print(m , n)
    return m+n

def xdrProject(sc , hdfs_path) :
    #data_dir = "hdfs://192.168.1.111:8020/user/xdr/20160624/*"
    data_dir = "hdfs://192.168.1.111:8020/user/xdr/test/*"
    #xdr_rdd = sc.textFile(data_dir)
    xdr_rdd = sc.parallelize([("a" , 1) , ("a" , 4) , ("a" , 2) , ("a" , 3) , ("a" , 5)])
    res_rdd = xdr_rdd.reduceByKey(test)
    print(res_rdd.count())
    """
    res_rdd = xdr_rdd.filter(lambda line:filtData(line))\
            .map(lambda line:splitLine(line))\
            .groupBy(lambda line:line[0])\
            .map(lambda line:getKV(line))
            #.mapValues(list)
    res_list = res_rdd.collect()
    for ele in res_list :
        for atype,val in ele.items() :
            with open("./dataResults/xdrtype.txt" , "a") as f :
                for subtype,urls in val.items() :
                    f.write(str({subtype:urls}))
                    f.write("\n")
    """
    return


def mainRun() :
    try :
        hdfs_path = settings.dir_path["hdfs_path"]
        spark_url = settings.spark_config["spark_url"]
        spark_conf_settings = settings.spark_config["spark_conf_settings"]
    except Exception as e :
        logger.error(str(e))
        logger.error("Exit...")
        sys.exit(1)
    app_name = "xdrProject"
    spark_conf = SparkConf().setAppName(app_name).setMaster(str(spark_url))
    for conf_name,conf_sets in spark_conf_settings.items() :
        spark_conf = spark_conf.set(conf_name , conf_sets)
    sc = SparkContext(conf=spark_conf)
    logger.info("Spark config: " + str(spark_conf.getAll()))
    xdrProject(sc , hdfs_path)


if __name__ == "__main__" :
    mainRun()
