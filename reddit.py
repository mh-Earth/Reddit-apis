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
            "submission":[],
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

                    posts["submission"].append({
                        "id":submission.id,
                        "title":submission.title,
                        "author":submission.author.name,
                        "score":submission.score,
                        "created_at":submission.created_utc,
                        "upvote_ratio":submission.upvote_ratio,
                        "url":submission.url

                    })


            return posts

        elif mode == "hot":
            for submission in subreddit.hot(limit=limit):
                url:str = submission.url.lower()
                if not submission.stickied and ".jpg" in url or ".png" in url:
                    
                    posts["submission"].append({
                        "id":submission.id,
                        "title":submission.title,
                        "author":submission.author.name,
                        "score":submission.score,
                        "created_at":submission.created_utc,
                        "upvote_ratio":submission.upvote_ratio,
                        "url":submission.url

                    })

            return posts

        elif mode == "new":
            for submission in subreddit.new(limit=limit):
                url:str = submission.url.lower()
                if not submission.stickied and ".jpg" in url or ".png" in url:
                    
                    posts["submission"].append({
                        "id":submission.id,
                        "title":submission.title,
                        "author":submission.author.name,
                        "score":submission.score,
                        "created_at":submission.created_utc,
                        "upvote_ratio":submission.upvote_ratio,
                        "url":submission.url

                    })

            return posts

        elif mode == "rising":
            for submission in subreddit.rising():
                url:str = submission.url.lower()
                if not submission.stickied and ".jpg" in url or ".png" in url:
                    
                    posts["submission"].append({
                        "id":submission.id,
                        "title":submission.title,
                        "author":submission.author.name,
                        "score":submission.score,
                        "created_at":submission.created_utc,
                        "upvote_ratio":submission.upvote_ratio,
                        "url":submission.url

                    })

            return posts
        
        else:
            return None
    
    
    def check(self,subreddit:str):
        try:
            self.reddit.redditor(subreddit).id
        except Exception as e:
            try:
                self.reddit.subreddit(subreddit).id
                return True
            except Exception as e:
                return False
        return True

    def test(self,subreddit):
        try:
            self.reddit.redditor(subreddit).id
        except Exception as e:
            try:
                self.reddit.subreddit(subreddit).id
                return True
            except Exception as e:
                return False
        return True



if __name__ == "__main__":

    a = Reddit()
    print(a.test("memes"))