#!/usr/biu/env python2.7
#coding:utf-8
from flask import session,redirect,url_for,escape
from flask import request
from flask import render_template
from flask import jsonify,abort 
from model import db,dark_status,app,business_info,control_info
from functools import wraps
from WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import time
import logging
import json
import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import hashlib
reload(sys)
sys.setdefaultencoding('utf8')
#日志模式初始化
logging.basicConfig(level="DEBUG",
                format='%(asctime)s  %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='./log/dark_status.log',
                filemode='a')
def md5pas(src):
    m2=hashlib.md5()
    m2.update(src)
    return m2.hexdigest()

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

@app.route('/api/darkinfolist',methods=['GET'])
@login_required
def hostinfodictlist():
    hostlist=dark_status.query.all()
    base_info={"code": 0,"msg": "","count": 1000,"data": []} 
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
                host.version_status=0
                totalinfo["error"]+=1
            else:
                if host.new_config_version==host.old_config_version and host.boot_time !="" and host.dark_num != 0:
                    host.version_status=1
                    host.message=u"dark程序正常"
                elif host.new_config_version != host.old_config_version and host.boot_time !="" and host.dark_num != 0:
                    host.version_status=0
                    host.message=u"配置更新中"
                else:
                    host.message=u"dark程序异常"
                    host.version_status=0
                    host.status=0
                    totalinfo["error"]+=1
            hostresult.append({"enabled":host.enabled,"message":host.message,"version_status": host.version_status, "status": host.status, "update_time":str(host.update_time), "boot_time":str(host.boot_time), "id": host.id,"mid": host.mid, "dark_num": host.dark_num, "dark_version": host.dark_version})
        else:
            host.message=u"报警已关闭"
            host.version_status=0
            host.status=0
            totalinfo["error"]+=1
            hostresult.append({"enabled":host.enabled,"message":host.message,"version_status": host.version_status, "status": host.status, "update_time":str(host.update_time), "boot_time":str(host.boot_time), "id": host.id,"mid": host.mid, "dark_num": host.dark_num, "dark_version": host.dark_version})
    for item in hostresult:
        item["id"]=rond
        hostresult_web.append(item)
        rond+=1 
    hostresult_web=sorted(hostresult_web,key=lambda x:x["status"])
    hostresult_web.extend(host_unabled)
    base_info["data"]=hostresult_web
    return jsonify(base_info)

@app.route('/list',methods=['GET'])
@login_required
def totallist():
    hostlist=dark_status.query.all()
    totalinfo={"error":0}
    for host in hostlist:
        if host.enabled:
            if abs(time.time() - time.mktime(time.strptime(str(host.update_time),"%Y-%m-%d %H:%M:%S"))) > 300:
                totalinfo["error"]+=1
            else:
                if host.new_config_version==host.old_config_version and host.boot_time !="" and host.dark_num != 0:
                    pass
                elif host.new_config_version != host.old_config_version and host.boot_time !="" and host.dark_num != 0:
                    pass
                else:
                    totalinfo["error"]+=1
        else:
            totalinfo["error"]+=1
    return render_template('lists.html',totalinfo=totalinfo)

@app.route('/controllist',methods=['GET'])
@login_required
def controllist():
    controlinfolist=control_info.query.all()
    hostlist=[]
    if len(controlinfolist)==0:
        return render_template('controllist.html',hostlist=hostlist)
    else:
        for infoobj in controlinfolist:
            hostlist.append({"msg":infoobj.msg,"id":infoobj.id,"mid":infoobj.mid,"darktype":infoobj.type_info,"cleanswitch":infoobj.destory_option,"deployswitch":infoobj.deploy_option,"aliveswitch":infoobj.alive_info})
        return render_template('controllist.html',hostlist=hostlist)
        
@app.route('/api/controllistinfo',methods=['GET'])
@login_required
def controllistinfo():
    controlinfolist=control_info.query.all()
    hostlist=[]
    base_info={"code": 0,"msg": "","count": 1000,"data": []} 
    if len(controlinfolist)==0:
        return jsonify(base_info) 
    else:
        for infoobj in controlinfolist:
            hostlist.append({"msg":infoobj.msg,"id":infoobj.id,"mid":infoobj.mid,"darktype":infoobj.type_info,"cleanswitch":infoobj.destory_option,"deployswitch":infoobj.deploy_option,"aliveswitch":infoobj.alive_info})
            base_info["data"]=hostlist
        return jsonify(base_info)

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
            elif host.new_config_version != host.old_config_version and host.boot_time !="" and host.dark_num != 0:
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

def correctstr(text):
    length = 16
    count = len(text)
    add = length - (count % length)
    result = text + ('\0' * add)
    return result

def buildkey(mid):
    length=len(mid)
    if length >=16:
        keyword=mid[:16]
    else:
        keyword = mid + (16 - int(length)) * '\0'
    return keyword

@app.route('/api/dkcontrolinfo',methods=['GET','POST'])
def dkcontrol():
    if request.method == "GET":
        mid=request.args.get("minionid")
        dktype=request.args.get("dktype")
        keyword=buildkey(mid)
        cryptor = AES.new(keyword, AES.MODE_CBC, keyword)
        dklist=control_info.query.filter_by(mid=mid).all()
        if len(dklist):
            currentdkinfo=control_info.query.filter_by(mid=mid).first()
            text=json.dumps({u'destory': int(currentdkinfo.destory_option), u'type': currentdkinfo.type_info, u'error': 0, u'alive': int(currentdkinfo.alive_info), u'deploy': int(currentdkinfo.deploy_option)})
            ciphertext = cryptor.encrypt(correctstr(text))
            return jsonify({"objinfo":b2a_hex(ciphertext)})
        else:
            db.session.add(control_info(mid=mid,type_info=dktype))
            db.session.commit()
            text=json.dumps({u'error': 1, u'msg': 'no info,register later'})
            ciphertext = cryptor.encrypt(correctstr(text))
            return jsonify({"objinfo":b2a_hex(ciphertext)})
    else:
        infodic=json.loads(request.form.get("status_info"))
        mid=infodic["mid"]
        try:
            reportlist=control_info.query.filter_by(mid=mid).all()
            if len(reportlist):
                crrentdkreport=control_info.query.filter_by(mid=mid).first()
                if infodic["alive"]==1 and infodic["check"]==1:
                   crrentdkreport.msg=u"程序运行中,crontab开启"
                elif infodic["alive"]==0 and infodic["check"]==1:  
                   crrentdkreport.msg=u"程序停止,crontab开启"
                elif infodic["alive"]==1 and infodic["check"]==2:  
                   crrentdkreport.msg=u"程序运行中,crontab未配置"
                elif infodic["alive"]==1 and infodic["check"]==0:  
                   crrentdkreport.msg=u"程序运行中,crontab关闭"
                elif infodic["exist"]==0 and infodic["alive"]==0 and infodic["check"]==0:  
                   crrentdkreport.msg=u"程序停止且已经清理"
                elif infodic["exist"]==1 and infodic["alive"]==0 and infodic["check"]==0:  
                   crrentdkreport.msg=u"程序存在,程序停止,同步暂停"

                elif infodic["exist"]==1 and infodic["alive"]==0 and infodic["check"]==2:  
                   crrentdkreport.msg=u"程序存在未运行,未发现crontab配置"
                else:
                   crrentdkreport.msg=u"状态未知"
            db.session.commit()        
        except Exception,e:
            return jsonify({"error":1,"msg":str(e)})
        else:
            return jsonify({"error":0,"msg":"ok"})
         
@app.route('/api/controldkstatus',methods=['POST'])
@login_required
def controldkstatus():
    opt=request.form.get("opt")
    name=request.form.get("name")
    mid=request.form.get("mid")
    passwd=request.form.get("passwd")
    md5passwd=md5pas(passwd)
    print request.form
    choice={"true":1,"false":0}
    if md5passwd == app.config["SUPERPASSWORD"]: 
        try:
            currentmid=control_info.query.filter_by(mid=mid).first()
            if name == "destory_option":
                currentmid.destory_option=choice[opt]
            elif name == "deploy_option":
                currentmid.deploy_option=choice[opt]
            else:
                currentmid.alive_info=choice[opt]
            db.session.commit()
        except Exception,e:
            return jsonify({"error":1,"msg":str(e)})
        else:
            return jsonify({"error":0})
    else:
        return jsonify({"error":1,"msg":"密码不正确"})
        

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
         ip=eval(info_dict)["ip_dict"]['gatewayifaceip']
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
    return render_template("processlist.html",id=id)  

@app.route('/api/hostprocesslist')
@login_required
def hostprocesslist():
    id=request.args.get("id",None)
    hostinfolist=[]
    base_info={"code": 0,"msg": "","count": 1000,"data":[]} 
    if id:
         try:
             show_result=business_info.query.filter_by(id=id).first()
         except Exception,e:
             logging.error("主机信息查询错误"+str(e))
             base_info["code"]=1
             base_info["msg"]=str(e)
             return jsonify(base_info)
         else:
             logging.info("主机信息查询正常")
             totaldic=eval(show_result.information)
             for procs in totaldic["processlist"]:
                 if len([procport for procport in totaldic["port_info"] if procport[0] == procs])==0:
                     if abs(time.time() - time.mktime(time.strptime(str(show_result.updatetime),"%Y-%m-%d %H:%M:%S"))) > 200:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":"未监听端口","updatetime":str(show_result.updatetime),"message":"上报异常"})
                     else:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":"未监听端口","updatetime":str(show_result.updatetime),"message":"正常"})
                 elif len([procport for procport in totaldic["port_info"] if procport[0] == procs])==1:
                     if abs(time.time() - time.mktime(time.strptime(str(show_result.updatetime),"%Y-%m-%d %H:%M:%S"))) > 200:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":[procport[1] for procport in totaldic["port_info"] if procport[0] == procs][0],"updatetime":str(show_result.updatetime),"message":"上报异常"})
                     else:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":[procport[1] for procport in totaldic["port_info"] if procport[0] == procs][0],"updatetime":str(show_result.updatetime),"message":"正常"})
                 else:
                     portinfo=[]
                     for lport in [procport for procport in totaldic["port_info"] if procport[0] == procs]:
                         portinfo.append(lport[1])
                     if abs(time.time() - time.mktime(time.strptime(str(show_result.updatetime),"%Y-%m-%d %H:%M:%S"))) > 200:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":",".join(portinfo),"updatetime":str(show_result.updatetime),"message":"上报异常"})
                     else:
                         hostinfolist.append({"id":show_result.id,"process":procs,"listenport":",".join(portinfo),"updatetime":str(show_result.updatetime),"message":"正常"})
             base_info["data"]=hostinfolist
             return jsonify(base_info)
    else:
         base_info["code"]=1
         base_info["msg"]=u'参数不完整...'
         return jsonify(base_info)

@app.route('/api/hostsysteminfo')
@login_required
def hostsysteminfo():
    id=request.args.get("id",None)
    host={}
    if id:
         try:
             show_result=business_info.query.filter_by(id=id).first()
         except Exception,e:
             logging.error("主机信息查询错误"+str(e))
             return jsonify({"error":1,"msg":str(e)})
         else:
             logging.info("主机信息查询正常")
             totaldic=eval(show_result.information)
             host["users"]=len(totaldic["user_info"])
             host["load"]=totaldic["cpu_info"]["load_avg"].split()[0]
             host["memory"]=float(totaldic["mem_info"]["used"])/int(totaldic["mem_info"]["total"])*100
             host["disk"]=[disk["percent"] for disk in totaldic["disk_info"] if disk["mountpoint"]=="/"]
             host["error"]=0
             return jsonify(host)
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
