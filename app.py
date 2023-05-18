from flask import Flask,render_template,redirect,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from reddit import Reddit
# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
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
            if sub.submission_id in subs['submission']:
                subs['submission'].pop(sub.submission_id)

        subs.update({"total":len(subs['submission'])})
        res = jsonify(subs)
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res

    else:
        return f"'{sub_reddit}' not found" ,404 ,{"Access-Control-Allow-Origin": "*"}

# http://localhost:3000/save
@app.route("/save" , methods=['POST'])
def Save():
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
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res , 200
    
    # print(all_submissions)
    res = jsonify("status:ok")
    res.headers.add('Access-Control-Allow-Origin', '*')
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
    return "Saved", 200 ,{"Access-Control-Allow-Origin": "*"}


@app.route("/check/<string:subreddit>", methods=['GET'])
def checkSubreddit(subreddit):
    is_exits =  reddit_api.check(subreddit)

    if is_exits:
        return "" , 200, {"Access-Control-Allow-Origin": "*"}
    
    return "" , 404 ,{"Access-Control-Allow-Origin": "*"}





@app.route("/test", methods=['GET'])
def test():
    data = {
  "mode": "day",
  "sub_reddit": "memes",
  "submission": [
    {
      "author": "so-unobvious",
      "created_at": 1684357508.0,
      "id": "13ke2ey",
      "score": 23165,
      "title": "Who do I call to complain",
      "upvote_ratio": 0.85,
      "url": "https://i.redd.it/k6wmemz3ig0b1.jpg"
    },
    {
      "author": "finndestroyer2",
      "created_at": 1684340000.0,
      "id": "13k68p5",
      "score": 17217,
      "title": "How are y'all not getting stung",
      "upvote_ratio": 0.9,
      "url": "https://i.redd.it/futo8f5ljg0b1.jpg"
    },
    {
      "author": "xocoping",
      "created_at": 1684315340.0,
      "id": "13jwmo1",
      "score": 16682,
      "title": "confused stonks",
      "upvote_ratio": 0.97,
      "url": "https://i.redd.it/zn30kmw8ie0b1.png"
    },
    {
      "author": "RansWachers",
      "created_at": 1684324347.0,
      "id": "13jziyo",
      "score": 15101,
      "title": "what is even the point of paying extra for luggage weight",
      "upvote_ratio": 0.92,
      "url": "https://i.redd.it/5zdz53sird0b1.jpg"
    },
    {
      "author": "Crankytyuz",
      "created_at": 1684325677.0,
      "id": "13k00o5",
      "score": 14309,
      "title": "“you ready guys”",
      "upvote_ratio": 0.96,
      "url": "https://i.redd.it/ynoj1frzcf0b1.jpg"
    }
  ],
  "time": "Thu, 18 May 2023 05:42:30 GMT",
  "total": 5
}
    res = jsonify(data)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

    



if __name__ == "__main__":
    app.run(debug=True,port=8080)