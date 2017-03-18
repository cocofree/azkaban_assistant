#!/usr/bin/python
#encoding:utf-8
'''
生成azkaban的配置文件
'''
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import zipfile
import urllib
import urllib2
import json
import commands

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, 'tinder/python'))

#配置文件
CONFILE = "%s/conf/nice.cfg" % CURRENTPATH

#azkaban的session_id
def get_session_id(username='',password=''):
    try:
        #请求路径
        url = 'https://localhost:8443/'
        params={}
        params['action']='login'
        if username=='' or password=='':
            username = raw_input('LDAP username:')
            password = raw_input('LDAP password:')
        params['username']= username
        params['password']= password
        data = urllib.urlencode(params) 
        req = urllib2.Request(url,data)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        print res
        obj = json.loads(res)
        return  obj['session.id']
    except Exception,e:
        print e
        return ''

if __name__ == '__main__':
    session_id = get_session_id()
    #generate_files(session_id)

