#!/usrbin/python
#encoding:utf-8
'''  
Author: wangxu 
Email: wangxu@oneniceapp.com
任务上传
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

from base.generate_files import login_and_upload
from util.config import get_conf
CONFILE = "%s/../../conf/nice.cfg" % CURRENTPATH
azkaban_url = get_conf(CONFILE).get('web_param','azkaban_url')

#指标处理类
class JobUploadHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        #更新完跳转到列表页
        title = '任务上传'
        #需要先从azkaban登陆
        #session_id = self.get_argument('session_id','')
        #login_user = self.get_argument('login_user','')
        #if session_id=='' or login_user=='':
        #    self.render('to_login.html')
        #    return
        #上传结果
        username = self.get_argument('username','')
        login_user = username
        password = self.get_argument('password','')
        session_id,result_list = login_and_upload(username,password)
            
        query_dict = {
                'session_id':session_id,
                'login_user':login_user
        }

        logging.info('[%s] upload jobs' % (login_user))
        self.render('upload.html',title=title,result_list=result_list,query_dict=query_dict,azkaban_url=azkaban_url)


