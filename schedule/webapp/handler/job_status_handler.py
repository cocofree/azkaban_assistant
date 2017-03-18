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
from job_status import JobStatus

#指标处理类
class JobStatusHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        #任务
        job_name = self.get_argument('job_name','')
        exec_time = self.get_argument('execute_time','')
        logging.info('----job name:[%s]' % job_name)
        try:
            json = JobStatus.get_jobstatus_json(job_name,exec_time)
            self.write(json)
        except Exception,e:
            self.write('error:%s' % e)



