## Model
### Directory Structure
#### Files
* AlternationLog
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

#### Linux libs(CentOS 7)
* yum install xvfb
* yum install python-lxml*
* yum install gcc ruby-devel libxml2 libxml2-devel libxslt libxslt-devel 

### crontab 
example:
```
55	19	*	*	*	root	/home/yxf/workspace/py/spiders/freeProxy/run.sh	>> /home/yxf/workspace/py/spiders/freeProxy/logs/crontab.log 2>&1 & 
```

### nohu
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
