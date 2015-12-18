#!/usrbin/python
#encoding:utf-8
'''  
Author: wangxu 
Email: wangxu@oneniceapp.com
任务列表
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

from base.job_define import Job
from util.config import get_conf
CONFILE = "%s/../../conf/nice.cfg" % CURRENTPATH
azkaban_url = get_conf(CONFILE).get('web_param','azkaban_url')
#指标处理类
class JobListHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        title = '调度任务列表'
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

        logging.info('query job list [%s]' % query_dict)
        self.render('list.html',title=title,jobs=jobs,query_dict=query_dict,azkaban_url=azkaban_url)


