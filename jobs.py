#!/usr/bin/env python
#coding:utf-8
import uwsgi
from uwsgidecorators import *
from configobj import ConfigObj
from weixinalarm import weixinalarm
import time
import logging
import urllib
import urllib2
import time
config=ConfigObj("etc/processmonitor.conf",encoding="UTF8")
corpid=config["weixin"]["corpid"]
secrect=config["weixin"]["secrect"]
weixinsender=weixinalarm(corpid=corpid,secrect=secrect)
times=int(config["alarm"]["times"])-2
import MySQLdb
conn=MySQLdb.connect(
        host=config["mysql"]["host"],
        port = int(config["mysql"]["port"]),
        user=config["mysql"]["user"],
        passwd=config["mysql"]["passwd"],
        db =config["mysql"]["db"],
        )   
cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
#日志模式初始化
logging.basicConfig(level="DEBUG",
                format='%(asctime)s  %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='./log/dark_status.log',
                filemode='a')
def alarmpolicy(mid,des):
    sql="select * from status_history where mid='%s';" %(str(mid))
    cur.execute(sql)
    status_info=cur.fetchall()
    logging.info(len(status_info))
    if len(status_info):
        if int(time.time())- round(float(status_info[0]["alarm_time"]))<= 3600 and int(status_info[0]["alarm_times"]) <= times:
	    if int(status_info[0]["alarm_times"]) == times:
                weixinsender.sendmsg(title="dark(当前时间最后一次报警)",description=des)
	    else:
                weixinsender.sendmsg(title="dark",description=des)
            count=int(status_info[0]["alarm_times"])+1
            update_sql = "UPDATE status_history SET alarm_times = '%d' WHERE mid = '%s'" % (count,mid)
            try:
                cur.execute(update_sql)  
                conn.commit()
            except Exception,e:
                logging.error("'%s' 数据更新异常:'%s'" %(mid,str(e)))
            else:
                logging.info("'%s' 数据更新成功'" %(mid))
        elif int(time.time())- round(float(status_info[0]["alarm_time"]))<= 3600 and int(status_info[0]["alarm_times"]) > times:
            logging.info("'%s'报警次数已达上限'" %(mid)) 
        elif time.time()- int(status_info[0]["alarm_time"])> 3600:
            weixinsender.sendmsg(title="dark",description=des)
            update_sql = "UPDATE status_history SET alarm_times = '%d',alarm_time='%d' WHERE mid = '%s'" % (0,time.time(),mid)
            try:
               cur.execute(update_sql) 
               conn.commit()
            except Exception,e:
                logging.error(str(e))
                logging.error("'%s' 数据更新异常:'%s'" %(mid,str(e)))
            else:
                logging.info("'%s' 数据更新成功'" %(mid))
    else:
        weixinsender.sendmsg(title="dark",description=des)
        update_sql = "INSERT INTO status_history (mid,last_status,alarm_time,alarm_times) VALUES ('%s','%d','%s','%d')" % (mid,0,str(time.time()),0)
        logging.info(update_sql)
        try:
           cur.execute(update_sql) 
           conn.commit()
        except Exception,e:
            logging.error(str(e))
            logging.error("'%s' 数据更新异常:'%s'" %(mid,str(e)))
        else:
            logging.info("'%s' 数据更新成功'" %(mid))
        
         

@timer(2)
def wxwarn(arg):
    sql="select * from dark_status;"
    cur.execute(sql)
    host_list=cur.fetchall()
    logging.info(host_list)
    if len(host_list):
        for host in host_list:
            if time.time() - time.mktime(time.strptime(str(host["update_time"]),"%Y-%m-%d %H:%M:%S")) > 300:
                des='上报错误('+str(host["mid"])+')'
                logging.info(des)
            elif host["new_config_version"] != host["old_config_version"] and host["dark_num"] == 0:
                des='程序未启动('+str(host["mid"])+')'
                logging.info(des)
            elif host["new_config_version"] == host["old_config_version"] and host["dark_num"] == 0:
                des='程序未启动('+str(host["mid"])+')'
                logging.info(des)
            else:
                logging.info("node is ok")
                continue 
            alarmpolicy(host["mid"],des)
    else:
        logging.info("未发现相关数据")

#@timer(30)
#def checkjsproxy(arg):
#    url = 'http://mx.93yxpt.com/forwardJs?js_url=http://apps.bdimg.com/cloudaapi/lightapp.js'
#    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
#    headers = {'User-Agent' : user_agent,'Referer':'http://www.qq.com'}
#    request = urllib2.Request(url,headers=headers)
#    n=0
#    for i in range(4):
#        try:
#            response = urllib2.urlopen(request,timeout=5)
#            page = response.read()
#        except Exception,e:
#            logging.info(str(e)) 
#            n=n+1
#        else:
#            if str(response.getcode()) == "200":
#               logging.info("jsproxy is ok") 
#            else:
#                n=n+1
#    if int(n) >= 3:
#        logging.info("jsproxy is not ok")
#        weixinsender.sendmsg(title="jscheck",description="jsproxy is not ok")
#    else:
#        logging.info("n="+str(n))

@filemon("/opt/dark_web_config/jobs.py")
def monitor_py(num):
    logging.info("jobs.py has been modified,reboot")
    uwsgi.reload()

@filemon("/opt/dark_web_config/main.py")
def monitor_py(num):
    logging.info("main.py has been modified,reboot")
    uwsgi.reload()
