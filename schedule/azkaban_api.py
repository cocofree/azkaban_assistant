#!/usr/bin/python
#encoding:utf-8
'''
生成azkaban的配置文件
'''
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import zipfile
import urllib
import urllib2
import json
import commands
import logging
import datetime

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, 'tinder/python'))

from util.helpers import mysql_helper
from job_define import Job,MyScheduleException
from azkaban_helper import get_session_id
#配置文件
CONFILE = "%s/conf/nice.cfg" % CURRENTPATH

def schedule_flow(session_id,project_name,flow_name,schedule_time,period):
    url = 'https://localhost:8443/schedule'
    
    project_id = Job.get_projectid_byname(project_name)
    sstime = datetime.datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
    sdate = sstime.strftime('%m/%d/%Y')
    stime = sstime.strftime('%I,%M,%p,')

    params = 'is_recurring=on&period=%s&projectName=%s&flow=%s&projectId=%s&scheduleTime=%s&scheduleDate=%s' % (period,project_name,flow_name,project_id,stime,    sdate)
    
    command = '''curl -k %s -d "ajax=scheduleFlow&%s" -b azkaban.browser.session.id=%s''' % (url,params,session_id)
    
    logging.info(command)
    status,result = commands.getstatusoutput(command)
    #
    resp = json.loads(result[result.find('{'):])
    if "error" in resp.keys():
        raise Exception(resp['error'])
    if 'status' in resp.keys()  and resp['status']=='error':
        raise Exception(resp['message'])
    
    return resp

def execute_flow(session_id,project_name,flow_name,param_dict={}):
    url = 'https://localhost:8443/executor'
    ignore_set = set(["concurrentOption","pipelineLevel"])
    param_str = ' '.join(map(lambda (k,v):"--data '%s=%s' " % (k if k in ignore_set else 'flowOverride[%s]'% k ,v[0] if type(v)==type([]) else v),param_dict.items()))

    command = '''curl -k --get --data 'session.id=%s' --data 'ajax=executeFlow' --data 'project=%s' --data 'flow=%s' %s %s''' %  (session_id,project_name,flow_name,url,param_str)

    logging.info(command)
    status,result = commands.getstatusoutput(command)
    logging.info(result)
    resp = json.loads(result[result.find('{'):])
    if "error" in resp.keys():
        raise Exception(resp['error'])
    
    return resp

def fetchexec_flow(session_id,execid):
    url = 'https://localhost:8443/executor'
    command = '''curl -k --data "session.id=%s&ajax=fetchexecflow&execid=%s" %s''' % (session_id,execid,url)
    logging.info(command)
    status,result = commands.getstatusoutput(command)
    logging.info(result)
    try:
        resp = json.loads(result[result.find('{'):])
    except:
        raise Exception('error execid[%s]' % execid)
    
    if "error" in resp.keys():
            raise Exception(resp['error'])
    return resp


def canel_execflow(execid):
    session_id = get_session_id('admin','admin_pwd')
    url = 'https://localhost:8443/executor'
    command = '''/usr/local/bin/curl -k --data "session.id=%s&ajax=cancelFlow&execid=%s" %s''' % (session_id,execid,url)
    logging.info(command)
    status,result = commands.getstatusoutput(command)
    logging.info(result)
    try:
        resp = json.loads(result[result.find('{'):])
    except:
        raise Exception('error execid[%s]' % execid)
    
    if "error" in resp.keys():
            raise Exception(resp['error'])
    return resp

if __name__ == '__main__':
    session_id = get_session_id('admin','admin_pwd')
    canel_execflow(112345)
    #generate_files(session_id)

