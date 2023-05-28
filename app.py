from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from reddit import Reddit
from functools import wraps

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# cors = CORS(app)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/Reddit.db"
# # initialize the app with the extension
db.init_app(app)

# Reddit api
reddit_api = Reddit()

@dataclass
class Submission(db.Model):
    id:int
    submission_name:str

    id = db.Column(db.Integer, primary_key=True)
    submission_name = db.Column(db.String, nullable=False)

@dataclass
class AdminUser(db.Model):
    id:int
    user:str
    password:str

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)
    
@dataclass
class Settings(db.Model):
    id:int
    limit:int
    mode:int

    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.Integer, unique=True, nullable=False)
    limit = db.Column(db.Integer, unique=True, nullable=False)
    

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

# Apply CORS headers to all routes
@app.after_request
@add_cors_headers
def add_cors_headers_to_response(response):
    return response


# http://localhost:3000/get/meme/hot
@app.route("/get/<string:sub_reddit>/<string:mode>/<int:limit>")
def getallsubs(sub_reddit,mode,limit):

    if reddit_api.check(sub_reddit):
        valid_mode = ["new","hot","day","rising"]

        if mode not in valid_mode:
            return f"Invalid mode '{mode}'" ,404 ,{"Access-Control-Allow-Origin": "*"}
         
        subs = reddit_api.submission_from_subreddit(subReddit=sub_reddit,mode=mode,limit=limit)
        previous_subs = Submission.query.all()

        for sub in previous_subs:
            for index,new_sub in enumerate(subs['submission']):
                if sub.submission_name == new_sub['name']:
                    subs['submission'].pop(index)
        subs.update({"total":len(subs['submission'])})

        res = jsonify(subs)
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res

    else:
        return f"'{sub_reddit}' not found" ,404 ,{"Access-Control-Allow-Origin": "*"}

# http://localhost:3000/save
@app.route("/save" , methods=['POST'])
def save():

    if request.is_json:
        jsondata = request.get_json()
        for subs in jsondata['submission_names']:
            new_submission = Submission(submission_name=subs)
            db.session.add(new_submission)
            db.session.commit()

    else:
        data = {
            "error":"No submission data found"
        }
        res = jsonify(data)
        return res , 404
        
    # print(all_submissions)
    res = jsonify("ok")
    return res , 200




@app.route("/getall" , methods=['GET'])
def getall():

    all_submissions = Submission.query.all()
    submission_names = [item.submission_name for item in all_submissions]
    submission_names.reverse()
    data = reddit_api.nameToDetails(submission_names)
    data.update({"total":len(data['submission'])})


    return jsonify(data) ,200



# http://localhost:3000/show
@app.route("/show")
def show_all():
    all_submissions = Submission.query.all()
    return jsonify(all_submissions) , 200 ,{"Access-Control-Allow-Origin": "*"}

@app.route("/remove/<string:submission_name>" , methods=['DELETE'])
def delete(submission_name):
    # delete from database
    submission = Submission.query.filter_by(submission_name=submission_name).first()
    db.session.delete(submission)
    db.session.commit()

    return "" , 200  ,{"Access-Control-Allow-Origin": "*"}


@app.route("/removes", methods=['DELETE'])
def deletes():
    if request.is_json:
        jsondata = request.get_json()
        for name in jsondata['submission_names']:
            new_submission = Submission.query.filter_by(submission_name=name).first()
            db.session.delete(new_submission)
            db.session.commit()

    
    else:
        data = {
            "error":"No submission data found"
        }
        return jsonify(data)
    
    return "DELETED", 200 ,{"Access-Control-Allow-Origin": "*"}


@app.route("/check/<string:subreddit>", methods=['GET'])
def checkSubreddit(subreddit):
    is_exits =  reddit_api.check(subreddit)

    if is_exits:
        return "" , 200, {"Access-Control-Allow-Origin": "*"}
    
    return "" , 404 ,{"Access-Control-Allow-Origin": "*"}

# @app.route("/reset", methods=['DELETE'])
# def delete_all():
#     # Delete all entries in the model
#     db.session.query(Submission).delete()
#     db.session.commit()

#     return "DELETED" ,200

@app.route("/settings", methods=['POST','GET'])
def handel_settings():
    if request.method == 'POST':
        if request.is_json:
            new_data = request.get_json()
            settings_data = Settings.query.filter_by(id=1).first()
            settings_data.limit = new_data["limit"]
            settings_data.mode = new_data["mode"]
            db.session.commit()
            return "" ,200

    elif request.method == 'GET':

        if len(Settings.query.all()) == 0:

            initial_settings = Settings(limit=50,mode="day")
            db.session.add(initial_settings)
            db.session.commit()
            return jsonify(initial_settings) , 200

        
        settings = Settings.query.filter_by(id=1).first()
        return jsonify(settings) , 200


if __name__ == "__main__":
    app.run(debug=True,port=8080)