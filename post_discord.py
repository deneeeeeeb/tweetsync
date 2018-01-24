#! /home/pi/.pyenv/shims/python
# -*- coding:utf-8 -*-
import json, config
import time
import os
import re
import json
import requests
from pprint import pprint

# import logging
# logging.basicConfig(level=logging.DEBUG)

from requests_oauthlib import OAuth1Session

CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET

webhook_url = config.WEBHOOK_URL


# debug run
# os.system('echo "" > /tmp/splamemo.list')


while True:
    twitter = OAuth1Session(CK, CS, AT, ATS)
    # url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    url = "https://api.twitter.com/1.1/lists/statuses.json"
    # url = "https://api.twitter.com/1.1/lists/list.json"

    params ={'count' : 3, 'owner_screen_name' : 'deneeeeeeb', 'slug' : 'splaplayers'}
    # params ={'count' : 10, 'owner_screen_name' : 'deneeeeeeb', 'slug' : 'splamemo'}

    req = ""
    req = twitter.get(url, params = params)

    if req.status_code == 200:
        timeline = ""
        timeline = json.loads(req.text)

       
        for tweet in reversed(timeline):

            cmd = 'grep ' + str(tweet['id']) + ' /tmp/splamemo.list'
            print(cmd)
            if os.system(cmd):

                # debug
                # print(tweet['user']['name'])
                # print(tweet['user']['screen_name'])
                # print(tweet['text'])
                # print(tweet['truncated'])
                # pprint(tweet)
                # print("------------")

                truncated = tweet['truncated']

                # check truncated
                tweet_text=""
                if truncated:
                    pattern = r"https[^ ]*$"
                    tweeturl = re.search(pattern , tweet['text'])
                    tweet_text = tweeturl.group()
                else:
                    # tweet_text = "https://twitter.com/" + tweet['user']['screen_name'] + "/status/" + str(tweet['id'])
                    tweet_text = tweet['text']

                # print(tweet['user']['profile_image_url_https'])

                # print('----------------------------------------------------')



                # post data
                payload_dic = {
                    # "content":str(tweeturl.group()),
                    "content":str(tweet_text),
                    "username":tweet['user']['name'],
                    "avatar_url":tweet['user']['profile_image_url_https'],
                }

                json_data = '{\'content\': \'test\'}'

                # post
                r = requests.post(webhook_url, data=json.dumps(payload_dic), headers={'Content-Type': 'application/json'})
                print(r)



                # add temp file
                cmd = 'echo ' + str(tweet['id']) + ' >> /tmp/splamemo.list'
                os.system(cmd)

    else:
        print("ERROR: %d" % req.status_code)
        print(req.json())

    time.sleep(60)
