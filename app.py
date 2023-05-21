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
    submission_id:str

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.String, nullable=False)

@dataclass
class AdminUser(db.Model):
    id:int
    user:str
    password:str

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)
    

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
                if sub.submission_id == new_sub['id']:
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
        for subs in jsondata['submission_ids']:
            new_submission = Submission(submission_id=subs)
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

# http://localhost:3000/show
@app.route("/show")
def show_all():
    all_submissions = Submission.query.all()
    return jsonify(all_submissions) , 200 ,{"Access-Control-Allow-Origin": "*"}

@app.route("/remove/<string:submission_id>" , methods=['DELETE'])
def delete(submission_id):
    # delete from database
    submission = Submission.query.filter_by(submission_id=submission_id).first()
    db.session.delete(submission)
    db.session.commit()

    return "" , 204  ,{"Access-Control-Allow-Origin": "*"}


@app.route("/removes", methods=['DELETE'])
def deletes():
    if request.is_json:
        jsondata = request.get_json()
        for subs in jsondata['submission_ids']:
            new_submission = Submission(submission_id=subs)
            db.session.delete(new_submission)
            db.session.commit()

    
    else:
        data = {
            "error":"No submission data found"
        }
        return jsonify(data)
    
    # print(all_submissions)
    return "DELETED", 404 ,{"Access-Control-Allow-Origin": "*"}


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




# @app.route("/test", methods=['GET'])
# def test():
#     subs = {
#   "mode": "new",
#   "sub_reddit": "memes",
#   "submission": [
#     {
#       "author": "azul_ivy",
#       "created_at": 1684652156.0,
#       "id": "13nlkgk",
#       "score": 6,
#       "title": "Literally me",
#       "upvote_ratio": 1.0,
#       "url": "https://i.redd.it/4is4x5rrb61b1.jpg"
#     },
#     {
#       "author": "Please_ForgetMe",
#       "created_at": 1684652145.0,
#       "id": "13nlkbj",
#       "score": 2,
#       "title": "Zork be givin me sas",
#       "upvote_ratio": 1.0,
#       "url": "https://i.redd.it/2g1zpz0rb61b1.jpg"
#     },
#     {
#       "author": "RealzLlamaz",
#       "created_at": 1684652100.0,
#       "id": "13nljtl",
#       "score": 2,
#       "title": "[insert rant about how we are living in the matrix and need to wake up here]",
#       "upvote_ratio": 1.0,
#       "url": "https://i.redd.it/g8h444gmb61b1.jpg"
#     },
#     {
#       "author": "daviess",
#       "created_at": 1684651797.0,
#       "id": "13nlgjp",
#       "score": 13,
#       "title": "She really had those thin 90's eyebrows",
#       "upvote_ratio": 1.0,
#       "url": "https://i.redd.it/q979791qa61b1.jpg"
#     },
#     {
#       "author": "azul_ivy",
#       "created_at": 1684651319.0,
#       "id": "13nlbbo",
#       "score": 2,
#       "title": "I don't want Monday to come",
#       "upvote_ratio": 0.67,
#       "url": "https://i.redd.it/4mojgz8a961b1.jpg"
#     },
#     {
#       "author": "RSforce1",
#       "created_at": 1684651134.0,
#       "id": "13nl9ai",
#       "score": 6,
#       "title": "Excuse me, what the f...",
#       "upvote_ratio": 0.88,
#       "url": "https://i.redd.it/bgke2cyq861b1.jpg"
#     },
#     {
#       "author": "Total-Experience2787",
#       "created_at": 1684648987.0,
#       "id": "13nkm1c",
#       "score": 14,
#       "title": "Its because of zeta im tellin you",
#       "upvote_ratio": 0.95,
#       "url": "https://i.redd.it/52z301dsk41b1.png"
#     },
#     {
#       "author": "InsanePug",
#       "created_at": 1684648972.0,
#       "id": "13nklvp",
#       "score": 7,
#       "title": "Scatman, Awesome face song, EEEAAAOOO...",
#       "upvote_ratio": 0.77,
#       "url": "https://i.redd.it/63cygldb261b1.jpg"
#     },
#     {
#       "author": "LemonConnoiseur",
#       "created_at": 1684647802.0,
#       "id": "13nk8iu",
#       "score": 5,
#       "title": "Can’t wait to see it!",
#       "upvote_ratio": 0.67,
#       "url": "https://i.redd.it/elny2t5uy51b1.jpg"
#     }
#   ],
#   "time": "Sun, 21 May 2023 07:01:20 GMT",
#   "total": 9
# }
#     previous_subs = Submission.query.all()

#     for sub in previous_subs:
#         for index,new_sub in enumerate(subs['submission']):
#             if sub.submission_id == new_sub['id']:
#                 print("True")
#                 subs['submission'].pop(index)
#     subs.update({"total":len(subs['submission'])})
#         # # print(sub)
#         # print(subs['submission'][index]['id'])
#         # print(sub.submission_id)
#         # if sub.submission_id == subs['submission'][index]['id']:

#     # print(f"Filter subs are {subs['submission']} \n\n" )
#     res = jsonify(subs)
#     res.headers.add('Access-Control-Allow-Origin', '*')
#     return res

    



if __name__ == "__main__":
    app.run(debug=True,port=8080)