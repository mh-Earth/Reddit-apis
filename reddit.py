import os
import praw
# from dotenv import load_dotenv
from datetime import datetime
import pathlib
import json
from prawcore.exceptions import NotFound
import time

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
                        "name":submission.name,
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
                        "name":submission.name,
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
                        "name":submission.name,
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
                        "name":submission.name,
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
            self.reddit.subreddit(subreddit).id
        except Exception as e:
            return False
        
        return True
    
    def measure_execution_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            print(f"Execution time of {func.__name__}: {execution_time} seconds")
            return result
        return wrapper

    @measure_execution_time
    def nameToDetails(self,submission_names:list) -> dict:

        posts:dict = {
            "submission":[],
            "time":datetime.utcnow()
        }

        submissions_list = list(self.reddit.info(fullnames=submission_names))
        for submission in submissions_list:
                posts["submission"].append({
                    "name":submission.name,
                    "id":submission.id,
                    "title":submission.title,
                    "author":submission.author.name,
                    "score":submission.score,
                    "created_at":submission.created_utc,
                    "upvote_ratio":submission.upvote_ratio,
                    "url":submission.url

                })

        return posts







if __name__ == "__main__":

    pass