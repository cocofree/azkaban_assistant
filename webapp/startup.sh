#!/bin/bash

CURDIR=`pwd`
#export CONF_HOME=$CURDIR/conf
export PYTHONPATH=$CURDIR:$PYTHONPATH

nohup python router/schedule_router.py --port=8445 > schedule_web.log 2>&1 &
