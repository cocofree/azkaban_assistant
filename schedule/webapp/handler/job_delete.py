#!/usrbin/python
#encoding:utf-8
'''  
Author: wangxu 
Email: wangxu@oneniceapp.com
任务删除
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
class JobDeleteHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
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
        #任务删除
        name = self.get_argument('name','')
        job = Job.get_job_fromdb(name)
        #job = Job()
        #job.name = name
        job.updater = login_user
        job.unschedule_flow()
        job.delete_dependencies()
        job.delete_job()
        
        #列表
        jobs = Job.get_alljobs(query_name,query_project_name,query_server_host,query_user,login_user)

        query_dict = {
                'query_name':query_name,
                'query_project_name':query_project_name,
                'query_server_host':query_server_host,
                'query_user':query_user,
                'session_id':session_id,
                'login_user':login_user
        }

        logging.info('[%s] delete job [%s]' % (login_user,name))
        self.render('list.html',title=title,jobs=jobs,query_dict=query_dict)


