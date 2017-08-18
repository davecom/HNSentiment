#/usr/bin/python3

import asyncio
import concurrent.futures
import requests
import json
import threading
from nltk.sentiment.vader import SentimentIntensityAnalyzer

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_QUERY_BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"

stories = {}
comments = {}

def build_comments(comment_id_list, story_id, count_id):
    for comment_id in comment_id_list:
        comment = json.loads(requests.get(HN_ITEM_QUERY_BASE_URL + str(comment_id) + ".json").text)
        comments[story_id].append(comment)
        if("kids" in comment):
            build_comments(comment["kids"], story_id, -1)
    if count_id > 0:
        print(str(count_id) + "done")


async def build_stories():
    top_story_ids = json.loads(requests.get(HN_TOP_STORIES_URL).text)
    futures = []
    count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        loop = asyncio.get_event_loop()
        for story_id in top_story_ids:
            count += 1
            story = json.loads(requests.get(HN_ITEM_QUERY_BASE_URL + str(story_id) + ".json").text)
            print(story)
            stories[story_id] = story
            comments[story_id] = []
            print("Building Comments for Story ID " + str(story_id) + " (" + str(count) + " of " +   str(len(top_story_ids)) + ")")
            if("kids" in story):
                #thr = threading.Thread(target=build_comments, args=(story["kids"], story_id,))

                futures.append(loop.run_in_executor(executor, build_comments, story["kids"], story_id, count))
            if count == 5: break #for debug only look at 5 stories
        print("Waiting for requests to complete")
        await asyncio.gather(*futures)

def add_sentiment_to_comments():
    sia = SentimentIntensityAnalyzer()
    for story_comment_list in comments.values():
        for comment in story_comment_list:
            if "text" in comment:
                comment["sentiment"] = sia.polarity_scores(comment["text"])
            print(comment) # here's where to add sentiment using nltk to text

def add_sentiment_to_stories():
    for story_id in stories:
        sentiments_of_story = [comment["sentiment"]["compound"] for comment in comments[story_id] if "sentiment" in comment ]
        stories[story_id]["sentiment"] = sum(sentiments_of_story) / float(len(sentiments_of_story))
        print(stories[story_id]["sentiment"])

            
if  __name__ =='__main__':
    print("Retrieving all comments through Hacker News API")
    print("-----------------------------------------------")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(build_stories())
    loop.close()
    print("-----------------------------------------------")
    print("Retrieving Sentiment for Comments")
    print("---------------------------------")
    add_sentiment_to_comments()
    print("Computing Sentiment for Stories")
    print("-------------------------------")
    add_sentiment_to_stories()
