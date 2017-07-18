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
app.config['SECRET_KEY'] = 'jjskdjlkasjdlfjalk'
db = SQLAlchemy(app)
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
    boot_time = db.Column(db.DateTime, nullable=True)
    update_time = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return json.dumps({"mid":self.mid,"dark_version":self.dark_version,"id":self.id,"new_config_version":self.new_config_version,"old_config_version":self.old_config_version,"status":self.old_config_version,"boot_time":self.boot_time,"update_time":self.update_time,"dark_num":self.dark_num},cls=MyEncoder) 
if __name__=="__main__":
    manager.run()
