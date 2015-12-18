#!/usrbin/python
#encoding:utf-8
'''  
Author: wangxu 
Email: wangxu@oneniceapp.com
DAG图依赖关系更新
'''  
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
import tornado.web
import json
import os
import traceback
import StringIO

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, '../../'))

from base.job_define import Job

#指标处理类
class DagOpHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        #需要先从azkaban登陆
        op = self.get_argument('op','')
        login_user = self.get_argument('login_user','')
        project_name = self.get_argument('project_name','')
        if login_user=='':
            self.render('to_login.html')
            return

        if op=='edit' :
            #项目
            jobs = Job.get_alljobs(project_name=project_name,login_user=login_user)
            has_dependce_jobs = set()
            is_dependced_jobs = set()

            for job in jobs:
                if job.dependencies != '':
                    has_dependce_jobs.add(job.name)
                    is_dependced_jobs.update(job.dependencies.split(','))
            
            for job in jobs:
               job.has_dependce = True if job.name in has_dependce_jobs else False
               job.is_dependced = True if job.name in is_dependced_jobs else False

            logging.info('to edit dag [%s][%s]' % (project_name,login_user))
            self.render('dag_edit.html',project_name=project_name,jobs=jobs,login_user=login_user)
        elif op=='save' :
            try:
                nodes = self.get_argument('nodes','')
                links = self.get_argument('links','')
                ns = json.loads(nodes)
                ls = json.loads(links)
                
                Job.update_dag(login_user,ns,ls)
                logging.info('edit dag [%s][%s]' % (project_name,login_user))
                self.write("保存成功")
            except Exception,e:
                logging.info(e)
                self.write('保存失败[%s]' % str(e))

