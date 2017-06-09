#!/usr/bin/env python
#coding:utf-8
from weixinalarm import weixinalarm
import time
corpid="ww3a7da140a1da4c3b"
secrect="HC-iSwV8-ZIKUva4XUfUfozYdbZQcdECXQZSMjZBW-g"
weixinsender=weixinalarm(corpid=corpid,secrect=secrect)
import MySQLdb
conn=MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='root',
        passwd='chinatt()^^*',
        db ='darkinfo',
        )
cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
def wxwarn(title):
    sql="select * from dark_status;"
    cur.execute(sql)
    host_list=cur.fetchall()
    for host in host_list:
        if time.time() - time.mktime(time.strptime(str(host["update_time"]),"%Y-%m-%d %H:%M:%S")) > 300:
            des='上报错误('+str(host["mid"])+')'
            print des 
        elif host["new_config_version"] != host["old_config_version"] and host["dark_num"] == 0:
            des='程序未启动('+str(host["mid"]+')'
            print des 
        elif host["new_config_version"] == host["old_config_version"] and host["dark_num"] == 0:
            des='程序未启动('+str(host["mid"]+')'
            print des 
        else:
            pass
        weixinsender.sendmsg(title=title,description=des)
