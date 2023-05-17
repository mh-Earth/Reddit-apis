import os
import praw
# from dotenv import load_dotenv
from datetime import datetime
import pathlib
import json
from prawcore.exceptions import NotFound

# load_dotenv()
class Reddit():
    
    def __init__(self) -> None:
        self.reddit = praw.Reddit(
                client_id="_-al8UcecqA9UAg_u_wBrg",
                client_secret="Yv2-OLLm4Xv9ssQ4ZSEet7DVBjkKGA",
                user_agent="<Auto memer>",
        )
    
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
                if not submission.stickied and ".jpg" in url or ".png" in url:

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
                if not submission.stickied and ".jpg" in url or ".png" in url:
                    
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
                if not submission.stickied and ".jpg" in url or ".png" in url:
                    
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
    
    
    def check(self,subreddit:str):
        try:
            self.reddit.redditor(subreddit).id
        except Exception as e:
            return False
        return True


if __name__ == "__main__":

    a = Reddit()
    print(a.check("memes"))