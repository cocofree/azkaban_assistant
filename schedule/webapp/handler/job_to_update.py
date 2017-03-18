#!/usrbin/python
#encoding:utf-8
'''  
Author: wangxu 
Email: wangxu@oneniceapp.com
任务更新
'''  
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
import tornado.web
import json
import os

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, '../../'))

from job_define import Job

#指标处理类
class JobToUpdateHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        op = self.get_argument('op','')
        if op=='show':
            name = self.get_argument('name','')
            job = Job.get_job_fromdb(name)
            self.write('<pre>%s</pre>' %str(job))
            return

        title = '任务配置'
        #需要先从azkaban登陆
        session_id = self.get_argument('session_id','')
        login_user = self.get_argument('login_user','')
        if session_id=='' or login_user=='':
            self.render('to_login.html')
            return
        #参数
        query_name = self.get_argument('query_name','')
        query_project_name = self.get_argument('query_project_name','')
        query_server_host = self.get_argument('query_server_host','')
        query_user = self.get_argument('query_user','')
        #任务
        name = self.get_argument('name','')
        is_copy = self.get_argument('is_copy','false')
        job = Job()
        if name !='':
            job = Job.get_job_fromdb(name)
        if is_copy == 'true':
            job.name = ''
            job.loc = ''
        projects = Job.get_projects(login_user)
        jobs = Job.get_alljobs(login_user=login_user)
        all_jobs = Job.get_alljobs()

        query_dict = {
                'query_name':query_name,
                'query_project_name':query_project_name,
                'query_server_host':query_server_host,
                'query_user':query_user,
                'session_id':session_id,
                'login_user':login_user
        }

        logging.info('to update job [%s]' % name)
        self.render('to_update.html',title=title,job=job,jobs=jobs,all_jobs=all_jobs,projects=projects,query_dict=query_dict)


