#/usr/bin/python3

import requests
import json
import threading
import nltk.sentiment.vader

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_QUERY_BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"

stories = {}
comments = {}

def build_comments(comment_id_list, story_id):
    for comment_id in comment_id_list:
        comment = json.loads(requests.get(HN_ITEM_QUERY_BASE_URL + str(comment_id) + ".json").text)
        comments[story_id].append(comment)
        if("kids" in comment):
            build_comments(comment["kids"], story_id)

def build_stories():
    top_story_ids = json.loads(requests.get(HN_TOP_STORIES_URL).text)
    threadList = []
    count = 0
    for story_id in top_story_ids:
        count += 1
        story = json.loads(requests.get(HN_ITEM_QUERY_BASE_URL + str(story_id) + ".json").text)
        stories[story_id] = story
        comments[story_id] = []
        print("Building Comments for Story ID " + str(story_id) + " (" + str(count) + " of " +   str(len(top_story_ids)) + ")")
        if("kids" in story):
            thr = threading.Thread(target=build_comments, args=(story["kids"], story_id,))
            thr.start()
    print("Waiting for threads to complete")
    for thre in threadList:
        thre.join()

def add_sentiment_to_comments():
    for story_comment_list in comments.values():
        for comment in story_comment_list:
            print(comment) # here's where to add sentiment using nltk to text
            
if  __name__ =='__main__':
    print("Retrieving all comments through Hacker News API")
    print("-----------------------------------------------")
    build_stories()
    print("-----------------------------------------------")
    print("Retrieving Sentiment for Comments")
    print("---------------------------------")
    add_sentiment_to_comments()
