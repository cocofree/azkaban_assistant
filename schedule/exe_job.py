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
import traceback
CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, '.'))

from job_status import JobStatus
from util.helpers import mysql_helper
from util.alarm import send_html
from util.alarm import send_msg
from job_define import Job,MyScheduleException
from util.config import get_conf
#配置文件
CONFILE = "%s/conf/nice.cfg" % CURRENTPATH

#获取数据库
def get_db():
    return mysql_helper.get_slave_db(db = "master_azkaban", confile = CONFILE)

#执行脚本
def exe_job(name,execid,start_time,param_dict_str=''):
    job = Job.get_job_fromdb(name)
    try:
        error_flag = process(name,execid,start_time,param_dict_str)
    except:
        traceback.print_exc()
        exe_alarm(job,execid,start_time)
        sysout('-------------以下为系统主动报错信息,忽略-------------------')
        raise MyScheduleException('脚本执行过程出错')
        
    if error_flag:
        exe_alarm(job,execid,start_time)
        sysout('-------------以下为系统主动报错信息,忽略-------------------')
        raise MyScheduleException('脚本执行过程出错')

def process(name,execid,start_time,param_dict_str=''):
    sysout('+++++++++++++任务初始化+++++++++++++++')
    sysout('开始加载远程任务 %s' % name)
    job = Job.get_job_fromdb(name)
    if job.server_host == '' or job.server_user=='' or job.server_script=='':
        raise MyScheduleException('远程配置信息不全')
    
    sysout('任务加载成功 \n=====================\n%s\n=====================' % job)
    
    #1/初始化配置
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(job.server_host,22,job.server_user, "")
    
    #2/初始化默认参数,替换脚本
    param_dict = get_param_dict(execid,param_dict_str)
    #拼接脚本命令,cd目录,执行脚本,获取脚本执行状态
    command = ' source /etc/bashrc;'
    if job.server_dir !='':
        work_dir,tmp_time = replace_param(job.server_dir,param_dict)
        sysout('配置脚本执行目录  work_dir:%s' % work_dir)
        command = 'cd %s;' % work_dir
    
    #给每个命令设备stdout不缓存的参数
    scripts = ';'.join(map(lambda x:'' if x.strip()=='' else 'stdbuf -o0 %s' % x , job.server_script.split(';')))
    
    command = command + scripts
    if not job.server_script.endswith(';'):
        command = command + ';'
    command = command+'echo "script execute status ["$?"]";'
    command,execute_time = replace_param(command,param_dict)
    sysout('生成完整执行脚本:%s' % (command))
    sysout('+++++++++++++任务初始化完成+++++++++++++++')
    #####更新job执行状态,启动######
    update_jobstatus(name,execute_time,execid,0)
    
    #3/检查跨项目或时间维度的依赖任务,未完成的两分钟检查一次,并实时输出到日志中
    if job.ext_dependencies != '':
        sysout('>>>>>>>>>>>>检查外部依赖完成情况')
        sysout('>>>>>>>>>>>>当前任务的基准时间:%s' % execute_time)
        sysout('>>>>>>>>>>>>依赖的外部任务配置:%s' % job.ext_dependencies)

        query_jobs = get_extdep_jobs(execute_time,job.ext_dependencies)
        wait_count = 1
        while True:
            flag,mes = JobStatus.is_ready(query_jobs)
            sysout('>>>>>>>>>>>>第%s次检查,依赖的外部任务准备情况:%s\n' % (wait_count,mes))
            
            if wait_count*120 > 86400:
                update_jobstatus(name,execute_time,execid,-1)
                raise MyScheduleException('依赖任务等待时间超过1天,请检查')
            if flag:
                update_jobstatus(name,execute_time,execid,None,True)
                break
            else:
                wait_count += 1
                time.sleep(120)

    #4/脚本执行,输出信息
    sysout('开始执行远程脚本:\n%s' % scripts)
    stdin, stdout, stderr = ssh.exec_command(command)
    error_flag = True
    sysout('---------------out 远程脚本日志输出----------------')
    while True:
        line = stdout.readline()
        if len(line) == 0:
            break
        sysout(line.strip())
        #sysout('%s,%s' % (time.time(),line))
        if line.find('script execute status [0]')>=0:
            error_flag=False
    sysout('---------------err 远程脚本错误输出-----------------')
    for line in stderr.readlines():
        sysout(line.replace('\n',''))
    sysout('---------------err end-----------------')
    ssh.close()

    #5/出错发邮件及短信,并抛出异常
    if error_flag:
        #####更新job执行状态,失败######
        update_jobstatus(name,execute_time,execid,-1)
        return True

    #####更新job执行状态,成功######
    exe_success(job,execid,start_time)
    update_jobstatus(name,execute_time,execid,1)
    
    return False

def sysout(msg):
    print msg
    sys.stdout.flush()

def append_file(file_path,msg):
    f = open(file_path,'a')
    f.write(msg)
    f.close()

#更新Job执行信息
def update_jobstatus(job_name,execute_time,execid,status=None,isUpdateStart=False):
    job_status = JobStatus()
    job_status.job_name = job_name
    job_status.execute_time = execute_time
    job_status.exec_id = execid
    if status!=None:
        job_status.status = status
        job_status.update_jobstatus()
        sysout('更新[%s]的执行状态[execute_time:%s][status:%s]' % (job_name,execute_time,status))
    elif isUpdateStart:
        job_status.update_starttime()

#成功通知
def exe_success(job,execid,start_time):
    sysout('发送成功通知')
    #邮件
    if job.success_email!='':
        title = '^_^ 任务执行成功azkaban[%s][%s]' % (job.project_name,job.name)
        content = '''
        <br>执行时间:%s
        <br>azkaban[%s][%s]任务执行成功
        <br><a href='https://localhost:8443/executor?execid=%s&job=%s'>点击查看日志</a>
        ''' % (start_time,job.project_name,job.name,execid,job.name)
        send_html(job.success_email,title,content)

    #短信
    if job.success_sms!='':
        content = '^_^ 任务执行成功azkaban[%s][%s]' % (job.project_name,job.name)
        send_msg(job.success_sms,content)

#失败告警
def exe_alarm(job,execid,start_time):
    sysout('发送失败告警')
    sql = '''
    select count(1) from execution_jobs t where t.exec_id=%s and job_id='%s'
    ''' % (execid,job.name)
    db = get_db()
    exec_count = db.fetch_one(sql)[0]
    sysout('exec_count:%s %s' % (exec_count,job.retries))
    retry_mes = '【!!需要重跑】'
    if job.retries > 0 and exec_count-1 < int(job.retries):
        retry_mes = '[将进行第%s次重试]' % (exec_count)

    #邮件
    if job.failure_email!='':
        title = 'T_T %sazkaban[%s][%s]任务执行出错[exec_id:%s]' % (retry_mes,job.project_name,job.name,execid)
        content = '''
        <br>执行时间:%s
        <br>azkaban[%s][%s]任务执行出错,请查看日志处理
        <br><a href='https://localhost:8443/executor?execid=%s&job=%s'>点击查看日志</a>
        ''' % (start_time,job.project_name,job.name,execid,job.name)
        send_html(job.failure_email,title,content)
    
    #短信接口，只需要在需要重跑时再发
    if exec_count > int(job.retries):
        content = '%sazkaban[%s][%s]任务执行出错[exec_id:%s],请处理' % (retry_mes,job.project_name,job.name,execid)
        #短信
        if job.failure_sms!='':
            content = '%sazkaban[%s][%s]任务执行出错[exec_id:%s],请处理' % (retry_mes,job.project_name,job.name,execid)
            send_msg(job.failure_sms,content)

#获取替换参数列表
def get_param_dict(execid,param_dict_str):
    sysout('获取所有替换参数值 ')
    #之前是用流程的启动时间来计算,在阻塞时会有问题,更新为通过执行时间来计算
    sql = '''select from_unixtime(floor(submit_time/1000),'%%Y-%%m-%%d %%H:%%i:%%s')  from execution_flows t where exec_id=%s''' % execid
    db = get_db()
    start_time, = db.fetch_one(sql)
    sysout('流程的提交时间为:%s' % start_time)
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
    #配置中的默认参数
    default_params = get_conf(CONFILE).items('job_replace_param')

    for k,v in default_params:
        param_dict[k] = v  
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
        sysout(e)

    sysout(param_dict)
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

        #判断小时级任务天级依赖
        scripts = Job.get_job_fromdb(ext_job['name']).server_script
        if ext_job['time_type']=='day' and (scripts.find('&[last_hour]')>=0 or scripts.find('&[cur_hour]')>=0):
            sysout('>>>>>>>>>>>>%s为小时级任务天级依赖，生成所有任务依赖' % ext_job['name'])
            for i in range(24):
                job_status = JobStatus()
                job_status.job_name = ext_job['name']
                job_status.execute_time = '%s%s' % (execute_time,'0%s' % i if i<10 else i)
                sysout('>>>>>>>>>>>>添加外部依赖任务检查项[%s][%s]' % (job_status.job_name,job_status.execute_time))
                query_jobs.append(job_status)
        else:
            job_status = JobStatus()
            job_status.job_name = ext_job['name']
            job_status.execute_time = execute_time
            sysout('>>>>>>>>>>>>添加外部依赖任务检查项[%s][%s]' % (job_status.job_name,job_status.execute_time))
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
        sysout('----[param_dict] %s' % param_dict)
    except:
        pass
    exe_job(job_name,execid,start_time,param_dict)

