from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import json
class MyEncoder(json.JSONEncoder):  
  def default(self, obj):  
      if isinstance(obj, datetime):  
          return obj.strftime('%Y-%m-%d %H:%M:%S')  
      elif isinstance(obj, date):  
          return obj.strftime('%Y-%m-%d')  
      else:  
          return json.JSONEncoder.default(self, obj)
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:chinatt_1347@localhost:3306/darkinfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['USERNAME']="admin"
app.config['PASSWORD']="admin888"
app.config['SUPERPASSWORD']="e10adc3949ba59abbe56e057f20f883e"
app.config['SECRET_KEY'] = 'jjskdjlkasjdlfjalk'
db = SQLAlchemy(app, use_native_unicode="utf8")
manager = Manager(app)
class dark_status(db.Model):
    __tablename__ = 'dark_status'
    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String(100), unique=True)
    dark_version = db.Column(db.String(100))
    new_config_version = db.Column(db.String(320))
    old_config_version = db.Column(db.String(320))
    status = db.Column(db.Boolean, nullable=False)
    dark_num = db.Column(db.Integer)
    enabled = db.Column(db.Boolean,server_default="1")
    boot_time = db.Column(db.DateTime, nullable=True)
    update_time = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return json.dumps({"mid":self.mid,"dark_version":self.dark_version,"id":self.id,"new_config_version":self.new_config_version,"old_config_version":self.old_config_version,"status":self.old_config_version,"boot_time":self.boot_time,"update_time":self.update_time,"dark_num":self.dark_num},cls=MyEncoder) 
class status_history(db.Model):
    __tablename__ = 'status_history'
    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String(100))
    item_type=db.Column(db.String(100),server_default="dark")
    last_status = db.Column(db.Boolean, nullable=False)
    alarm_time = db.Column(db.String(100), nullable=True)
    last_alarm_time = db.Column(db.String(100), nullable=True)
    alarm_times = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return json.dumps({"mid":self.mid,"last_status":self.last_status,"alarm_time":self.alarm_time,"alarm_times":self.alarm_times}) 

class control_info(db.Model):
    __tablename__ = 'control_info'
    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String(100),unique=True)
    destory_option=db.Column(db.Boolean,server_default="0")
    deploy_option = db.Column(db.Boolean,server_default="1")
    alive_info = db.Column(db.Boolean, server_default="1")
    type_info=db.Column(db.String(100),nullable=False)
    msg=db.Column(db.String(100),server_default="waitting update")
    def __repr__(self):
        return json.dumps({"mid":self.mid,"id":self.id,"destory_option":self.destory_option,"deploy_option":self.deploy_option,"alive_info":self.alive_info,"msg":self.msg})
 
class business_info(db.Model):
    __tablename__ = 'business_info'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100), unique=True)
    information=db.Column(db.Text(1200))
    updatetime = db.Column(db.TIMESTAMP(True), nullable=False)

    def __repr__(self):
        return json.dumps({"id":self.id,"ip":self.ip,"infomation":self.information,"updatetime":self.updatetime,"description":self.description}) 
if __name__=="__main__":
    manager.run()
