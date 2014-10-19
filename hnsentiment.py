#/usr/bin/python3

import requests
import json
from multiprocessing import Pool

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

top_story_ids = json.loads(requests.get(HN_TOP_STORIES_URL).text)
pool = Pool(10)
for story_id in top_story_ids:
    story = json.loads(requests.get(HN_ITEM_QUERY_BASE_URL + str(story_id) + ".json").text)
    stories[story_id] = story
    comments[story_id] = []
    print("Building Comments for Story ID " + str(story_id))
    if("kids" in story):
        pool.apply_async(build_comments(story["kids"], story_id))