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
import datetime
import traceback
CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, '../../'))

from job_define import Job
from generate_files import generate_files,get_session_id
from azkaban_api import schedule_flow,execute_flow,fetchexec_flow


#web接口类
class JobApiHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        self.username = 'azkaban_api'
        self.password = 'azkaban_pwd'
        self.session_id = get_session_id(self.username,self.password)
        
        action = self.get_argument('action')
        method = getattr(self,action)
        
        #查询类
        get_action = set(['get_alljobs'])
        if action in get_action:
            method()    
        else:
            resp = {'status':200,'message':''}
            try:
                result = method()
                if result!=None:
                    resp = result
            except Exception,e:
                logging.info(traceback.format_exc())
                resp['status'] = 400
                resp['message'] = str(e)
       
            logging.info(str(resp))
            self.write(json.dumps(resp))


    def upload_project(self):
        #上传结果
        project_name = self.get_argument('project_name')
        result_list = generate_files(self.username,self.session_id,project_name)
        logging.info(str(result_list))
        if len(result_list) == 0:
            raise Exception('unexist project_name')
        result = result_list[0]
        if result['upload_flag'] == 'false':
            raise Exception(str(result_list))

        logging.info('[%s] upload jobs' % (self.username))

    def schedule_flow(self):
        project_name = self.get_argument('project_name')
        flow_name = self.get_argument('flow_name')
        schedule_time = self.get_argument('schedule_time')
        period =  self.get_argument('period')
        
        result = schedule_flow(self.session_id,project_name,flow_name,schedule_time,period) 
         
        logging.info(str(result))

    def get_alljobs(self):
        job_list = Job.get_alljobs()
        jobs = map(lambda x:{'name':x.name,'project_name':x.project_name}, job_list)
        self.write(json.dumps(jobs))

    def delete_job(self):
        login_user = self.username
        name = self.get_argument('name')
        
        try:
            job = Job.get_job_fromdb(name)
        except:
            raise Exception('not fonud job[%s]' % name)
        job.updater = login_user
        
        flag,mes = job.has_job_permission()
        logging.info('check job permission [%s] [%s]' % (flag,mes))
        if not flag:
            raise Exception(mes)
        
        job.unschedule_flow(self.session_id)
        job.delete_dependencies()
        job.delete_job()
        logging.info('[%s]delete job [%s]' % (login_user,name))

    def execute_flow(self):
        project_name = self.get_argument('project_name')
        flow_name = self.get_argument('flow_name')

        param_dict = self.request.arguments
        del param_dict['action']

        result = execute_flow(self.session_id,project_name,flow_name,param_dict)
        
        return result

    def fetchexec_flow(self):
        execid = self.get_argument('execid')

        result = fetchexec_flow(self.session_id,execid)
        return result

    def update_job(self):
        login_user = self.username
        #必需参数
        required_args = ['name','project_name','server_host','server_user','server_script','server_dir']
        for arg in required_args: 
            self.get_argument(arg)
        #生成job
        attr_list = Job.get_attr_list()
        #dependencies_box = self.get_argument('dependencies_box','')
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
        flag,mes = job.has_job_permission()
        
        logging.info('check job permission [%s] [%s]' % (flag,mes))
        if not flag:
            raise Exception(mes)

        job.update_job()

        logging.info('[%s] update job [%s]' % (login_user,job.name))
        
