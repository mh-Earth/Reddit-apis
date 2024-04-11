from typing import Any
from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from reddit import Reddit
from functools import wraps
from settings import API_KEY
# create the extension
db = SQLAlchemy()       
# create the app
app = Flask(__name__)
# cors = CORS(app)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/Reddit.db"
app.config['API_KEY'] = API_KEY
# # initialize the app with the extension
db.init_app(app)

# Reddit api
reddit_api = Reddit()

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


# Decorator to add CORS headers to each response
def add_cors_headers(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        response = make_response(func(*args, **kwargs))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, DELETE, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight response for 1 hour
        return response

    return decorated_function
def require_api_key(view_func):
    @wraps(view_func)
    def decorated(*args, **kwargs):
        # Assuming the request data is JSON
        api_key = request.args.get('api_key')

        if api_key == None:
            request_data = request.get_json()
            # Check if 'api_key' exists in the request data
            api_key = request_data.get('api_key')

        if api_key is None or api_key != app.config['API_KEY']:
            return jsonify({"Message": "Invalid API Key"}),     


        return view_func(*args, **kwargs)

    return decorated

def require_password(view_func):
    '''
    Check for password in request
    '''
    @wraps(view_func)
    def decorated(*args, **kwargs):
        if request.method in ['POST','DELETE','OPTION','PUT'] and request.is_json:
        # Assuming the request data is JSON
            data = request.get_json()

            try:
                password:str = data['password']
                if password == None or password == r"":
                    raise ValueError
                else: 
                    return view_func(*args, **kwargs)
                    
            except KeyError:
                return jsonify({"Message":"Password required"}) ,401
            except ValueError:
                return jsonify({"Message":"Password cannot be empty"}) ,401
            except Exception as e:
                return jsonify({"Message":"Server Error"}) ,500
        else:
            return view_func(*args, **kwargs)

            
    return decorated

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


# Apply CORS headers to all routes
@app.after_request
@add_cors_headers
def add_cors_headers_to_response(response):
    return response



@app.route("/api/admin",methods=['GET','DELETE'])
@require_api_key
@require_password
@password_auth
def admin():

    # for getting current user info
    if request.method == "GET":
        admin = Admin.query.filter_by(id=1).first()
        if admin:
            return jsonify({"username":admin.username,"code":200}) , 200 , {"Access-Control-Allow-Origin": "*"}
        return jsonify({"Message":"No admin user Found","code":404}), 200, {"Access-Control-Allow-Origin": "*"}

        ...
 

    # for deleting current user
    elif request.method == "DELETE":
        try:
            db.session.query(Admin).delete()
            db.session.commit()
            return "DELETED" ,200
        except Exception as e:
            print(e)


@app.route("/api/admin/create",methods=['POST'])
def create_admin():
   # for creating new user
    if request.is_json:
        if len(Admin.query.all()) == 0:
            try:
                jsondata = request.get_json()
                username = jsondata['username']
                password = jsondata['password']
                new_admin = Admin(username=username,password=password)
                db.session.add(new_admin)
                db.session.commit()
                return jsonify(new_admin) , 200
            except KeyError as e:
                return jsonify({"Message":f"Invaild Data. Correction:{e}"}) ,500
            except Exception as e:
                return "Server Error" ,500
        else:
            return jsonify({"Message":"Max user reached"})




# http://localhost:3000/get/meme/hot
@app.route("/api/get/<string:sub_reddit>/<string:mode>/<int:limit>")
@require_api_key
def getallsubs(sub_reddit,mode,limit):

    valid_mode = ["new","hot","day","rising"]

    if mode not in valid_mode:
        return f"Invalid mode '{mode}'" ,404

    subs = reddit_api.submission_from_subreddit(subReddit=sub_reddit,mode=mode,limit=limit)
    previous_subs = Submission.query.all()

    for sub in previous_subs:
        for index,new_sub in enumerate(subs['submission']):
            if sub.name == new_sub['name']:
                subs['submission'].pop(index)
    subs.update({"total":len(subs['submission'])})

    res = jsonify(subs)
    return res


# http://localhost:3000/save
@app.route("/api/save/<string:name>" , methods=['POST','PUT'])
@require_api_key
@require_password
@password_auth
def save(name:str=None):
    if request.method == 'POST':
        if request.is_json:
            try:
                jsondata = request.get_json()
                for sub in jsondata['submissions']:
                    new_submission = Submission(name=sub['name'],title=sub['title'])
                    db.session.add(new_submission)
                    db.session.commit()

                res = jsonify("ok")
                return res, 200, {"Access-Control-Allow-Origin": "*"}
            except KeyError as e:
                return jsonify({"Message":f"Invaild Data. Correction:{e}"})
            except Exception as e:
                print(e)
                return "Server Error", 500

        else:
            data = {
                "error":"No submission data found"
            }
            res = jsonify(data)
            return res , 404
        
    elif request.method == 'PUT':
        if request.is_json:
            jsondata = request.get_json()
            submission:Submission = db.session.query(Submission).filter(Submission.name == name).first()
            if submission:
                try:
                    submission.tags = jsondata['tags']
                    submission.title = jsondata['title']
                    db.session.commit()
                except KeyError as e:
                    return jsonify({"Message":f"Invaild Data. Correction:{e}"})
                except Exception as e:
                    return "Server Error", 500
                return jsonify(submission) , 200
            else:
                return jsonify({"Message":"Submission Not Found"}) ,404,{"Access-Control-Allow-Origin": "*"}

        else:
            data = {
                "error":"No submission data found"
            }
            res = jsonify(data)
            return res , 404

@app.route("/api/getall" , methods=['GET'])
@require_api_key
def getall():

    all_submissions:list[Submission] = Submission.query.all()
    name = [item.name for item in all_submissions]

    settings  = Settings.query.filter_by(id=1).first()
    if settings == None:
        settings = Settings(limit=50,mode="day",is_reversed=True)
        db.session.add(settings)
        db.session.commit()

    if settings.is_reversed:
        all_submissions.reverse()
        name.reverse()

    # Getting all info about the submission from reddit server
    data = reddit_api.nameToDetails(name)

    # merging OG data from reddit server and local data server data (tags,title etc)
    for index,subs in enumerate(data["submission"]):
        subs.update({
            'tags':all_submissions[index].tags,
            'title':all_submissions[index].title,
            })

    data.update({"total":len(data['submission'])})
    return jsonify(data) ,200


# # http://localhost:3000/show
# @app.route("/api/show")
# def show_all():
#     all_submissions = Submission.query.all()
#     return jsonify(all_submissions) , 200 ,{"Access-Control-Allow-Origin": "*"}

# http://localhost:3000/sub/id
@app.route("/api/show/<string:name>")
@require_api_key
def show(name:str):
    submission = db.session.query(Submission).filter(Submission.name == name).first()
    reddit_subs = reddit_api.submission(name.split("_")[1])

    # merge local and reddit server info
    data = {
        "name":reddit_subs.name,
        "id":reddit_subs.id,
        "title(OG)":reddit_subs.title, 
        "title":submission.title, # local
        "tags":submission.tags, # local
        "author":reddit_subs.author.name if reddit_subs.author != None else "Not found", #optional
        "score":reddit_subs.score if reddit_subs.score != None else "Not found", #optional
        "created_at":reddit_subs.created_utc if reddit_subs.created_utc != None else "Not found", #optional
        "upvote_ratio":reddit_subs.upvote_ratio if reddit_subs.upvote_ratio != None else "Not found", #optional
        "url":reddit_subs.url # most required
    }
    return jsonify(data) , 200 ,{"Access-Control-Allow-Origin": "*"}


# http://localhost:3000/posted
@app.route("/api/posted",methods=['POST','GET','DELETE'])
@require_api_key
@require_password
@password_auth
def posted():
    if request.method == 'GET':
        all_posts = Posted.query.all()
        return jsonify(all_posts) , 200 ,{"Access-Control-Allow-Origin": "*"}
    
    elif request.method == "POST":
        if request.is_json:
            data = request.get_json()
            res_json = {}
            for name in data['name']:
                if db.session.query(Posted).filter(Posted.name == name).first():
                    res_json.update({name:'duplicated'})
                else:    
                    new_post = Posted(name=name)
                    db.session.add(new_post)
                    db.session.commit()
                    res_json.update({name:'ok'})

            return jsonify(res_json) , 200 ,{"Access-Control-Allow-Origin": "*"}
        
    elif request.method == "DELETE":
        if request.is_json:
            jsondata = request.get_json()
            res_json = {}
            try:
                for name in jsondata['name']:
                    submission = Posted.query.filter(Posted.name.endswith(name)).first()
                    if submission:
                        db.session.delete(submission)
                        db.session.commit()
                        res_json.update({name:"ok"})
                    else:
                        res_json.update({name:"failed"})


                return jsonify(res_json), 200 ,{"Access-Control-Allow-Origin": "*"}
            except KeyError:
                return jsonify({"Message":"Invaild Data"})
            except Exception as e:
                return "Server Error" , 500
                
        
        return "No data found", 200 ,{"Access-Control-Allow-Origin": "*"}


@app.route("/api/remove/<string:name>" , methods=['DELETE'])
@require_api_key
@require_password
@password_auth
def remove(name):
    # delete from database
    submission = Submission.query.filter_by(name=name).first()
    if submission:
        db.session.delete(submission)
        db.session.commit()

    return "" , 200  ,{"Access-Control-Allow-Origin": "*"}

# DELETE ONE OR MANY SUBMISSIONS
@app.route("/api/removes", methods=['DELETE'])
@require_api_key
@require_password
@password_auth
def removes():
    if request.is_json:
        jsondata = request.get_json()
        try:
            for name in jsondata['name']:
                submission = Submission.query.filter(Submission.name.endswith(name)).first()
                if submission:
                    db.session.delete(submission)
                    db.session.commit()
        except KeyError:
            return jsonify({"Message":"Invaild Data"})
        except Exception as e:
            return "Server Error" , 500

    else:
        data = {
            "error":"No submission data found"
        }
        return jsonify(data) ,200 ,{"Access-Control-Allow-Origin": "*"}

    return "DELETED", 200 ,{"Access-Control-Allow-Origin": "*"}


@app.route("/api/check/<string:subreddit>", methods=['GET'])
@require_api_key
def checkSubreddit(subreddit):
    if request.method == 'GET':

        is_exits =  reddit_api.check(subreddit)

        if is_exits:
            return "" , 200, {"Access-Control-Allow-Origin": "*"}

        return "" , 404 ,{"Access-Control-Allow-Origin": "*"}
    

# delete all submissions
@app.route("/api/reset", methods=['DELETE'])
@require_api_key
@require_password
@password_auth
def delete_all():
    # Delete all entries in the model
    db.session.query(Submission).delete()
    db.session.commit()
    return "DELETED" ,200


@app.route("/api/", methods=['get'])
def home():
    return jsonify({"status":"Running"}),200

@app.route("/api/settings", methods=['POST','GET'])
@require_api_key
def handel_settings():
    if request.method == 'POST':
        if request.is_json:
            new_data = request.get_json()
            settings_data = Settings.query.filter_by(id=1).first()
            settings_data.limit = new_data["limit"]
            settings_data.mode = new_data["mode"]
            settings_data.is_reversed = new_data["is_reversed"]
            db.session.commit()
            return "" ,200

    elif request.method == 'GET':

        if len(Settings.query.all()) == 0:

            initial_settings = Settings(limit=50,mode="day",is_reversed=True)
            db.session.add(initial_settings)
            db.session.commit()
            return jsonify(initial_settings) , 200


        settings = Settings.query.filter_by(id=1).first()
        return jsonify(settings) , 200

if __name__ == "__main__":
    app.run(debug=True)