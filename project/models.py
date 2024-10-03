from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(1000))
    admin = db.Column(db.String(1))    
    email = db.Column(db.String(100))
    groupid = db.Column(db.Integer)   
    groupadm = db.Column(db.String(1))  
    updplayer = db.Column(db.String(1)) 

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    groupid = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    midfilder = db.Column(db.Integer)
    forward = db.Column(db.Integer)
    overall = db.Column(db.Integer)    
    checkin = db.Column(db.Integer)
    team = db.Column(db.Integer) 
    random = db.Column(db.Integer)
    position = db.Column(db.String(1))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    
class Groupadm(db.Model):
    groupid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(100), primary_key=True)
    admin = db.Column(db.String(1))  
    updplayer = db.Column(db.String(1))
    
class Draworder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupid = db.Column(db.Integer)
    position = db.Column(db.Integer)