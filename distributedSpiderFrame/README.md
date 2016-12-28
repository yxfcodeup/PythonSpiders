## Model
### Directory Structure
#### Files
* AlternationLog
* .gitignore
```
#以'#'开始的行，被视为注释.                                                          
#以斜杠“/”开头表示目录；
#以星号“*”通配多个字符；
#以问号“?”通配单个字符；
#以方括号“[]”包含单个字符的匹配列表；
#以叹号“!”表示不忽略(跟踪)匹配到的文件或目录；
#git 对于 .ignore
#配置文件是按行从上到下进行规则匹配的，意味着如果前面的规则匹配的范围更大，则后面的规则将不会生效；

# 1. 忽略掉所有文件名是 foo.txt的文件.
#foo.txt

# 2. 忽略所有生成的 html文件,
#*.html

# 3. foo.html是手工维护的，所以例外.
#!foo.html

# 4. 忽略所有.o和 .a文件.
#*.[oa]
```

* README.md
* run_master.sh
* run_slave.sh

#### Directories
* config
* dataResults
* dataSources
* lib
* logs
* References
* src

### Dependencies
#### Python
* pip install grpcio
* pip install redis
* pip install lxml
* pip install selenium
* pip install pyvirtualdisplay

#### Linux libs
* yum install xvfb
* yum install python-lxml*
* yum install gcc ruby-devel libxml2 libxml2-devel libxslt libxslt-devel 

### crontab 
example:
```
55	19	*	*	*	root	/home/yxf/workspace/py/spiders/freeProxy/run.sh	>> /home/yxf/workspace/py/spiders/freeProxy/logs/crontab.log 2>&1 & 
```
### nohup
example:
```
nohup /home/yxf/workspace/py/spiders/freeProxy/run.sh >> /home/yxf/workspace/py/spiders/freeProxy/logs/nohup.log 2>&1 &
```

### run.sh
```
#!/bin/bash

#source ~/.bashrc
#source /etc/profile
function getCurrentPath() 
{
    local _tmp_=`echo $0|grep "^/"`
    if test "${_tmp_}"
    then
        dirname $0
    else 
        dirname `pwd`/$0
    fi
}
workdir=$(getCurrentPath)
ttg="/."
ta=${workdir:${#workdir}-2:${#workdir}}
if [ "$ttg" = "$ta" ] 
then
    workdir=${workdir:0:-2}
fi

logfile="${workdir}/logs/run.log"
function log()
{
    echo `date '+%Y-%m-%d %H:%M:%S'` $*
    echo `date '+%Y-%m-%d %H:%M:%S'` $* >> ${logfile}
}
pre_time=`date +%Y%m%d%H -d '-4 hours'`
test_time=`date +%Y%m%d%H%M%S`

#-------------------------------------Customize----------------------------------+
#
#--------------------------------------------------------------------------------+

echo $workdir
log "-----------------------------------------------------------------------------"
log "start"
#python3 ${workdir}/src/htmlSpider.py -d "${workdir}"
python3 ${workdir}/src/slaveSpider.py 
log "end"
log "-----------------------------------------------------------------------------"
```
