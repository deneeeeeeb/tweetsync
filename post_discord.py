#! /home/pi/.pyenv/shims/python
# -*- coding:utf-8 -*-
import json
import configparser
import time
import os
import re
import json
import requests
import sys
from pprint import pprint
from requests_oauthlib import OAuth1Session


# load config
config   = configparser.ConfigParser()
confpath = os.path.dirname(os.path.abspath(__file__)) + "/config.ini"
config.read(confpath)


# get oauth session
CK  = config['common']['CONSUMER_KEY']
CS  = config['common']['CONSUMER_SECRET']
AT  = config['common']['ACCESS_TOKEN']
ATS = config['common']['ACCESS_TOKEN_SECRET']
twitter = OAuth1Session(CK, CS, AT, ATS)


# debug run
# os.system('echo "" > /tmp/splamemo.list')


# main loop
while True:

    # set twitter api
    url    = "https://api.twitter.com/1.1/lists/statuses.json"
    params = {'count' : 100, 'owner_screen_name' : 'deneeeeeeb', 'slug' : 'splaplayers'}

    # get twitter api
    req = twitter.get(url, params = params)

    # get twitter api success
    if req.status_code == 200:

        # get json
        timeline = json.loads(req.text)
       
        # loop for each tweet
        for tweet in reversed(timeline):

            # check posted id
            cmd = 'grep ' + str(tweet['id']) + ' /tmp/splamemo.list >> /dev/null'
            if os.system(cmd):

                # debug
                # pprint(tweet)

                # check truncated
                truncated  = tweet['truncated']
                tweet_text =""

                # truncated
                if truncated:

                    # set text (url)
                    pattern    = r"https[^ ]*$"
                    tweeturl   = re.search(pattern , tweet['text'])
                    tweet_text = tweeturl.group()

                # not truncated
                else:
                    # set text
                    tweet_text = tweet['text']

                # set post data
                post_data = {
                    "content"   : str(tweet_text),
                    "username"  : tweet['user']['name'],
                    "avatar_url": tweet['user']['profile_image_url_https'],
                }

                # post
                print("post : " + str(tweet['id']))
                webhook_url = config['prod']['WEBHOOK_URL']
                r = requests.post(webhook_url, data=json.dumps(post_data), headers={'Content-Type': 'application/json'})

                # if error
                if r.status_code != 204:

                    # wait & rerun
                    time.sleep(60)
                    r = requests.post(webhook_url, data=json.dumps(post_data), headers={'Content-Type': 'application/json'})                    

                    # error end
                    if r.status_code != 204:
                        print("error: %d" % r.status_code)
                        print(r.json())
                        sys.exit(10)


                # add log
                cmd = 'echo ' + str(tweet['id']) + ' >> /tmp/splamemo.list'
                os.system(cmd)

    # get twitter api error
    else:
        print("error: %d" % req.status_code)
        print(req.json())
        sys.exit(20)


    # wait
    time.sleep(60)
