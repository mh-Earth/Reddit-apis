import os
import praw
# from dotenv import load_dotenv
from datetime import datetime
import time
from settings import CLIENT_ID,CLIENT_SECRET,USER_AGENT
# load_dotenv()
class Reddit():

    def __init__(self) -> None:
        self.reddit = praw.Reddit( #vritual env dosen't work on production so remember it to replace variable from setting to their actual value everywhere.
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT
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


    # @measure_execution_time
    def nameToDetails(self,submission_names:list) -> dict:

        posts:dict = {
            "submission":[],
            "time":datetime.utcnow()
        }

        submissions_list = list(self.reddit.info(fullnames=submission_names))
        for submission in submissions_list:
                # if any of the required value dose not exits then skip that submission
                try:
                    if submission.url != "":
                        url = submission.url
                    else:
                        raise TypeError

                    posts["submission"].append({
                        "name":submission.name, # most required
                        "id":submission.id, # most required
                        "title_og":submission.title, # most required
                        "author":submission.author.name if submission.author != None else "Not found", #optional
                        "score":submission.score if submission.score != None else "Not found", #optional
                        "created_at":submission.created_utc if submission.created_utc != None else "Not found", #optional
                        "upvote_ratio":submission.upvote_ratio if submission.upvote_ratio != None else "Not found", #optional
                        "url":url # most required

                    })
                except Exception as e:
                    pass

        return posts
    
    def submission(self,id:str):
        '''id:str = Thing without underscore (_)'''
        return self.reddit.submission(id=id)
        



if __name__ == "__main__":
    r = Reddit()
    r.submission("1bz04dd")