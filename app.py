from flask import Flask,render_template,redirect,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from reddit import Reddit
# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Memes.db"
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
    subs = reddit_api.submission_from_subreddit(subReddit=sub_reddit,mode=mode,limit=limit)
    previous_subs = Submission.query.all()

    for sub in previous_subs:
        if sub.submission_id in subs['submission']:
            subs['submission'].pop(sub.submission_id)
            pass

    subs['submission'] = sorted(subs['submission'].items() ,key=lambda x:x[0][1])
    subs.update({"total":len(subs['submission'])})
    return jsonify(subs)


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
        return jsonify(data)
    
    # print(all_submissions)
    return "Saved", 200

# http://localhost:3000/show
@app.route("/show")
def show_all():
    all_submissions = Submission.query.all()
    return jsonify(all_submissions)

@app.route("/remove/<string:submission_id>" , methods=['DELETE'])
def delete(submission_id):
    # delete from database
    submission = Submission.query.filter_by(submission_id=submission_id).first()
    db.session.delete(submission)
    db.session.commit()

    return "" , 204


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
    return "Saved", 200



if __name__ == "__main__":
    app.run(debug=True,port=3000)