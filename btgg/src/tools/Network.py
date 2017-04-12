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


def ping(url , times=10) :
    def isnumber(nstr) :
        if type(nstr) != type(str()) :
            print("tools.isnumber(): " + str(nstr) + " is not string!Cannot judge it!")
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
    shell_path = "./sh"
    ping_shell = "./sh/ping.sh"
    if not os.path.exists(shell_path) :
        print("tools.ping() WARNING: ./sh do not exists!")
        os.mkdir(shell_path)
    if not os.path.exists(ping_shell) :
        print("tools.ping() WARNING: ./sh/ping.sh do not exists!")
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
        print("tools.ping() ERROR!")
        print("tools.ping() ERROR: " + str(res))
        return False
    if 1 != len(pac_loss_mh) :
        print("tools.ping() ERROR!")
        print("tools.ping() ERROR: " + str(res))
        return False
    min_avg_max_mdev = str(min_avg_max_mdev_mh[0]).split("/")
    avg_time = min_avg_max_mdev[1]
    pac_loss = pac_loss_mh[0]
    if isnumber(str(avg_time)) :
        avg_time = float(avg_time)
    if isnumber(str(pac_loss)) :
        pac_loss = float(pac_loss)
    return [avg_time , pac_loss]


def wget(wget_command) :
    #wget.sh
    #WGET=`$1`
    shell_path = "./sh"
    wget_shell = "./sh/wget.sh"
    if not os.path.exists(shell_path) :
        print("tools.networkTool.wget() WARNING: ./sh do not exists!")
        os.mkdir(shell_path)
    if not os.path.exists(wget_shell) :
        print("tools.networkTool.wget() WARNING: ./sh/wget.sh not exists!")
        os.system("echo '#/bin/bash' >> ./sh/wget.sh")
        os.system("echo 'WGET=`$1`' >> ./sh/wget.sh")
    print(wget_command)
    os.system(wget_command)
    return True


if __name__ == "__main__" :
    url = "www.baidu.com"
    print(ping(url))
    #wget_command = "wget -r -P ./a http://diameizi.diandian.com 2>|./b/log.txt"
    #wget(wget_command)
