#!/usr/bin/python
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import urllib
import urllib2
import paramiko
import datetime
import time
import json
CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, 'tinder/python'))

from util.helpers import mysql_helper
#from util.mail.sendmail import send_html
#from util.helpers.alarm_helper import send_msg
from azkaban_api import canel_execflow

#配置文件
CONFILE = "%s/conf/nice.cfg" % CURRENTPATH

#获取数据库
def get_db():
    return mysql_helper.get_slave_db(db = "master_azkaban", confile = CONFILE)

def send_msg(msgto,content,level='报警'):
    pass
    #res_data = urllib2.urlopen(req)

def check_jobs():
    sql = '''
    select count(1),
    ifnull(sum(if(t.start_time=-1,1,0)),0),
    ifnull(sum(if(unix_timestamp(now())-start_time/1000>60*60*24,1,0)),0) 
    from execution_flows t 
    where end_time=-1'''
    db = get_db()
    total,prepared,overtime = db.fetch_one(sql)
    print total,prepared,overtime 
    if total>=10 and prepared>=1:
        title = 'azkaban任务队列出现阻塞,请处理'
        mes = '当前azkaban队列共[%s]个任务,其中[%s]阻塞中' % (total,prepared)
        exe_alarm(title,mes)
    elif overtime>=1:
        sql = '''
        select 
        count(1),group_concat("[",t.flow_id,",",submit_user,"]"),group_concat(exec_id)
        from execution_flows t 
        where end_time=-1 and unix_timestamp(now())-start_time/1000>60*60*24
        '''
        db = get_db()
        overtime,mes,ids = db.fetch_one(sql)
        print ids
        title = 'azkaban有任务超过1天%s,已kill' % mes
        mes = '当前azkaban共[%s]超过1天,分别是%s' % (overtime,mes)
        exe_alarm(title,mes)
        for exec_id in ids.split(','):
            try:
                canel_execflow(exec_id)
            except Exception,e:
                print e

#失败告警
def exe_alarm(title,mes):
    mailto = ['wangxu@oneniceapp.com']
    msgto = ''
    #邮件
    title = '!!!!![这是报警]%s' % title
    content = "&nbsp;&nbsp;&nbsp;&nbsp;%s<br>&nbsp;&nbsp;&nbsp;&nbsp;<a href='https://localhost:8443/executor'>详情查看</a>" % mes
    send_html(mailto,title,content)
    
    send_msg(msgto, title , '报警')

if __name__ == '__main__':
    check_jobs()
