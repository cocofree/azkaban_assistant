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

from util.helpers import mysql_helper
from job_define import Job,MyScheduleException
#配置文件
CONFILE = "%s/conf/nice.cfg" % CURRENTPATH

#执行脚本
def generate_files(username='',session_id='',project_name=''):
    #1/清空所有文件
    dir_path = '%s/../files/' % CURRENTPATH
    os.system('rm -rf %s' % dir_path)
    os.system('mkdir %s' % dir_path)
    #2/生成文件目录
    
    #3/生成文件
    job_list = Job.get_alljobs(login_user=username,project_name=project_name)
    for job in job_list:
        #2/生成文件目录
        project_path = dir_path+job.project_name+'/'
        zip_path = dir_path+job.project_name+'.zip'
        if not os.path.exists(project_path):
            os.system('mkdir %s' % project_path)
        #3/生成文件
        file_name = job.name+'.job'
        file_path = project_path+file_name
    
        f = open(file_path,'wb')
        f.write(job.get_file_str())
        f.close()
        
        #4/zip包
        zf = zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED)
        #遍历所有文件
        for dirpath, dirnames, filenames in os.walk(project_path):
            for filename in filenames:
                zf.write(os.path.join(dirpath,filename))
        zf.close()
        
        print '任务%s.job文件已生成' % job.name

    result_list = []
    #5/上传zip包
    for filename in os.listdir(dir_path):
        if filename.endswith('.zip'):
            zip_path = dir_path+'/'+filename
            project_name = filename.replace('.zip','')
            result = upload_zip(session_id,project_name,zip_path)
            result_list.append(result)

    print result_list
    return result_list

def login_and_upload(username,password):
    session_id = get_session_id(username,password)
    result_list = generate_files(username,session_id)
    return session_id,result_list
    

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

#azkaban上传任务流程
def upload_zip(session_id,project_name,zip_path):
    result_dict = {'project_name':project_name,'upload_flag':'false'}
    try:
        #请求路径
        url = 'https://localhost:8443/manager'
        command = '''curl -k -i -H "Content-Type: multipart/mixed" -X POST --form 'session.id=%s' --form 'ajax=upload' --form 'file=@%s;type=application/zip' --form 'project=%s' %s''' % (session_id,zip_path,project_name,url)
        print '>>>>',command
        status,result = commands.getstatusoutput(command)
        
        #生成结果信息
        if status!=0:
            result_dict['mes'] = result
        else:
            if result.find('error')>=0:
                if result.find('{')>=0:
                    result = result[result.find('{'):]
                if result.find('Login error')>=0:
                    result = result[result.find('Login error'):]
                result_dict['mes'] = result
            else:
                result_dict['upload_flag'] = 'true'
                if result.find('{')>=0:
                    result = result[result.find('{'):]
                result_dict['mes'] = result
        return result_dict
    except Exception,e:
        print e
        result_dict['mes'] = str(e)
        return result_dict

if __name__ == '__main__':
    session_id = get_session_id()
    #generate_files(session_id)

