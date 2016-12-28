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


#ord(".")=46 , ord("0")=48 , ord("1")=49 , ord("2")=50 , ord("3")=51 , ord("4")=52 , ord("5")=53 , ord("6")=54 , ord("7")=55 , ord("8")=56 , ord("9")=57
def isnumber(nstr) :
    if type(nstr) != type(str()) :
        print("tools.isnumber(): " + str(nstr) + " is not string!Cannot judge it!")
        return False
    num_str = ""
    num_dot = 0
    if 0 == len(nstr) :
        return False
    if 1 == len(nstr) :
        if ord(nstr)>=48 and ord(nstr)<=57 :
            return True
        else :
            return False
    for i in range(len(nstr)) :
        ns = nstr[i]
        if (ord(ns)<48 or ord(ns)>57) and 46!=ord(ns):
            print(ord(ns))
            return False
        if 46 == ord(ns) :
            num_dot += 1
    if num_dot > 1 :
        return False
    return True


if __name__ == "__main__" :
    a = "0.1"
    b = "00.1"
    c = " "
    d = ""
    e = "1.0"
    print(isnumber(e))
