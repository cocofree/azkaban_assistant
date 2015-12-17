#!/usr/bin/python
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import paramiko

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, 'tinder/python'))

from util.helpers import mysql_helper
from job_define import Job

if __name__=='__main__':
    attr_list = Job.get_attr_list()
    for attr in attr_list:
        print '''<div class="form-group">
<label for="%s" class="col-sm-2 control-label">%s</label>
<div class="col-sm-10">
<input type="text" class="form-control" id="%s" name='%s' placeholder="%s" value="{{ job.%s}}">
</div></div>''' % (attr,attr,attr,attr,attr,attr)
    
