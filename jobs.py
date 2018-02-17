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
reload(sys)
sys.setdefaultencoding('utf8')
config=ConfigObj("etc/processmonitor.conf",encoding="UTF8")
secrect=config["weixin"]["secrect"]
agentid=config["weixin"]["agentid"]
corpid=config["weixin"]["corpid"]
weixinsender=weixinalarm(corpid=corpid,secrect=secrect,agentid=agentid)
times=int(config["alarm"]["times"])
import MySQLdb
from DBUtils.PersistentDB import PersistentDB
#try:
#    pool = PooledDB(MySQLdb,10,host=config["mysql"]["host"],user=config["mysql"]["user"],passwd=config["mysql"]["passwd"],db=config["mysql"]["db"],port=int(config["mysql"]["port"]))
#except Exception,e:
#    weixinsender.sendmsg(title="数据库连接错误",description=str(e))
#    logging.error(str(e))
#    uwsgi.reload()
#else:
#    logging.info("数据库连接成功")
class MysqlConnectionPool(object):
    __pool = None;
    def __enter__(self):
        self.conn = self.__getConn();
        self.cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor);
        return self;

    def __getConn(self):
        if self.__pool is None:
            self.__pool = PersistentDB(creator=MySQLdb,host=config["mysql"]["host"],user=config["mysql"]["user"],passwd=config["mysql"]["passwd"],db=config["mysql"]["db"],port=int(config["mysql"]["port"]))

        return self.__pool.connection()

    def __exit__(self, type, value, trace):
        self.cursor.close()
        self.conn.close()

def getMysqlConnection():
    return MysqlConnectionPool()
#日志模式初始化
logging.basicConfig(level="DEBUG",
                format='%(asctime)s  %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='./log/dark_status.log',
                filemode='a')
def alarmpolicy(mid,des,itemtype):
    with getMysqlConnection() as db:
        sql="select * from status_history where mid='%s' and item_type='%s';" %(str(mid),itemtype)
        db.cursor.execute(sql)
        status_info=db.cursor.fetchall()
        if len(status_info):
            if int(time.time())- round(float(status_info[0]["alarm_time"]))<= 3600 and int(status_info[0]["alarm_times"]) <= times:
                if int(status_info[0]["alarm_times"]) == times:
                    weixinsender.sendmsg(title=itemtype+"(当前时间最后一次报警)",description=des)
                else:
                    logging.info(des+"["+str(int(status_info[0]["alarm_times"])+1)+"]")
                    logging.info(int(time.time())- round(float(status_info[0]["alarm_time"])))
                    logging.info(status_info[0]["alarm_times"])
                    weixinsender.sendmsg(title=itemtype,description=des+"["+str(int(status_info[0]["alarm_times"])+1)+"]")
                count=int(status_info[0]["alarm_times"])+1
                if int(status_info[0]["alarm_times"])==0:
                    update_sql = "UPDATE status_history SET alarm_time='%s' ,alarm_times = '%d' , last_alarm_time= '%s',last_status = '%d' WHERE mid = '%s' and item_type= '%s'" % (str(time.time()),count,str(time.time()),0,mid,itemtype)
                else:
                    update_sql = "UPDATE status_history SET alarm_times = '%d' , last_alarm_time= '%s',last_status = '%d' WHERE mid = '%s' and item_type='%s'" % (count,str(time.time()),0,mid,itemtype)
                with getMysqlConnection() as db:
                    try:
                        db.cursor.execute(update_sql)  
                        db.conn.commit()
                    except Exception,e:
                        logging.error("'%s' type('%s') 数据更新异常:'%s'" %(mid,itemtype,str(e)))
                    else:
                        logging.info("'%s' type('%s') 数据更新成功" %(mid,itemtype))
            elif int(time.time())- round(float(status_info[0]["alarm_time"]))<= 3600 and int(status_info[0]["alarm_times"]) > times:
                logging.info(status_info[0]["alarm_times"])
                logging.info("'%s':报警次数已达上限('%s')" %(mid,itemtype)) 
            elif time.time()- round(float(status_info[0]["alarm_time"]))> 3600:
                weixinsender.sendmsg(title=itemtype,description=des+"[1]")
                update_sql = "UPDATE status_history SET alarm_times = '%d',alarm_time='%d' ,alarm_time='%s',last_status = '%d' WHERE mid = '%s' and item_type = '%s' " % (1,time.time(),str(time.time()),0,mid,itemtype)
                with getMysqlConnection() as db:
                    try:
                       db.cursor.execute(update_sql) 
                       db.conn.commit()
                    except Exception,e:
                        logging.error(str(e))
                        logging.error("'%s' type('%s') 数据更新异常:'%s'" %(mid,itemtype,str(e)))
                    else:
                        logging.info("'%s' type('%s') 数据更新成功" %(mid,itemtype))
        else:
            weixinsender.sendmsg(title=itemtype,description=des+"[1]")
            update_sql = "INSERT INTO status_history (mid,last_status,alarm_time,last_alarm_time,alarm_times,item_type) VALUES ('%s','%d','%s','%s','%d','%s')" % (mid,0,str(time.time()),str(time.time()),1,itemtype)
            with getMysqlConnection() as db:
                try:
                   db.cursor.execute(update_sql) 
                   db.conn.commit()
                except Exception,e:
                    logging.error(str(e))
                    logging.error("'%s' type('%s') 数据更新异常:'%s'" %(mid,itemtype,str(e)))
                else:
                    logging.info("'%s' type('%s') 数据更新成功" %(mid,itemtype))
def stamp2str(secs):
    m,s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return h,m,s
         
def checkstatus(mid,itemtype):
    with getMysqlConnection() as db:
        sql="select * from status_history where mid='%s' and item_type='%s';" %(str(mid),itemtype)
        db.cursor.execute(sql)
        check_info=db.cursor.fetchall()
        if len(check_info):
            if int(check_info[0]["last_status"])==0:
                timerange=int(time.time())-round(float(check_info[0]["alarm_time"]))
                hours,minutes,sec=stamp2str(timerange)
                timedesc=str(hours)+"小时"+str(minutes)+"分"+str(sec)+"秒"
                weixinsender.sendmsg(title=itemtype+"(恢复通知)",description=mid+"已从异常中恢复,异常持续时间:"+str(timedesc))  
                update_sql = "UPDATE status_history SET last_status = '%d' , alarm_times='%d' WHERE mid = '%s' and item_type= '%s'" % (1,0,mid,itemtype)
                with getMysqlConnection() as db:
                    try:
                       db.cursor.execute(update_sql) 
                       db.conn.commit()
                    except Exception,e:
                        logging.error(str(e))
                        logging.error("'%s' 数据更新异常:'%s'" %(mid,str(e)))
                    else:
                        logging.info("'%s' 数据更新成功'" %(mid))
            else:
                logging.info(mid+":状态未发生异常")
        else:
            logging.info(mid+itemtype+":状态未发生异常")
            
            
    
@timer(5)
def wxwarn(arg):
    with getMysqlConnection() as db:
        sql="select * from dark_status;"
        db.cursor.execute(sql)
        host_list=db.cursor.fetchall()
        if len(host_list):
            for host in host_list:
                if abs(time.time() - time.mktime(time.strptime(str(host["update_time"]),"%Y-%m-%d %H:%M:%S"))) > 300:
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
                    checkstatus(str(host["mid"]),"dark")
                    continue 
                logging.info(host["enabled"])
                if host["enabled"]:
                    alarmpolicy(host["mid"],des,"dark")
                else:
                    logging.info(host["mid"]+"未启用报警")
        else:
            logging.info("未发现相关数据")

@timer(300)
def checkdisk(arg):
    with getMysqlConnection() as db:
        sql="select * from business_info;"
        db.cursor.execute(sql)
        disk_list=db.cursor.fetchall()
        if len(disk_list):
            for diskinfo in disk_list:
                infodict=eval(diskinfo["information"])
                rootusage=float([diskitem for diskitem in infodict["disk_info"] if diskitem["mountpoint"]== "/"][0]["percent"])
                if rootusage >= 90:
                    des='根分区已使用'+str(rootusage)+'%,及时清理('+str(diskinfo["description"])+')'
                    logging.info(des)
                else:
                    logging.info("磁盘检测正常")
                    checkstatus(str(diskinfo["description"]),"disk")
                    continue 
                alarmpolicy(diskinfo["description"],des,"disk")
        else:
            logging.info("未发现disk相关数据")

@timer(300)
def checkmem(arg):
    with getMysqlConnection() as db:
        sql="select * from business_info;"
        db.cursor.execute(sql)
        mem_list=db.cursor.fetchall()
        if len(mem_list):
            for meminfo in mem_list:
                infodict=eval(meminfo["information"])
                if float(infodict["mem_info"]["used"])/float(infodict["mem_info"]["total"])*100 > 80:
                    des='内存大于80%,及时处理('+str(meminfo["description"])+')'
                    logging.info(des)
                else:
                    logging.info("内存检测正常")
                    checkstatus(str(meminfo["description"]),"mem")
                    continue 
                alarmpolicy(meminfo["description"],des,"mem")
        else:
            logging.info("未发现mem相关数据")

@timer(300)
def checkload(arg):
    with getMysqlConnection() as db:
        sql="select * from business_info;"
        db.cursor.execute(sql)
        load_list=db.cursor.fetchall()
        if len(load_list):
            for loadinfo in load_list:
                infodict=eval(loadinfo["information"])
                if float(infodict["cpu_info"]["load_avg"].split()[0]) > float(infodict["cpu_info"]["logical_cores"])*1.5:
                    des='负载过高，及时处理('+str(loadinfo["description"])+')'+' value:'+str(infodict["cpu_info"]["load_avg"].split()[0])
                    logging.info(des)
                else:
                    logging.info("负载检测正常")
                    checkstatus(str(loadinfo["description"]),"load")
                    continue 
                alarmpolicy(loadinfo["description"],des,"load")
        else:
            logging.info("未发现load相关数据")

@timer(10)
def checkprocesslist(arg):
    with getMysqlConnection() as db:
        sql="select * from business_info;"
        db.cursor.execute(sql)
        load_list=db.cursor.fetchall()
        if len(load_list):
            for loadinfo in load_list:
                infodict=eval(loadinfo["information"])
                processmonit=set(infodict["keyprocess"])-set(infodict["processlist"])
                if len(processmonit) > 0:
                    proclist=",".join(processmonit) 
                    des=proclist+'进程不存在:'+'('+str(loadinfo["description"])+')'
                    logging.info(des)
                else:
                    logging.info("进程检测正常")
                    checkstatus(str(loadinfo["description"]),"proc")
                    continue 
                alarmpolicy(loadinfo["description"],des,"proc")
        else:
            logging.info("未发现load相关数据")

@timer(60)
def checkreport(arg):
    with getMysqlConnection() as db:
        sql="select * from business_info;"
        db.cursor.execute(sql)
        repo_list=db.cursor.fetchall()
        if len(repo_list):
            for repoinfo in repo_list:
                if abs(time.time() - time.mktime(time.strptime(str(repoinfo["updatetime"]),"%Y-%m-%d %H:%M:%S"))) > 300:
                    des='上报错误('+str(repoinfo["description"])+')'
                    logging.error(des)
                else:
                    checkstatus(repoinfo["description"],"report")
                    continue
                alarmpolicy(repoinfo["description"],des,"report")
        else:
            logging.info("未发现report相关数据")


#@timer(5)
#def checkjsproxy(arg):
#    url = 'http://mx.93yxpt.com/forwardJs?js_url=http://apps.bdimg.com/cloudaapi/lightapp.js&append_js=append_jscode.js'
#    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
#    headers = {'User-Agent' : user_agent,'Referer':'http://www.qq.com'}
#    request = urllib2.Request(url,headers=headers)
#    n=0
#    for i in range(4):
#        try:
#            response = urllib2.urlopen(request,timeout=5)
#            page = response.read()
#            time.sleep(1)
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
#

@filemon("/opt/dark_web_config/jobs.py")
def monitor_py(num):
    logging.info("jobs.py has been modified,reboot")
    uwsgi.reload()

@filemon("/opt/dark_web_config/main.py")
def monitor_py(num):
    logging.info("main.py has been modified,reboot")
    uwsgi.reload()

@filemon("/opt/dark_web_config/etc/processmonitor.conf")
def monitor_py(num):
    logging.info("configfile has been modified,reboot")
    uwsgi.reload()
