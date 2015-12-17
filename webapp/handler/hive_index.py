#!/usrbin/python
#encoding:utf-8
'''  
Author: wangxu 
Email: wangxu@oneniceapp.com
hive权限首页
'''  
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
import tornado.web
import json
import os

from model.hive_meta import HiveMeta

#指标处理类
class HiveIndexHandler(tornado.web.RequestHandler):
    #统一调用post方法
    def get(self):
        self.post()
    
    #action为操作类型
    def post(self):
        title = 'hive权限管理'
        #参数
        item_type_dict = {
            '':'',
            'DB_name':'库',
            'TABLE_name':'表',
            'ROLE_name':'角色',
            'USER_name':'用户',
            'ROLE_css':'success',
            'USER_css':'info',
            'DB_css':'warning',
            'TABLE_css':'danger',
        }
        item_type = self.get_argument('item_type','')
        item_value = self.get_argument('item_value','')
        #role_name = self.get_argument('role_name','')
        #user_name = self.get_argument('user_name','')
        #db_name = self.get_argument('db_name','')
        #table_name = self.get_argument('table_name','')
        #列表
        hive_meta = HiveMeta()
        
        item = {
            'type':item_type,
            'value':item_value,
            'type_dict':item_type_dict
        }
        map_items_list = [
            ['ROLE',hive_meta.getItems(item_type,'ROLE',item_value)],
            ['USER',hive_meta.getItems(item_type,'USER',item_value)],
            ['DB',hive_meta.getItems(item_type,'DB',item_value)],
            ['TABLE',hive_meta.getItems(item_type,'TABLE',item_value)]
        ]

        logging.info('hive meta index :type[%s],value[%s]' % (item_type,item_value))
        refer = 'hive_index.html'
        if item_type!= '' and item_value!='':
            refer = 'hive_item.html'
        self.render(refer,title=title,hive_meta=hive_meta,item=item,map_items_list=map_items_list)


