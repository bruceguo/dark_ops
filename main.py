#!/usr/biu/env python2.7
#coding:utf-8
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify,abort 
app=Flask(__name__)
@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')
if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
