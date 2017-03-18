#!/usr/bin/sh

pid=`ps aux | grep "router/schedule_router.py" |grep -v grep |awk '{print $2}'`
[ "$pid" != "" ] && kill -9 $pid 
echo $pid

