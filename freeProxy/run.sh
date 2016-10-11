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
pylog="${workdir}/logs/log.log"
settings="${workdir}/config/settings.py"
redis_host="192.168.1.111"
redis_port="6380"
redis_db="0"
#--------------------------------------------------------------------------------+

echo $workdir
log "-----------------------------------------------------------------------------"
log "start"
python3 ${workdir}/src/getProxy.py -p "${workdir}" -h "${redis_host}" -o "${redis_port}" -n "${redis_db}"
log "end"
log "-----------------------------------------------------------------------------"
