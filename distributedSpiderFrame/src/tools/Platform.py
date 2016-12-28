import os
import sys
import re
import time
import math
import datetime
import platform
from multiprocessing import cpu_count

def getPlatform() :
    pf = (platform.system()).lower()
    if "linux" in pf :
        return 1
    elif "windows" in pf :
        return 2
    else :
        return 0

def cpuCount() :
    return cpu_count()


if __name__ == "__main__" :
    print(cpuCount())
