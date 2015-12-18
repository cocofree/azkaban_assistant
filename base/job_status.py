#!/usr/bin/python
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import paramiko
import logging

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, '..'))

from util.helpers import mysql_helper

#配置文件
CONFILE = "%s/../conf/nice.cfg" % CURRENTPATH

#获取数据库
def get_db():
    print CONFILE
    return mysql_helper.get_slave_db(db = "master_azkaban", confile = CONFILE)

#job执行记录
class JobStatus(object):
    #初始化字段为空
    def __init__(self,**keys):
         attr_list = JobStatus.get_attr_list()
         for i,attr in enumerate(attr_list):
             value = keys[attr] if keys.has_key(attr) else ''
             self.__setattr__(attr,value)
   
    
    @staticmethod
    def get_attr_list():
        #按顺序返回表字段,方便构建,与查询SQL一致
        attr_list = ['id','job_name','execute_time','exec_id','create_time','update_time','status']
        return attr_list

    @staticmethod
    def generate_jobstatus(ret):
        if ret != None:
            job_status = JobStatus()
            attr_list = JobStatus.get_attr_list()
            for i,attr in enumerate(attr_list):
                #动态赋值
                job_status.__setattr__(attr, str(ret[i])) 
            return job_status
        else:
            return None
    
    #获取job状态信息
    @staticmethod
    def get_jobstatus(job_name,execute_time):
        attr_list = JobStatus.get_attr_list()
        attrs = ','.join(attr_list)
        sql = '''
        select %s
        from kk_jobs_status
        where job_name='%s' and execute_time=%s
        ''' % (attrs,job_name,execute_time)
        
        db = get_db()
        ret = db.fetch_one(sql)
        if ret==None:
            return None
        else:
            return JobStatus.generate_jobstatus(ret) 

    #更新
    def update_jobstatus(self):
        sql = '''
        insert into kk_jobs_status (job_name,execute_time,exec_id,status)
        values
        ('%s',%s,%s,%s)
        ON DUPLICATE KEY UPDATE status=values(status),exec_id=values(exec_id)
        ''' % ( self.job_name,self.execute_time,self.exec_id,self.status)
        #logging.info(sql)
        #print sql
        db = get_db()
        db.execute(sql)
    
    #依赖job是否准备完毕//分不分这么细,失败>未创建>正在执行>成功
    @staticmethod
    def is_ready(query_jobs):
        query_size = len(query_jobs)
        flag = True
        if query_size==0:
            return True,'无外部依赖任务'
        #查询所有已存在的任务状态
        condition_list = []
        for j in query_jobs:
            tmp = "(t.job_name='%s' and execute_time=%s)" % (j.job_name,j.execute_time)
            condition_list.append(tmp)
        sql = '''
        select t.job_name,t.execute_time,t.status 
        from kk_jobs_status t 
        where (%s)
        ''' % ' or '.join(condition_list)
        #print sql
        db = get_db()
        ret = db.fetch_all(sql)

        #判断状态
        total = len(ret)
        run_jobs = []
        fail_jobs = []
        success_jobs = []
        for row in ret:
            status = int(row[2])
            job_name = row[0]
            if status==-1:
                fail_jobs.append(job_name)
            elif status==0:
                run_jobs.append(job_name)
            elif status==1:
                success_jobs.append(job_name)
        if query_size==len(success_jobs):
            return True,'所有外部依赖任务已执行完毕'
        else:
            mes = '已成功%s个[%s],正在执行%s个[%s],已失败%s个[%s],剩下任务未创建' % (len(success_jobs),','.join(success_jobs),len(run_jobs),','.join(run_jobs),len(fail_jobs),','.join(fail_jobs)) 
            return False,mes


if __name__=='__main__':
    '''
    job_status = JobStatus(execute_time=214241)
    job_status.job_name = 'a'
    #job_status.execute_time = 20151210
    job_status.status = -1
    print job_status.execute_time
    #job_status.update_jobstatus()
    '''
    #print JobStatus.get_jobstatus('b',20151210)
    jobs = []
    for i in range(5):
        v = 2015121415-i
        print v
        job =  JobStatus(job_name='ods-gapi_access_log',execute_time=v)
        jobs.append(job)

    print JobStatus.is_ready(jobs)


