import os
import sys

file_list = os.listdir("./")
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
