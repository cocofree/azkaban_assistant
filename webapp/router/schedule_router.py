#!/usr/bin/env python
#encoding:utf-8
'''
Author: wangxu
Email: wangxu@oneniceapp.com
''' 

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging  
import os
import tornado.ioloop
import tornado.web
import tornado.options
from handler.job_list import JobListHandler
from handler.job_to_update import JobToUpdateHandler
from handler.job_update import JobUpdateHandler
from handler.job_delete import JobDeleteHandler
from handler.job_upload import JobUploadHandler
from handler.job_check_exist import JobCheckExistHandler
from handler.hive_index import HiveIndexHandler
from handler.dag_edit import DagOpHandler

#默认端口
from tornado.options import define, options
define("port", default=8445, help="run on the given port", type=int)

#log日志配置
def init_logconfig():
    log_file = 'schedule_web.log'
    logging.basicConfig(level=logging.INFO,  
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s',  
                        datefmt='',  
                        filename=log_file,  
                        filemode='a')  

settings = {
    "template_path":os.path.join(os.path.dirname(__file__), "../templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "../static") 
}

#路径路由
application = tornado.web.Application([
    #(r"/upload", UploadHandler),
    (r"/job_list", JobListHandler),
    (r"/job_to_update", JobToUpdateHandler),
    (r"/job_update", JobUpdateHandler),
    (r"/job_delete", JobDeleteHandler),
    (r"/job_upload", JobUploadHandler),
    (r"/job_check_exist", JobCheckExistHandler),
    (r"/hive_index", HiveIndexHandler),
    (r"/dag",DagOpHandler),
],**settings)

if __name__ == "__main__":
    #初始化logging
    init_logconfig()
#    logging.info(template_path)
    logging.info('-----quality monitor service startup-------')
    tornado.options.parse_command_line()
    logging.info('port:%s' % options.port)

    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    #logging.info('----------service startup---------')
