#!/usr/bin/env python
#coding:utf-8
import uwsgi
from uwsgidecorators import *
from weixinalarm import weixinalarm
import time
import logging
import urllib
import urllib2
corpid="ww3a7da140a1da4c3b"
secrect="HC-iSwV8-ZIKUva4XUfUfozYdbZQcdECXQZSMjZBW-g"
weixinsender=weixinalarm(corpid=corpid,secrect=secrect)
import MySQLdb
conn=MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='root',
        passwd='chinatt_1347',
        db ='darkinfo',
        )   
cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
#日志模式初始化
logging.basicConfig(level="DEBUG",
                format='%(asctime)s  %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='./log/dark_status.log',
                filemode='a')
@timer(180)
def wxwarn(arg):
    sql="select * from dark_status;"
    cur.execute(sql)
    host_list=cur.fetchall()
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
        weixinsender.sendmsg(title="dark",description=des)

@timer(30)
def checkjsproxy(arg):
    url = 'http://mx.93yxpt.com:12000/forwardJs?js_url=http://apps.bdimg.com/cloudaapi/lightapp.js'
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
    headers = {'User-Agent' : user_agent,'Referer':'http://www.qq.com'}
    request = urllib2.Request(url,headers=headers)
    n=0
    for i in range(4):
        try:
            response = urllib2.urlopen(request,timeout=5)
            page = response.read()
        except Exception,e:
            logging.info(str(e)) 
            n=n+1
        else:
            if str(response.getcode()) == "200":
               logging.info("jsproxy is ok") 
            else:
                n=n+1
    if int(n) >= 3:
        logging.info("jsproxy is not ok")
        weixinsender.sendmsg(title="jscheck",description="jsproxy is not ok")
    else:
        logging.info("n="+str(n))

@filemon("/opt/dark_web_config/jobs.py")
def monitor_py(num):
    logging.info("jobs.py has been modified,reboot")
    uwsgi.reload()

@filemon("/opt/dark_web_config/main.py")
def monitor_py(num):
    logging.info("main.py has been modified,reboot")
    uwsgi.reload()
