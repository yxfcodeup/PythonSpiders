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



def listFormatString(in_list , separator=",") :
    if None==in_list or type(in_list)!=type(list()) or 0==len(in_list) :
        print("tools.listFormatString() ERROR: in_list is error.")
        return False
    if type(separator) != type(str()) :
        print("tools.listFormatString() ERROR: separator is not string1")
        return False
    res = ""
    stan = "{0}" + separator
    for i in range(len(in_list)) :
        res += stan.format(in_list[i])
    return res[:-1]


if __name__ == "__main__" :
    t = ["ab" , 1 , ["c" , 2]]
    print(listFormatString(t))
