#!/usr/bin/python
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import paramiko
import logging

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, 'tinder/python'))

from util.helpers import mysql_helper

#配置文件
CONFILE = "%s/conf/nice.cfg" % CURRENTPATH

#获取数据库
def get_db():
    print CONFILE
    return mysql_helper.get_slave_db(db = "master_azkaban", confile = CONFILE)

#自定义异常
class MyScheduleException(Exception):
    def __init__(self,str):
        self.str = str
        print str
    def __str___(self):
        return repr(self.str)

#job对象
class Job(object):
    #初始化字段为空
    def __init__(self):
         attr_list = Job.get_attr_list()
         for i,attr in enumerate(attr_list):
             self.__setattr__(attr,'')

    @staticmethod
    def get_alljobs(name='',project_name='',server_host='',user='',login_user=''):
        #admin或写权限
        condition = ' 1=1 '
        if login_user!='':
            condition += ''' and project_name in (
            select p.name
            from project_permissions t 
            inner join projects p on t.project_id=p.id
            where (t.permissions&2>0 or t.permissions=134217728)
            and t.name='%s'
            )''' % login_user
        if name !='':
            condition += ' and name like "%%%s%%"' % name
        if project_name !='':
            condition += ' and project_name = "%s"' % project_name
        if server_host !='':
            condition += ' and server_host = "%s"' % server_host
        if user !='':
            condition += ' and (creator="%s" or updater="%s") ' % (user,user)
        
        attr_list = Job.get_attr_list()
        attrs = ','.join(attr_list)

        sql = '''
        select %s
        from kk_jobs
        where %s
        order by update_time desc
        ''' % (attrs,condition)
        logging.info(sql)
        db = get_db()
        rets = db.fetch_all(sql)
        job_list=[]
        for ret in rets:
            job = Job.generate_job(ret)
            if job!=None:
                job_list.append(job)
        return job_list
    
    @staticmethod
    def get_projects(login_user=''):
        sql = '''
        select p.name
        from project_permissions t 
        inner join projects p on t.project_id=p.id
        where (t.permissions&2>0 or t.permissions=134217728)
        and t.name='%s'
        order by name
        ''' % login_user
        db = get_db()
        rets = db.fetch_all(sql)
        projects = []
        for ret in rets:
            pname = ret[0]
            projects.append(pname)

        return projects

    @staticmethod
    def get_job_fromdb(name):
        attr_list = Job.get_attr_list()
        attrs = ','.join(attr_list)
        sql = '''
        select %s
        from kk_jobs
        where name='%s'
        ''' % (attrs,name)
        db = get_db()
        ret = db.fetch_one(sql)
        if ret==None:
            raise MyScheduleException('找不到任务[%s]' % name)
        else:
            return Job.generate_job(ret)
    
    #显示内容
    def __str__(self):
        mes = ''
        attr_list = Job.get_attr_list()
        for i,attr in enumerate(attr_list):
            #动态取值
            mes += '%s:\t%s\n' % (attr,self.__getattribute__(attr))
        return mes

    @staticmethod
    def get_attr_list():
        #按顺序返回表字段,方便构建,与查询SQL一致
        attr_list = ['id','name','project_name','flow_name',
        'server_host','server_user','server_dir','server_script',
        'dependencies','success_email','failure_email','success_sms','failure_sms',
        'retries','creator','updater','create_time','update_time','loc','ext_dependencies']
        return attr_list

    @staticmethod
    def generate_job(ret):
        if ret != None:
            job = Job()
            attr_list = Job.get_attr_list()
            for i,attr in enumerate(attr_list):
                #动态赋值
                job.__setattr__(attr, str(ret[i])) 
            '''
            job.id = str(ret[0])
            job.name = str(ret[1])
            job.project_name = str(ret[2])
            job.flow_name = str(ret[3])
            job.server_host = str(ret[4])
            job.server_user = str(ret[5])
            job.server_dir = str(ret[6])
            job.server_script = str(ret[7])
            job.dependencies = str(ret[8])
            job.success_email = str(ret[9])
            job.failure_email = str(ret[10])
            job.success_sms = str(ret[11])
            job.failure_sms = str(ret[12])
            job.retries = str(ret[13])
            job.creator = str(ret[14])
            job.updater = str(ret[15])
            job.create_time = str(ret[16])
            job.update_time = str(ret[17])
            '''
            return job
        else:
            return None

    #更新DAG图,依赖和节点位置
    @staticmethod
    def update_dag(username,nodes,links):
        #计算依赖
        job_deps = {}
        for link in links:
            job_from = link['from']
            job_to = link['to'] 
            deps = job_deps.get(job_to,set())
            deps.add(job_from)
            job_deps[job_to] = deps
        
        db = get_db()
        for node in nodes:
            name = node['key']
            loc = node['loc']
            deps = ','.join(list(job_deps.get(name,set())))
            sql = '''
            update kk_jobs
            set updater='%s',
                update_time=now(),
                dependencies='%s',
                loc='%s'
            where name='%s'
            ''' % (username,deps,loc,name)
            print sql
            db.execute(sql)

    #更新job入库
    def update_job(self):
        db = get_db()
        #先删后插
        self.delete_job()
        #插入
        columns='id'
        values='null'
        attr_list = Job.get_attr_list()
        for attr in attr_list:
            if hasattr(self,attr) and attr!='id':
                columns += ',%s' % attr
                #替换'防止SQL报错
                values += ",'%s'" % str(getattr(self,attr,'')).replace("'","\\'")

        insert_sql = '''
        insert into kk_jobs
        (%s)
        values
        (%s)
        ''' % (columns,values)
        print insert_sql
        db.execute(insert_sql)
    
    #删除job
    def delete_job(self):
        db = get_db()
        delete_sql = '''
        delete t from kk_jobs t where t.name='%s'
        ''' % self.name
        print delete_sql
        logging.info(delete_sql)
        db.execute(delete_sql)
        
    #删除job的依赖关系
    def delete_dependencies(self):
        name = self.name
        logging.info('开始删除与[%s]的依赖关系'% (self.project_name))
        all_jobs = Job.get_alljobs(login_user=self.updater,project_name=self.project_name)
        logging.info('开始删除与[%s]的个数'% (len(all_jobs)))
        for j in all_jobs:
            logging.info('[%s]与[%s]'% (j.name,j.dependencies))
            deps = set(j.dependencies.split(','))
            if name in deps:
                deps.remove(name)
                j.dependencies = ','.join(list(deps))
                j.update_job()
                logging.info('[%s]删除与[%s]的依赖关系'% (j.name,name))

    #azkaban的job文件内容
    def get_file_str(self):
        #节点配置
        if self.flow_name=='':
            str = 'type=command\n'
            str = str + 'command=python %s/exe_job.py %s ${azkaban.flow.execid} "${azkaban.flow.start.timestamp}" "${param_dict}"\n' % (CURRENTPATH,self.name)
        else:
            #子流程配置
            str = 'type=flow\n'
            #子流程的最近一个节点,会自动梳理出所依赖的上游节点
            str = str + 'flow.name=%s\n' % self.flow_name

        #依赖
        if self.dependencies!='':
            str = str + 'dependencies=%s\n' % self.dependencies
        if self.retries!='0':
            str = str + 'retries=%s\n' % self.retries
        if self.failure_email!='':
            str = str + 'failure.emails=%s\n' % self.failure_email
        if self.success_email!='':
            str = str + 'success.emails=%s\n' % self.success_email

        return str

if __name__=='__main__':
    job = Job()
    job.name = 'aaaa'
    job.project_name = 'bbbbb'
    job.server_script = "ccc''c'c"
    job.update_job()
