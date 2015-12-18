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

from base.job_define import Job

#指标处理类
class JobCheckExistHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        #任务
        name = self.get_argument('name','')
        logging.info('----name:[%s]' % name)
        job = None
        try:
            job = Job.get_job_fromdb(name)
        except:
            pass

        if job==None:
            self.write('non_exist')
        else:
            self.write('exist')



