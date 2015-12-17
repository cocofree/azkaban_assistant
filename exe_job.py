#!/usr/bin/python
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import paramiko
import datetime
import time
import json
CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, 'tinder/python'))

from job_status import JobStatus
from util.helpers import mysql_helper
from util.mail.sendmail import send_html
from util.helpers.alarm_helper import send_msg
from job_define import Job,MyScheduleException
#配置文件
CONFILE = "%s/conf/nice.cfg" % CURRENTPATH

#执行脚本
def exe_job(name,execid,start_time,param_dict_str=''):
    job = Job.get_job_fromdb(name)
    if job.server_host == '' or job.server_user=='' or job.server_script=='':
        raise MyScheduleException('远程配置信息不全')
    
    #1/初始化配置
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(job.server_host,22,job.server_user, "")
    
    #2/初始化默认参数,替换脚本
    param_dict = get_param_dict(start_time,param_dict_str)
    #拼接脚本命令,cd目录,执行脚本,获取脚本执行状态
    command = ' source /etc/bashrc;'
    if job.server_dir !='':
        work_dir,tmp_time = replace_param(job.server_dir,param_dict)
        print 'work_dir:%s' % work_dir
        command = 'cd %s;' % work_dir
    command = command + job.server_script
    if not job.server_script.endswith(';'):
        command = command + ';'
    command = command+'echo "script execute status ["$?"]";'
    command,execute_time = replace_param(command,param_dict)
    print '>>>>>>>>>>>>%s' % (command)
    #####更新job执行状态,启动######
    update_jobstatus(name,execute_time,execid,0)
    
    #3/检查跨项目或时间维度的依赖任务,未完成的两分钟检查一次,并实时输出到日志中
    file_path = '%s/../executor/executions/%s/home/hadoop/service/azkaban/files/%s/_job.%s.%s.log' % (CURRENTPATH,execid,job.project_name,execid,job.name)
    if job.ext_dependencies != '':
        query_jobs = get_extdep_jobs(execute_time,job.ext_dependencies)
        f = open(file_path,'a')
        f.write('>>>>>>>>>>>>当前任务的基准时间:%s\n' % execute_time)
        f.write('>>>>>>>>>>>>依赖的外部任务配置:%s\n' % job.ext_dependencies)
        f.close()
        while True:
            flag,mes = JobStatus.is_ready(query_jobs)
            f = open(file_path,'a')
            f.write('>>>>>>>>>>>>依赖的外部任务准备情况:%s\n' % mes)
            f.close()
            
            if flag:
                break
            else:
                time.sleep(120)

    #4/脚本执行,输出信息
    stdin, stdout, stderr = ssh.exec_command(command)
    error_flag = True
    print '---------------out----------------'
    for line in stdout.readlines():
        print line.replace('\n','')
        if line.find('script execute status [0]')>=0:
            error_flag=False
    print '---------------err-----------------'
    for line in stderr.readlines():
        print line.replace('\n','')
    print '---------------err end-----------------'
    ssh.close()

    #5/出错发邮件及短信,并抛出异常
    if error_flag:
        #####更新job执行状态,失败######
        update_jobstatus(name,execute_time,execid,-1)
        exe_alarm(job,execid,start_time)
        raise MyScheduleException('脚本执行过程出错')
    
    #####更新job执行状态,成功######
    update_jobstatus(name,execute_time,execid,1)

#更新Job执行信息
def update_jobstatus(job_name,execute_time,execid,status):
    job_status = JobStatus()
    job_status.job_name = job_name
    job_status.execute_time = execute_time
    job_status.exec_id = execid
    job_status.status = status
    job_status.update_jobstatus()
    print '更新[%s]的执行状态[execute_time:%s][status:%s]' % (job_name,execute_time,status)

#失败告警
def exe_alarm(job,execid,start_time):
    #邮件
    if job.failure_email!='':
        title = 'azkaban[%s][%s]任务执行出错' % (job.project_name,job.name)
        content = '''
        <br>执行时间:%s
        <br>azkaban[%s][%s]任务执行出错,请查看日志处理
        <br><a href='https://brec02:8443/executor?execid=%s&job=%s'>点击查看日志</a>
        ''' % (start_time,job.project_name,job.name,execid,job.name)
        mailto = job.failure_email.split(',')
        send_html(mailto,title,content)
    
    #短信
    if job.failure_sms!='':
        content = 'azkaban[%s][%s]任务执行出错,请处理' % (job.project_name,job.name)
        msgto = job.failure_sms.split(',')
        for phone in msgto:
            send_msg(phone, content , '报警')

#获取替换参数列表
def get_param_dict(start_time,param_dict_str):
    param_dict = {}
    #默认时间参数
    time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    cur_time = start_time
    cur_hour = time.strftime('%Y%m%d%H')
    cur_date = time.strftime('%Y%m%d')
    last_hour = (time - datetime.timedelta(hours=1)).strftime('%Y%m%d%H')
    last_two_hour = (time - datetime.timedelta(hours=2)).strftime('%Y%m%d%H')
    last_date = (time - datetime.timedelta(days=1)).strftime('%Y%m%d')
    last_two_date = (time - datetime.timedelta(days=2)).strftime('%Y%m%d')

    param_dict['cur_time'] = cur_time
    param_dict['cur_hour'] = cur_hour
    param_dict['cur_date'] =cur_date
    param_dict['last_hour'] =last_hour
    param_dict['last_two_hour'] =last_two_hour
    param_dict['last_date'] =last_date
    param_dict['last_two_date'] =last_two_date
    #默认目录参数
    param_dict['default_work_dir'] = '/home/hadoop/schedule-service/current/'
    #页面传参
    try:
        if param_dict_str!='':
            dicts = param_dict_str.split(',')
            for d in dicts:
                item = d.split(':')
                key = item[0]
                value = item[1]
                param_dict[key] = value
    except Exception,e:
        print e

    print param_dict
    return param_dict


#替换参数,生成任务执行时间标识
def replace_param(source,param_dict):
    #默认的执行时间标识为当天
    execute_time = param_dict['cur_date']
    for k,v in param_dict.items():
        replace_str = '&[%s]' % k
        #以命令里的时间参数为准
        if source.find(replace_str)>=0 and (replace_str.find('hour')>=0  or replace_str.find('date')>=0):
            execute_time = v

        source = source.replace(replace_str,v)
    
    return source,execute_time

#根据配置生成外部依赖任务
def get_extdep_jobs(base_time,ext_deps):
    ext_jobs = json.loads(ext_deps)
    query_jobs = []
    for ext_job in ext_jobs['jobs']:
        execute_time = get_exetime(base_time,ext_job['time_type'],ext_job['hour_diff'])
        
        job_status = JobStatus()
        job_status.job_name = ext_job['name']
        job_status.execute_time = execute_time
        print '>>>>>>>>>>>>外部依赖任务检查[%s][%s]' % (job_status.job_name,job_status.execute_time)
        query_jobs.append(job_status)
    
    return query_jobs

#根据基准时间获取依赖任务的时间参数
def get_exetime(base_time,time_type,hour_diff):
    #基准时间戳
    base_stamp = None
    exec_time = base_time
    #天级/小时级
    if len(str(base_time))==8:
        base_stamp = datetime.datetime.strptime(str(base_time),"%Y%m%d")
    elif len(str(base_time))==10:
        base_stamp = datetime.datetime.strptime(str(base_time),"%Y%m%d%H") 
        
    exec_stamp = base_stamp + datetime.timedelta(hours=hour_diff)
    
    if time_type=='day':
        exec_time = exec_stamp.strftime('%Y%m%d')
    elif time_type=='hour':
        exec_time = exec_stamp.strftime('%Y%m%d%H')

    return exec_time

#目录处理
def process_dir(work_dir):
    dir_params_dict = {}
    dir_params_dict['default_work_dir'] = '/home/hadoop/schedule-service/current/'

    for k,v in dir_params_dict.items():
        replace_str = '&[%s]' % k
        work_dir = work_dir.replace(replace_str,v)
    
    return work_dir

if __name__ == '__main__':
    job_name = sys.argv[1]
    execid = sys.argv[2]
    start_time = ''.join(list(sys.argv[3].replace('T',' '))[:19])
    param_dict = ''
    try:
        param_dict = sys.argv[4]
        print '----[param_dict] %s' % param_dict
    except:
        pass
    #try:
    #    raise MyScheduleException('脚本执行过程出错')
    #except Exception,e:
    #    print e
    exe_job(job_name,execid,start_time,param_dict)

