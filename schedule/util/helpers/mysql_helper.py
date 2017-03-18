#!/usr/bin/python
#encoding:utf-8

import os
import sys
import MySQLdb 
from util.config import get_conf

reload(sys)
sys.setdefaultencoding("utf-8")

class DBBase:
    
    db = None
    cursor = None

    def __init__(self, dbconfig):
        self._conf = get_conf(dbconfig)

    def _connect(self, key, ttype):
        _host = self._conf.get(key, "host")
        _port = self._conf.getint(key, "port")
        _user = self._conf.get(key, "username")
        _pass = self._conf.get(key, "password")
        _db = self._conf.get(key, "db")
        _connect_timeout = self._conf.getint(key, "connect_timeout", 10)
        #_read_timeout = self._conf.get(key, "read_timeout")
        #_write_timeout = self._conf.get(key, "write_timeout")
        _charset = self._conf.get(key, "charset")

        configs = {
                "host":_host,
                "port":_port,
                "user":_user,
                "passwd":_pass,
                "db":_db,
                "charset":_charset,
                "connect_timeout":_connect_timeout,
                #"read_timeout":_read_timeout,
                #"write_timeout":_write_timeout,
                "charset":_charset,
            }
        self.db = MySQLdb.connect(**configs)
        self.db.autocommit(True)
    
        if ttype == "tuple":
            self.cursor = self.db.cursor()
        else:
            self.cursor = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def __del__(self):
        self._close(self.db, self.cursor)

    def _close(self, db, cursor):
        if db:
            try:
                db.close()
            except:
                pass
        if cursor:
            try:
                cursor.close()
            except:
                pass

def valid_sql(func):
    def decorator(*args, **kwargs):
        if not args[1]:
            raise Exception("empty sql")
        return func(*args, **kwargs)
    return decorator

class MysqlHelper(DBBase):

    def __init__(self, choice_db, confile, ttype='tuple'):
        DBBase.__init__(self, confile)
        self.ttype = ttype
        self.choice_db = choice_db
        self._connect(self.choice_db, self.ttype)
    
    def escape_string(self, value):
        return self.db.escape_string(value)
    
    def check_alive(self):
        try:
            self.db.ping()
        except Exception, e:
            sys.stderr.write("%s\n" % repr(e))
            sys.stderr.flush()
            n = 5
            while n > 0:
                n -= 1
                try:
                    self._close(self.db, self.cursor)
                    self._connect(self.choice_db, self.ttype)
                    return
                except Exception, e:
                    sys.stderr.write("%s\n" % repr(e))
                    sys.stderr.flush()
                    continue

    @valid_sql
    def fetch_many(self, sql, size = 100):
        self.check_alive()
        self.cursor.execute(sql)
        while True:
            ret = self.cursor.fetchmany(size)
            if ret:
                yield ret
            else:
                break

    @valid_sql
    def fetchmany(self, sql, size = 100):
        self.check_alive()
        self.cursor.execute(sql)
        while True:
            ret = self.cursor.fetchmany(size)
            if ret:
                yield ret
            else:
                break

    def fetch_all(self, sql):
        self.check_alive()
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def fetchall(self, sql):
        self.check_alive()
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def fetch_one(self, sql):
        self.check_alive()
        self.cursor.execute(sql)
        return self.cursor.fetchone()
    
    def fetchone(self, sql):
        self.check_alive()
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def execute(self, sql):
        self.check_alive()
        self.cursor.execute(sql)
        #self.db.commit()

    def execute_many(self, sql, values = []):
        self.check_alive()
        self.cursor.executemany(sql, values)
        #self.db.commit()
    
    def executemany(self, sql, values = []):
        self.check_alive()
        self.cursor.executemany(sql, values)
        #self.db.commit()

def get_slave_db(db = "slave_db_12", ttype = "tuple", confile = "nice.cfg"):
    '''获取统计从库'''
    return MysqlHelper(choice_db = db, ttype = ttype, confile=confile)
