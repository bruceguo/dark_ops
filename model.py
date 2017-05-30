from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import json
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:chinatt()^^*@localhost:3306/darkinfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
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
    boot_time = db.Column(db.DateTime, nullable=False)
    update_time = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
#        return '<dark_mid %r>' % self.mid
        return json.dumps({"mid":self.mid,"dark_version":self.dark_version,"id":self.id,"new_config_version":self.new_config_version,"old_config_version":self.old_config_version,"status":self.old_config_version,"boot_time":self.boot_time,"update_time":self.update_time}) 
if __name__=="__main__":
    manager.run()
