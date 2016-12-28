import os
import sys
import getopt


"""
"parameter和argument的区别
" 1. parameter是指函数定义中参数，而argument指的是函数调用时的实际参数。
" 2. 简略描述为：parameter=形参(formal parameter)， argument=实参(actual parameter)。
" 3. 在不很严格的情况下，现在二者可以混用，一般用argument，而parameter则比较少用。
"opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
"""
if len(sys.argv) < 1 :
    print("---> Program needs 3 argument.\nExit...")
    print("sys.argv: " + str(sys.argv))
    sys.exit(1)
opts,args = getopt.getopt(sys.argv[1:] , "p:")
work_dir = ""
for opt,val in opts :
    if "-p" == opt :
        work_dir = str(val)
    else :
        print("Arguments ERROR.")
        print("opt:\t" + str(opt))
        print("val:\t" + str(val))
        sys.exit(1)


file_list = os.listdir(work_dir)
py_list = []
for f in file_list :
    if ".py"==f[-3:] and "__"!=f[:2]:
        py_list.append(f[:-3])

py_str = "__all__ = [ "
for p in py_list :
    py_str += "\"" + p + "\" , "

py_str = py_str[:-3]
py_str += "]"

os.system("> __init__.py")
os.system("echo 'import os\nimport sys' >> __init__.py")
os.system("echo 'PYVI = sys.version_info' >> __init__.py")
os.system("echo '" + str(py_str) + "' >> __init__.py")
