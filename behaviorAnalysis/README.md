## Model
#### crontab 
example:
```
55	19	*	*	*	root	/home/yxf/workspace/py/spiders/freeProxy/run.sh	>> /home/yxf/workspace/py/spiders/freeProxy/logs/crontab.log 2>&1 & 
```
#### nohup
example:
```
nohup /home/yxf/workspace/py/spiders/freeProxy/run.sh >> /home/yxf/workspace/py/spiders/freeProxy/logs/nohup.log 2>&1 &
```
