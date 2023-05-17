import os
import praw
# from dotenv import load_dotenv
from datetime import datetime
import pathlib
import json
# load_dotenv()
class Reddit():
    
    JSON_PATH = "Selected.json"
    POST_KEY = "submission"
    def __init__(self) -> None:
        self.reddit = praw.Reddit(
                client_id="_-al8UcecqA9UAg_u_wBrg",
                client_secret="Yv2-OLLm4Xv9ssQ4ZSEet7DVBjkKGA",
                user_agent="<Auto memer>",
        )
        
        self.data_path = os.path.join(pathlib.Path(__file__).parent.resolve())
        self.postHistoryFolder = os.path.join(self.data_path,self.JSON_PATH)

        
        if not os.path.isfile(self.postHistoryFolder):
            with open("Selected.json","w+") as f:
                f.write('{"submission": ["a"]}')
                
            with open("Selected.json","r") as f:
                self.selected_sumissions:list = dict(json.load(f))["submission"][-100:]
                self.postHistory = dict(json.load(f))
                
        else:
            with open("Selected.json","r") as f:
                self.selected_sumissions:list = dict(json.load(f))["submission"][-100:]
            
    
    # return every .png , .jpg file submission those who have not beem selected before
    def submission_from_subreddit(self,subReddit:str,mode:str,limit:int) -> dict :

        posts:dict = {
            "submission":{},
            "sub_reddit":subReddit,
            "mode":mode,
            "time":datetime.utcnow()
        }
        subreddit = self.reddit.subreddit(subReddit)

        if mode == 'day':
            submissions = subreddit.top("day", limit=limit)
            for submission in submissions:
                url:str = submission.url.lower()
                if not submission.stickied and ".jpg" in url or ".png" in url and submission.id not in self.selected_sumissions:

                    posts["submission"].update({submission.id:{
                        "id":submission.id,
                        "author":submission.author.name,
                        "created_at":submission.created_utc,
                        "title":submission.title,
                        "score":submission.score,
                        "url":submission.url,
                        "upvote_ratio":submission.upvote_ratio

                    }})


            return posts

        elif mode == "hot":
            for submission in subreddit.hot(limit=limit):
                url:str = submission.url.lower()
                if not submission.stickied and ".jpg" in url or ".png" in url and submission.id not in self.selected_sumissions:
                    
                    posts["submission"].update({submission.id:{
                        "id":submission.id,
                        "author":submission.author.name,
                        "created_at":submission.created_utc,
                        "title":submission.title,
                        "score":submission.score,
                        "url":submission.url,
                        "upvote_ratio":submission.upvote_ratio


                    }})

            return posts

        elif mode == "new":
            for submission in subreddit.new(limit=limit):
                url:str = submission.url.lower()
                if not submission.stickied and ".jpg" in url or ".png" in url and submission.id not in self.selected_sumissions:
                    
                    posts["submission"].update({submission.id:{
                        "id":submission.id,
                        "author":submission.author.name,
                        "created_at":submission.created_utc,
                        "title":submission.title,
                        "score":submission.score,
                        "url":submission.url,
                        "upvote_ratio":submission.upvote_ratio


                    }})

            return posts
        
        else:
            return None


    
    def save_submissions_json(self): 
        with open("Selected.json","r") as f:
            postHistory = dict(json.load(f))
            postHistory.update({self.POST_KEY:self.selected_sumissions})

        with open(self.postHistoryFolder,"w") as f:
            json.dump(postHistory,f)

    def add_submission(self,submission:str):
        self.selected_sumissions.append(submission)
    
    def remove_submission(self,submission):
        self.selected_sumissions.remove(submission)

if __name__ == "__main__":

    a = Reddit()
