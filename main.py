#!/usr/biu/env python2.7
#coding:utf-8
from flask import session,redirect,url_for,escape
from flask import request
from flask import render_template
from flask import jsonify,abort 
from model import db,dark_status,app,business_info
from functools import wraps
from WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import time
import logging
import json
#日志模式初始化
logging.basicConfig(level="DEBUG",
                format='%(asctime)s  %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='./log/dark_status.log',
                filemode='a')
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        print session.get("logged_in")
        if session.get("logged_in") and session.get("username") != None:
            return func(*args, **kwargs)
        return redirect(url_for('login', next=request.url))
    return decorated_function

@app.route('/logout')
def loginout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for("login"))
    
@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.values['name'] != app.config['USERNAME']:
            error='Invalid username'
            print error
        elif request.values['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
            print error
        else:
            print "yes"
            session['logged_in'] = True
            session['username'] = request.values['name'] 
            return redirect(url_for("index"))
            print "yes"
    return render_template("login.html")

@app.route('/',methods=['GET'])
@login_required
def index():
    username=session.get("username")
    hostinfolist=business_info.query.all()
    return render_template("index.html",username=username,hostinfolist=hostinfolist) 

@app.route('/list',methods=['GET'])
@login_required
def list():
    hostlist=dark_status.query.all()
    hostresult=[]
    hostresult_web=[]
    host_unabled=[]
    totalinfo={"error":0}
    rond=1
    for host in hostlist:
        if host.enabled:
            if abs(time.time() - time.mktime(time.strptime(str(host.update_time),"%Y-%m-%d %H:%M:%S"))) > 300:
                host.message=u"dark上报异常"
                host.status=0
                totalinfo["error"]+=1
            else:
                if host.new_config_version==host.old_config_version and host.boot_time !="" and host.dark_num != 0:
                    host.message=u"dark程序正常"
                else:
                    host.message=u"dark程序异常"
                    host.status=0
                    totalinfo["error"]+=1
            hostresult.append(host)
        else:
            host.message=u"报警已关闭"
            host.status=0
            totalinfo["error"]+=1
            host_unabled.append(host)
    for item in hostresult:
        item.id=rond
        hostresult_web.append(item)
        rond+=1 
    hostresult_web=sorted(hostresult_web,key=lambda x:x.status)
    hostresult_web.extend(host_unabled)
    return render_template('lists.html',hostlist=hostresult_web,totalinfo=totalinfo)
@app.route('/addhost',methods=['GET'])
@login_required
def addhost():
    return render_template('add.html')
@app.route('/home',methods=['GET'])
@login_required
def home():
    hoststotal=len(dark_status.query.all())
    hostresult=[]
    for host in dark_status.query.filter_by(status=1).all():
        if time.time() - time.mktime(time.strptime(str(host.update_time),"%Y-%m-%d %H:%M:%S")) > 300:
            pass
        else:
            if host.new_config_version==host.old_config_version and host.boot_time !="" and host.dark_num != 0:
                hostresult.append(host)
            else:
                pass
    normalnum=len(hostresult)
    return render_template('home.html',hoststotal=hoststotal,normalnum=normalnum)

@app.route('/api/collect_dark_status',methods=['POST'])
def collect_info():
    if request.values.get("mid",None) and request.values.get("update_time",None):
        result=dark_status.query.filter_by(mid= request.values["mid"]).all()
        if len(result)==0:
            if request.values["new_config_version"] == request.values["old_config_version"] and request.values["boot_time"] != "":
                status=1
            else:
                status=0
            try:
                if request.values["boot_time"]=="":
                    db.session.add(dark_status(mid=request.values["mid"],dark_version=request.values["dark_version"],new_config_version=request.values["new_config_version"].split("-")[-1],old_config_version=request.values["old_config_version"].split("-")[-1],status=status,update_time=request.values["update_time"],dark_num=request.values["dark_num"]))
                else:
                    db.session.add(dark_status(mid=request.values["mid"],dark_version=request.values["dark_version"],new_config_version=request.values["new_config_version"].split("-")[-1],old_config_version=request.values["old_config_version"].split("-")[-1],status=status,boot_time=request.values["boot_time"],update_time=request.values["update_time"],dark_num=request.values["dark_num"]))
                db.session.commit()
            except Exception,e:
                print e
                return jsonify({"error":1,"message":str(e)}),10012
            else:
                return jsonify({"error":0,"message":"status upload succeed."}),201
        else:
            query_result=dark_status.query.filter_by(mid=request.values["mid"]).first()
            if request.values["new_config_version"] == request.values["old_config_version"] and request.values["boot_time"] != "":
                status=1
            else:
                status=0
            query_result.status=status
            query_result.dark_version=request.values["dark_version"]
            query_result.new_config_version=request.values["new_config_version"].split("-")[-1]
            query_result.old_config_version=request.values["old_config_version"].split("-")[-1]
            query_result.update_time=request.values["update_time"]
            query_result.dark_num=request.values["dark_num"]
            if request.values["boot_time"]=="":
                pass
            else:
                query_result.boot_time=request.values["boot_time"]
            db.session.commit()
            return jsonify({"error":0,"message":"status update succeed."}),201
    else:
        return jsonify({"error":1,"message":"mid and update_time is required"}),10010
@app.route('/api/del_host',methods=['POST'])
@login_required
def delte_host():
    mid=request.values.get("mid",None)
    if mid:
        try:
            midhost= dark_status.query.filter_by(mid=mid).first()
            db.session.delete(midhost)
            db.session.commit()
        except Exception,e:
            print e.message
            return jsonify({"error":1,"msg":str(e)})
        else:
            return jsonify({"error":0})
    else:
        return jsonify({"error":1,"msg":"mid not find"})

@app.route('/alarmswitch',methods=['POST'])
@login_required
def alarmswitch():
    print request.values
    mid=request.values.get("mid",None)
    enabled=request.values.get("enabled",None)
    if all([mid,enabled]):
        try:
            enabled_result=dark_status.query.filter_by(mid=request.values["mid"]).first()
            enabled_result.enabled=int(enabled)
            db.session.commit()
        except Exception,e:
            logging.error(str(e))
            return jsonify({"error":1,"msg":str(e)})
        else:
            return jsonify({"error":0})
    else:
        return jsonify({"error":1,"msg":"mid or enabled is null"})

@app.route('/posthostinfo',methods=['POST'])
def hostinfo():
    if request.form.get("host_info",None):
         info_dict=request.form["host_info"]
         ip=eval(info_dict)["ip_dict"][(eval(info_dict)["ip_dict"].keys()[0])]
         description=eval(info_dict)["description"]
         try:
             info_result=business_info.query.filter_by(ip=ip).all()
             if len(info_result)==0:
                 db.session.add(business_info(ip=ip,description=description,information=info_dict))
                 db.session.commit()
             else:
                 update_sql=business_info.query.filter_by(ip=ip).first()
                 update_sql.information=info_dict
                 update_sql.description=description
                 db.session.commit()
         except Exception,e:
             logging.error("主机信息更新错误"+str(e))
             return jsonify({"error":1,"msg":str(e)})
         else:
             logging.info("主机信息更新正常")
             return jsonify({"error":0})
    else:
        return jsonify({"error":1,"msg":"info Incomplete"})

@app.route('/showhostmonitor')
@login_required
def showhostinfo():
    id=request.args.get("id",None)
    host={}
    hostinfolist=[]
    if id:
         try:
             show_result=business_info.query.filter_by(id=id).first()
         except Exception,e:
             logging.error("主机信息查询错误"+str(e))
         else:
             logging.info("主机信息查询正常")
             totaldic=eval(show_result.information)
             host["users"]=len(totaldic["user_info"])
             host["load"]=totaldic["cpu_info"]["load_avg"].split()[0]
             host["memory"]=float(totaldic["mem_info"]["used"])/int(totaldic["mem_info"]["total"])*100
             host["disk"]=[disk["percent"] for disk in totaldic["disk_info"] if disk["mountpoint"]=="/"]
             for procs in totaldic["processlist"]:
                 if len([procport for procport in totaldic["port_info"] if procport[0] == procs])==0:
                     if abs(time.time() - time.mktime(time.strptime(str(show_result.updatetime),"%Y-%m-%d %H:%M:%S"))) > 200:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":"未监听端口","updatetime":show_result.updatetime,"message":"上报异常"})
                     else:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":"未监听端口","updatetime":show_result.updatetime,"message":"正常"})
                 elif len([procport for procport in totaldic["port_info"] if procport[0] == procs])==1:
                     if abs(time.time() - time.mktime(time.strptime(str(show_result.updatetime),"%Y-%m-%d %H:%M:%S"))) > 200:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":[procport[1] for procport in totaldic["port_info"] if procport[0] == procs][0],"updatetime":show_result.updatetime,"message":"上报异常"})
                     else:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":[procport[1] for procport in totaldic["port_info"] if procport[0] == procs][0],"updatetime":show_result.updatetime,"message":"正常"})
                 else:
                     portinfo=[]
                     for lport in [procport for procport in totaldic["port_info"] if procport[0] == procs]:
                         portinfo.append(lport[1])
                     if abs(time.time() - time.mktime(time.strptime(str(show_result.updatetime),"%Y-%m-%d %H:%M:%S"))) > 200:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":",".join(portinfo),"updatetime":show_result.updatetime,"message":"上报异常"})
                     else:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":",".join(portinfo),"updatetime":show_result.updatetime,"message":"正常"})
             return render_template("processlist.html",host=host,hostinfolist=hostinfolist)  
    else:
        return jsonify({"error":1,"msg":"args Incomplete"})

@app.route('/weixin/api_info',methods=['POST','GET','PUT'])
def weixinapi():
    sVerifyMsgSig=request.args.get("msg_signature")
    sVerifyTimeStamp=request.args.get("timestamp")
    sVerifyNonce=request.args.get("nonce")
    sVerifyEchoStr=request.args.get("echostr",None)
    sToken = "n4qNeb1yaa97NTN"
    sEncodingAESKey = "egSYpRdPluyV68CPE63SJ1vmLNPf4YleTX3ftwXBoLv"
    sCorpID = "ww3a7da140a1da4c3b"
    wxcpt=WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
    if request.method=="POST":
        sReqData=request.data
        ret,sMsg=wxcpt.DecryptMsg( sReqData, sVerifyMsgSig,sVerifyTimeStamp, sVerifyNonce)
        if ret ==0:
            xml_tree = ET.fromstring(sMsg)
            content = xml_tree.find("Content").text
            ToUserName=xml_tree.find("ToUserName").text
            FromUserName=xml_tree.find("FromUserName").text
            AgentID=xml_tree.find("AgentID").text
            sRespData = "<xml><ToUserName>"+ToUserName+"</ToUserName><FromUserName>"+FromUserName+"</FromUserName><CreateTime>1476422779</CreateTime><MsgType>text</MsgType><Content>你好</Content><MsgId>1456453720</MsgId><AgentID>"+AgentID+"</AgentID></xml>"
            ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, sVerifyNonce, sVerifyTimeStamp)
            return sEncryptMsg
    else:
        ret,sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)
        if ret == 0:
            return sEchoStr
        
        

if __name__=='__main__':
    app.run()
