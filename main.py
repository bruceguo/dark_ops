#!/usr/biu/env python2.7
#coding:utf-8
from flask import session,redirect,url_for,escape
from flask import request
from flask import render_template
from flask import jsonify,abort 
from model import db,dark_status,app
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
    return render_template("index.html",username=username) 

@app.route('/list',methods=['GET'])
@login_required
def list():
    hostlist=dark_status.query.all()
    hostresult=[]
    hostresult_web=[]
    totalinfo={"error":0}
    rond=1
    for host in hostlist:
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
    for item in hostresult:
        item.id=rond
        hostresult_web.append(item)
        rond+=1 
    hostresult_web=sorted(hostresult_web,key=lambda x:x.status)
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
    print request.values
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
    print  request.values
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
