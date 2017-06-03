#!/usr/biu/env python2.7
#coding:utf-8
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify,abort 
from model import db,dark_status,app
import time
import json
@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/list',methods=['GET'])
def list():
    hostlist=dark_status.query.all()
    hostresult=[]
    totalinfo={"error":0}
    for host in hostlist:
        if time.time() - time.mktime(time.strptime(str(host.update_time),"%Y-%m-%d %H:%M:%S")) > 300:
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

    return render_template('lists.html',hostlist=hostresult,totalinfo=totalinfo)
@app.route('/addhost',methods=['GET'])
def addhost():
    return render_template('add.html')
@app.route('/home',methods=['GET'])
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
    print  request.values
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

if __name__=='__main__':
    app.run(debug=ture)
