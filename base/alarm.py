#!/usr/bin/python
#encoding:utf-8

'''
报警处理,自定义实现
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import paramiko
import datetime
import time
import json
CURRENTPATH = os.path.dirname(os.path.abspath(__file__))

#失败告警                                                                          
def exe_alarm(job,execid,start_time):                                          
    #邮件                                                                       '
    if job.failure_email!='':                                                  
        title = 'azkaban[%s][%s]任务执行出错' % (job.project_name,job.name)          
        content = '''                                                         
        <br>执行时间:%s                                                           
        <br>azkaban[%s][%s]任务执行出错,请查看日志处理                                     
        <br><a href='https://brec02:8443/executor?execid=%s&job=%s'>点击查看日志</a>
        ''' % (start_time,job.project_name,job.name,execid,job.name)          
        mailto = job.failure_email.split(',')                                 
        print content
        #邮件接口
        #send_html(mailto,title,content)                                       
                                                                              
    #短信                                                                       
    if job.failure_sms!='':                                                   
        content = 'azkaban[%s][%s]任务执行出错,请处理' % (job.project_name,job.name)   
        msgto = job.failure_sms.split(',')                                    
        for phone in msgto:                                                   
            print content
            #短信接口
            #send_msg(phone, content , '报警')                                   
                                                                              

