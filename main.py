#!/usr/biu/env python2.7
#coding:utf-8
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify,abort 
from model import db,dark_status,app
import json
@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/list',methods=['GET'])
def list():
    hostlist=dark_status.query.all()
    return render_template('lists.html',hostlist=hostlist)
@app.route('/addhost',methods=['GET'])
def addhost():
    return render_template('add.html')
@app.route('/home',methods=['GET'])
def home():
    hoststotal=len(dark_status.query.all())
    normalnum=len(dark_status.query.filter_by(status=1).all())
    print hoststotal
    return render_template('home.html',hoststotal=hoststotal,normalnum=normalnum)
@app.route('/api/collect_dark_status',methods=['POST'])
def collect_info():
    if request.values.get("mid",None) and request.values.get("update_time",None):
        result=dark_status.query.filter_by(mid= request.values["mid"]).all()
        if len(result)==0:
            if request.values["new_config_version"] == request.values["old_config_version"]:
                status=1
            else:
                status=0
            try:
                db.session.add(dark_status(mid=request.values["mid"],dark_version=request.values["dark_version"],new_config_version=request.values["new_config_version"],old_config_version=request.values["old_config_version"],status=status,boot_time=request.values["boot_time"],update_time=request.values["update_time"]))
                db.session.commit()
            except Exception,e:
                print e
                return jsonify({"error":1,"message":str(e)}),10012
            else:
                return jsonify({"error":0,"message":"status upload succeed."}),201
        else:
            query_result=dark_status.query.filter_by(mid=request.values["mid"]).first()
            if request.values["new_config_version"] == request.values["old_config_version"]:
                status=1
            else:
                status=0
            query_result.status=status
            query_result.dark_version=request.values["dark_version"]
            query_result.new_config_version=request.values["new_config_version"]
            query_result.old_config_version=request.values["old_config_version"]
            query_result.update_time=request.values["update_time"]
            query_result.boot_time=request.values["boot_time"]
            db.session.commit()
            return jsonify({"error":0,"message":"status update succeed."}),201
    else:
        return jsonify({"error":1,"message":"mid and update_time is required"}),10010
if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
