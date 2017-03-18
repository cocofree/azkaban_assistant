#!/usr/bin/python
# coding=utf-8

import os

def send_html(mailto,title,content):
    print '假装在发送邮件，请自行接入（schedule/util/alarm）'
    print mailto
    print title

def send_msg(msgto,content):
    print '假装在发送短信，请自行接入（schedule/util/alarm）'
    print msgto
    print content

if __name__=='__main__':
    send_msg(11111,'aa')
