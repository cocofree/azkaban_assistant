#!/usr/bin/python
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import paramiko
import logging

CURRENTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENTPATH, '../../tinder/python'))

from util.helpers import mysql_helper

#配置文件
CONFILE = "%s/../../conf/nice.cfg" % CURRENTPATH

#获取数据库
def get_db():
    return mysql_helper.get_slave_db(db = "hive_meta", confile = CONFILE)

#hive对象
class HiveMeta(object):
    #初始化字段为空
    def __init__(self):
        #用户/角色/库/表
        self.user_list = HiveMeta.get_users()
        self.role_list = HiveMeta.get_roles()
        self.db_list = HiveMeta.get_dbs()
        self.table_list = HiveMeta.get_tables()

        #DICT映射
        self.itemmap_list = HiveMeta.get_item_maps()

    #获取映射关系的值,value和priv
    def getItems(self,key_type,value_type,key_data):
        item_list = []
        for item_map in self.itemmap_list:
            if item_map.key_type == key_type and item_map.value_type == value_type and item_map.key_data == key_data:
                value = [item_map.value_data,item_map.priv]
                item_list.append(value)
        return item_list

    #获取所有的映射关系,所有元素放在KEY中
    @staticmethod
    def get_item_maps():
        sql = '''
        select 'DB' key_type,'TABLE' value_type,d.NAME as data_key,concat(d.NAME,'.',t.TBL_NAME) as data_value,'' priv
        from TBLS t inner join DBS d on t.DB_ID=d.DB_ID
        union all
        select 'TABLE','DB',concat(d.NAME,'.',t.TBL_NAME),d.NAME ,'' priv
        from TBLS t inner join DBS d on t.DB_ID=d.DB_ID
        union all
        select 'ROLE',t.PRINCIPAL_TYPE,ROLE_NAME,t.PRINCIPAL_NAME,''
        from ROLE_MAP t inner join ROLES r on t.ROLE_ID=r.ROLE_ID
        union all
        select t.PRINCIPAL_TYPE,'ROLE',t.PRINCIPAL_NAME,ROLE_NAME,''
        from ROLE_MAP t inner join ROLES r on t.ROLE_ID=r.ROLE_ID
        union all
        select t.PRINCIPAL_TYPE,'DB',t.PRINCIPAL_NAME,NAME,group_concat(DB_PRIV) 
        from DB_PRIVS t 
        inner join DBS d on t.DB_ID=d.DB_ID 
        group by  t.PRINCIPAL_TYPE,NAME,t.PRINCIPAL_NAME
        union all
        select 'DB',t.PRINCIPAL_TYPE,NAME,t.PRINCIPAL_NAME,group_concat(DB_PRIV) 
        from DB_PRIVS t 
        inner join DBS d on t.DB_ID=d.DB_ID 
        group by  t.PRINCIPAL_TYPE,NAME,t.PRINCIPAL_NAME
        union all
        select t.PRINCIPAL_TYPE,'TABLE',TBL_NAME,t.PRINCIPAL_NAME,group_concat(TBL_PRIV) 
        from TBL_PRIVS t 
        inner join (select t.TBL_ID,concat(d.NAME,'.',t.TBL_NAME) as TBL_NAME from TBLS t inner join DBS d on t.DB_ID=d.DB_ID) d on t.TBL_ID=d.TBL_ID 
        group by  t.PRINCIPAL_TYPE,TBL_NAME,t.PRINCIPAL_NAME
        union all
        select 'TABLE',t.PRINCIPAL_TYPE,t.PRINCIPAL_NAME,TBL_NAME,group_concat(TBL_PRIV) 
        from TBL_PRIVS t 
        inner join (select t.TBL_ID,concat(d.NAME,'.',t.TBL_NAME) as TBL_NAME from TBLS t inner join DBS d on t.DB_ID=d.DB_ID) d on t.TBL_ID=d.TBL_ID 
        group by  t.PRINCIPAL_TYPE,TBL_NAME,t.PRINCIPAL_NAME
        '''
        db = get_db()
        rets = db.fetch_all(sql)
        itemmap_list = []
        for ret in rets:
            item_map = HiveItemMap(ret)
            itemmap_list.append(item_map)
        return itemmap_list

    @staticmethod
    def get_roles():
        sql = '''
        select ROLE_NAME from ROLES
        '''
        db = get_db()
        rets = db.fetch_all(sql)
        role_list=[]
        for ret in rets:
            role_list.append(ret[0])
        return role_list

    @staticmethod
    def get_users():
        sql = '''
        select PRINCIPAL_NAME from (
        select distinct t.PRINCIPAL_NAME from ROLE_MAP t
        union
        select distinct t.PRINCIPAL_NAME from DB_PRIVS t where t.PRINCIPAL_TYPE='USER'
        union
        select distinct t.PRINCIPAL_NAME from TBL_PRIVS t where t.PRINCIPAL_TYPE='USER'
        )tmp 
        order by PRINCIPAL_NAME
        '''
        db = get_db()
        rets = db.fetch_all(sql)
        user_list=[]
        for ret in rets:
            user_list.append(ret[0])
        return user_list
    
    @staticmethod
    def get_dbs():
        sql = '''
        select NAME from DBS
        '''
        db = get_db()
        rets = db.fetch_all(sql)
        db_list=[]
        for ret in rets:
            db_list.append(ret[0])
        return db_list

    @staticmethod
    def get_tables():
        sql = '''
        select concat(d.NAME,'.',t.TBL_NAME),t.TBL_NAME,d.NAME from TBLS t inner join DBS d on t.DB_ID=d.DB_ID
        '''
        db = get_db()
        rets = db.fetch_all(sql)
        table_list=[]
        for ret in rets:
            table_list.append(ret[0])
        return table_list

#映射关系,方便使用
class HiveItemMap(object):
    #初始化数据
    def __init__(self,row):
        self.key_type = row[0]
        self.value_type = row[1]
        self.key_data = row[2]
        self.value_data = row[3]
        self.priv = row[4]
        
    
if __name__=='__main__':
    h = HiveMeta()
    print h.user_list
