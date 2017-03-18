#!/usr/bin/python
# coding=utf-8

import os
from ConfigParser import RawConfigParser


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


#@singleton
class Configuration:
    def __init__(self, configfile):
        config_home = os.getenv("CONF_HOME")
        if config_home:
            self._configFile = "%s/%s" % (config_home, configfile)
        else:
            self._configFile = configfile

        self._genConf()

    def _setConfigFile(self, configFile=None):
        """设置configure文件"""
        self._configFile = configFile
        if not self._configFile:
            raise Exception("配置文件不存在")
        self._genConf()

    def _genConf(self):
        if not self._configFile:
            raise Exception("没有配置文件")
        self._config = RawConfigParser()
        self._config.read(self._configFile)

    def get(self, sect, opt, default=None):
        if self._config.has_option(sect, opt):
            return self._config.get(sect, opt)
        return default

    def getint(self, sect, opt, default=None):
        if self._config.has_option(sect, opt):
            return self._config.getint(sect, opt)
        return default

    def items(self,sect):
        return self._config.items(sect)

def get_conf(confile="nice.cfg"):
    """创建配置文件"""
    return Configuration(confile)
