from pprint import pprint
import time
from flask import request,jsonify,Blueprint
from reddit import Reddit
from models import Submission,Settings,Posted,Admin,db,password_auth,AdminPlaneUrls
from decorators import add_cors_headers,require_password,require_api_key
from utils import gen_random_string

bp = Blueprint('routes', __name__)

# Reddit api
reddit_api = Reddit()

# Apply CORS headers to all routes
@bp.after_request
@add_cors_headers
def add_cors_headers_to_response(response):
    return response



@bp.route("/api/admin",methods=['DELETE'])
@require_api_key
@require_password
@password_auth
def delete_admin():
    try:
        db.session.query(Admin).delete()
        db.session.commit()
        return "DELETED" ,200 , {"Access-Control-Allow-Origin": "*"}
    except Exception as e:
        print(e)


@bp.route("/api/admin/create",methods=['POST'])
@require_api_key
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
                print(e)
                return jsonify({"Message":f"Invaild Data. Correction:{e}"}) ,200
            except Exception as e:
                print(e)
                return "Server Error" ,500
        else:
            return jsonify({"Message":"Max user reached"})
        
@bp.route("/api/admin/check",methods=['GET'])
def check_admin():

    if request.method == "GET":
        admin = Admin.query.filter_by(id=1).first()
        if admin:
            return jsonify({"admin":True,"code":200}) , 200 , {"Access-Control-Allow-Origin": "*"}
        return jsonify({"admin":False}) , 200 , {"Access-Control-Allow-Origin": "*"}


@bp.route("/api/admin/genarate_url", methods=['POST'])
@require_api_key
@require_password
@password_auth
def genarate_admin_url():
    # step 1: Genarate an url
    try:
        new_admin_url = AdminPlaneUrls(slug=gen_random_string(64),create_at=time.time(),live=600,expired=False)
        db.session.add(new_admin_url)
        db.session.commit()
        return jsonify(new_admin_url),200
    except Exception as e:
        print(e)


def check_admin_url_slug_validation(slug:str) -> tuple[AdminPlaneUrls,bool]:
    slug_row:AdminPlaneUrls  = db.session.query(AdminPlaneUrls).filter(AdminPlaneUrls.slug == slug).first()
    # if there is a slug the check the validation
    print(slug_row)
    if slug_row:
        # if the time is expried then delete the slug from db
        time_gap:float = round(time.time() - slug_row.create_at,2)
        if time_gap > slug_row.live:
            return (slug_row,False)
        else:
            return (slug_row,True)
    else:
        return (slug_row,False)
        
            
def isHasAdminUser() -> bool:
    '''
    check for admin user existen in db
    '''
    admin = Admin.query.filter_by(id=1).first()
    if admin:
        return True
    else:
        return False
    
   
@bp.route("/api/admin/adminpanel", methods=['POST'])
@require_api_key
def adminpanel():
    # step 1: Genarate an url
    if request.is_json:
        jsondata = request.get_json()
        try:
            slug = jsondata['slug']
        except KeyError:
            return jsonify({"username":"","code":404})
        # check if the slug is valid or not
        validation = check_admin_url_slug_validation(slug)
        if validation[1]:
            admin = Admin.query.filter_by(id=1).first()
            if admin:
                return jsonify({"username":admin.username,"code":200}) , 200 , {"Access-Control-Allow-Origin": "*"}
            return jsonify({"username":"","code":404}) , 404 , {"Access-Control-Allow-Origin": "*"}
            
        else:
            try:
                db.session.delete(validation[0])
                db.session.commit()
            except Exception as e:
                pass
            return jsonify({"code":404}),404
        


# http://localhost:3000/get/meme/hot
@bp.route("/api/get/<string:sub_reddit>/<string:mode>/<int:limit>")
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
    subs.update({"total":len(subs['submission']),"hasAdmin":isHasAdminUser()})

    return jsonify(subs)


# http://localhost:3000/save
@bp.route("/api/save/<string:name>" , methods=['POST','PUT'])
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

@bp.route("/api/getall" , methods=['GET'])
@require_api_key
def getall():

    all_submissions:list[Submission] = Submission.query.all()
    name = [item.name for item in all_submissions]

    settings = Settings.query.filter_by(id=1).first()
    if settings == None:
        settings = Settings(limit=50,mode="day",is_reversed=True)
        db.session.add(settings)
        db.session.commit()

    if settings.is_reversed:
        all_submissions.reverse()
        name.reverse()

    # Getting all info about the submission from reddit's server
    data = reddit_api.nameToDetails(name)

    # merging OG data from reddit server and local data server data (tags,title etc...)
    for index,subs in enumerate(data["submission"]):
        subs.update({
            'tags':all_submissions[index].tags,
            'title':all_submissions[index].title,
            })
        
    data.update({"total":len(data['submission']),"hasAdmin":isHasAdminUser()})
    return jsonify(data) ,200

# http://localhost:3000/show
@bp.route("/api/showallnames")
def show_all():
    all_submissions = Submission.query.all()
    all_names = [sub.name for sub in all_submissions]
    return jsonify({"names":all_names}) , 200 ,{"Access-Control-Allow-Origin": "*"}

# http://localhost:3000/sub/id
@bp.route("/api/show/<string:name>")
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
@bp.route("/api/posted",methods=['POST','GET','DELETE'])
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


@bp.route("/api/remove/<string:name>" , methods=['DELETE'])
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
@bp.route("/api/removes", methods=['DELETE'])
@require_api_key
@require_password
@password_auth
def removes():
    if request.is_json:
        jsondata = request.get_json()
        try:
            for name in jsondata['names']:
                submission = Submission.query.filter(Submission.name.endswith(name)).first()
                if submission:
                    db.session.delete(submission)
                    db.session.commit()
        except KeyError:
            return jsonify({"Message":"Invaild Data"}) ,500
        except Exception as e:
            return "Server Error" , 500

    else:
        data = {
            "error":"No submission data found"
        }
        return jsonify(data) ,200 ,{"Access-Control-Allow-Origin": "*"}

    return "DELETED", 200 ,{"Access-Control-Allow-Origin": "*"}


@bp.route("/api/check/<string:subreddit>", methods=['GET'])
@require_api_key
def checkSubreddit(subreddit):
    if request.method == 'GET':

        is_exits =  reddit_api.check(subreddit)

        if is_exits:
            return "" , 200, {"Access-Control-Allow-Origin": "*"}

        return "" , 404 ,{"Access-Control-Allow-Origin": "*"}
    

# delete all submissions
@bp.route("/api/reset", methods=['DELETE'])
@require_api_key
@require_password
@password_auth
def delete_all():
    # Delete all entries in the model
    db.session.query(Submission).delete()
    db.session.commit()
    return "DELETED" ,200


@bp.route("/api/", methods=['get'])
def home():
    return jsonify({"status":"Running"}),200

@bp.route("/api/settings", methods=['POST','GET'])
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
    pass