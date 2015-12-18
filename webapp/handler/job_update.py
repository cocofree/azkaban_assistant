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
import time

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, '../../'))

from base.job_define import Job
from util.config import get_conf
CONFILE = "%s/../../conf/nice.cfg" % CURRENTPATH
azkaban_url = get_conf(CONFILE).get('web_param','azkaban_url')

#指标处理类
class JobUpdateHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        #更新完跳转到列表页
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
        #生成job
        attr_list = Job.get_attr_list()
        dependencies_box = self.get_argument('dependencies_box','')
        logging.info('>>>>>>>>>>>'+str(type(dependencies_box)))
        logging.info('>>>>>>>>>>>'+str(dependencies_box))
        job = Job()
        #动态加载字段,默认均为字符串
        for attr in attr_list:
            value = str(self.get_argument(attr,'')).strip()
            if value!='':
                setattr(job,attr,value)
                logging.info(attr+':'+value)
        #默认设置
        job.name = job.name.replace('.','-')
        job.updater = login_user
        job.update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if job.creator == '':
            job.creator = job.updater
            job.create_time = job.update_time
        #更新
        job.update_job()

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

        logging.info('[%s] update job [%s]' % (login_user,job.name))
        self.render('list.html',title=title,jobs=jobs,query_dict=query_dict,azkaban_url=azkaban_url)


