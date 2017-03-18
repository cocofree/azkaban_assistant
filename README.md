# azkaban
azkaban是一款非常给力的调度系统，由Linkedin开源，有以下主要功能：
- Web用户界面
- 调度工作流
- 认证/授权(权限的工作)
- 工作流和任务的日志记录和审计

# azkaban_assistant
在nice内部使用过程中，对azkaban进行了扩展，实现了以下功能：
- 任务管理WEB化（再也不用管理一堆文件了）
- 远程服务调用（所有任务都是执行远程服务脚本）
- 报警扩展（每个任务都可以配置邮件及短信报警了）
- 跨流程的依赖选项（跨项目甚至是跨时间维度的任务依赖）
- 图形化依赖配置（拖来拖去就把依赖关系配好了）
- LDAP权限认证（不用再给每一个人添加帐号了）

# 安装部署
基于azkaban-2.5.0开发，对源文件有所改动

## 环境准备
1. 安装python,以及依赖模块tornado、paramiko
2. 创建azkaban数据库,导入resouces/azkaban_create_table.sql (比原生多了两张表)

## 配置更新
1. 更新azkaban-executor/azkaban-web的配置文件（默认你们已经懂azkaban了，不清楚百度/谷歌）
2. 更新schedule/conf/nice.cfg
3. 工程azkaban-web中使用LDAP管理用户，提供了admin/admin_pwd这个默认超级管理员帐号。如果不支持LDAP，可改为默认方式，维护azkaban-users.xml中的用户即可

## 服务启动
1. 分别启动azkaban-executor/azkaban-web
2. 启动job管理服务：schedule/webapp下执行startup.sh/restart.sh,查看schedule_web.log日志是否有报错
3. 登陆https://hostname:8443，先创建项目，再点击“任务配置”进行配置

## 需要注意的地方
1. 因为所有任务都是远程服务调用，**所以需要提前打通azkaban启动用户到各服务器的ssh权限！！！**
2. 邮件、短信接口已预留好，在schdule/util/alarm.py自定义，默认只在日志中打印出信息
3. 远程脚本是否正常结束，是通过shell执行script execute status ["$?"]（最后一个脚本的状态返回值）来判断的，所以下面的脚本：
> test.sh
> > echooo 'hello world'
> > 
> > echo 'hello world'

虽然第一行出错，但最后一行继续执行并返回正确（相当于第一行的异常被捕获了），所以脚本仍认为是成功。使用的时候需要注意下

4. 在azkaban页面上kill任务时，仅会kill本地监听的脚本，远程脚本会继续执行下去（该特性暂时不做调整）

# 关于nice
专注于图片与标签的社交APP~
