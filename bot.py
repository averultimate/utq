# X Bot tweeting UNDERTALE unique quotes (from text_data.json every 24 hours)
import tweepy
import os
import json
import random
import re
import schedule
import time
import datetime
from pytz import timezone
from keep_alive import keep_alive
keep_alive()

def get_client():

    client = tweepy.Client(
        consumer_key=os.environ["CONSUMER_KEY"],
        consumer_secret=os.environ["CONSUMER_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
    )

    return client


def tweet(client, text):
    client.create_tweet(text=text)


"""

  Start automation, get text_data.json
  and tweet every 24 hours

"""

strings = list()

with open("text_data.json", "r") as f:
    print("Loading strings")
    data = json.load(f)
    for s in data["strings"]:
        string = re.sub(r"((\\|\^).[0-9]?)|(\/(.+)?)", "", s)
        string = re.sub(r"&|#", "\n", string)

        if len(string) > 10:
            strings.append(string)


def get_word():
    return random.choice(strings)


def tweet_quote():
    client = get_client()

    for _ in range(3):
        text = get_word()
        tweet(client, text)
    print("Job ran at:", datetime.datetime.now(timezone("Asia/Bangkok")))


print("Scheduling twitter bot")
tweet_quote() # Tweet once
schedule.every(6).hours.do(tweet_quote)

while True:
    schedule.run_pending()
    time.sleep(1)


