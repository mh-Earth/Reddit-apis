from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask import request,jsonify
from functools import wraps


# create the extension
db = SQLAlchemy() 

@dataclass
class Submission(db.Model):
    id:int
    name:str
    tags:str
    title:str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    tags = db.Column(db.String,default="#igobymemes #shorts #memes")
    title = db.Column(db.String,default="igobymemes")
@dataclass
class Posted(db.Model):
    id:int
    name:str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    

@dataclass
class Admin(db.Model):
    id:int
    username:str
    password:str

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)

@dataclass
class Settings(db.Model):
    id:int
    limit:int
    mode:str
    is_reversed:bool

    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.Integer, unique=True, nullable=False)
    limit = db.Column(db.Integer, unique=True, nullable=False)
    is_reversed = db.Column(db.Boolean, nullable=False,default=True)

@dataclass
class AdminPlaneUrls(db.Model):
    id:int
    slug:str
    create_at:float
    # in second
    live:int
    expired:bool
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, unique=True, nullable=False)
    create_at = db.Column(db.Float, nullable=False)
    live = db.Column(db.Integer, nullable=False,default=120)
    expired = db.Column(db.Boolean, nullable=False,default=False)
    

# @require_password
def password_auth(view_func):
    '''
    Check password's authenticity. Use with 'require_password' decorator
    '''
    @wraps(view_func)
    def decorated(*args, **kwargs):
        if request.method in ['POST','DELETE','OPTION','PUT'] and request.is_json:
            data = request.get_json()
            admin = Admin.query.filter_by(id=1).first()
            if admin:
                admin_pass = admin.password
            else:
                return jsonify({"Message":"No Admin Found"})

            password:str = data['password']
            if password == admin_pass:
                return view_func(*args, **kwargs)
            else:
                return jsonify({"Message":"Invalid password"}) ,401
        else:
            return view_func(*args, **kwargs)

                
    return decorated