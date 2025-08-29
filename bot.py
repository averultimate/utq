from flask import Flask
from datetime import datetime, timedelta
import os
import json
import random
import tweepy

app = Flask(__name__)

last_tick = datetime.now()
last_hour = last_tick.hour
tweet_hour_multiple = 6
tweet_count = 3
next_tweet = None


def get_client():
    client = tweepy.Client(
        consumer_key=os.environ["CONSUMER_KEY"],
        consumer_secret=os.environ["CONSUMER_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
    )
    return client


def load_quotes():
    quotes = []
    try:
        with open("text_data.json", "r") as f:
            print("Loading strings...")
            data = json.load(f)
            for s in data["strings"]:
                string = re.sub(r"((\\|\^).[0-9]?)|(\/(.+)?)", "", s)
                string = re.sub(r"&|#", "\n", string)
                if len(string.strip()) > 10:
                    quotes.append(string.strip())
            return quotes
    except FileNotFoundError:
        print("Error: 'text_data.json' not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Could not decode 'text_data.json'. Check for formatting issues.")
        return []


def tweet_quote(client, quotes):
    if not quotes:
        print("No quotes available to tweet.")
        return
    text = random.choice(quotes)
    try:
        client.create_tweet(text=text)
        print(f"Successfully tweeted: '{text}' at {datetime.now()}")
    except Exception as e:
        print(f"Could not tweet. Error: {e}")


for i in range(12):
    if (last_hour + i) % tweet_hour_multiple == 0:
        if (last_hour + i) < 24:
            next_tweet = last_tick.replace(
                hour=last_hour + i, minute=0, second=0, microsecond=0
            )
            break

        else:
            next_tweet = last_tick.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)
            break


@app.route("/")
def index():
    # Pinged by something
    global next_tweet

    current_tick = datetime.now()

    if current_tick >= next_tweet:
        client = get_client()
        quotes = load_quotes()

        for i in range(tweet_count):
            tweet_quote(client, quotes)

        if current_tick.hour + tweet_hour_multiple < 24:
            last_tick = current_tick.replace(
                hour=current_tick.hour + tweet_hour_multiple,
                minute=0,
                second=0,
                microsecond=0,
            )

        else:
            last_tick = current_tick.replace(
                hour=24 - (current_tick.hour + tweet_hour_multiple),
                minute=0,
                second=0,
                microsecond=0,
            ) + timedelta(days=1)

        next_tweet = last_tick

    return f"I will tweet at {next_tweet} (in {next_tweet.hour - current_tick.hour} hour(s) and {next_tweet.minute - current_tick.minute} minute(s).)"


if __name__ == "__main__":
    app.run(debug=True)
