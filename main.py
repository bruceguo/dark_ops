#!/usr/biu/env python2.7
#coding:utf-8
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify,abort 
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root@localhost:3306/darkinfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db = SQLAlchemy(app)
#manager = Manager(app)
class dark_status(db.Model):
    __tablename__ = 'dark_status'
    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String(100), unique=True)
    dark_version = db.Column(db.String(100))
    new_config_version = db.Column(db.String(320))
    old_config_version = db.Column(db.String(320))
    status = db.Column(db.Boolean, nullable=False)
    boot_time = db.Column(db.DateTime, nullable=False)
    update_time = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return '<dark_mid %r>' % self.mid





@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/list',methods=['GET'])
def list():
    return render_template('lists.html')
@app.route('/addhost',methods=['GET'])
def addhost():
    return render_template('add.html')
@app.route('/home',methods=['GET'])
def home():
    return render_template('home.html')
@app.route('/api/collect_dark_status',methods=['POST'])
def collect_info():
    print request.values
    return jsonify({"status":"ok"})
if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
