from flask import Flask, render_template
from threading import Thread
import tweepy
import os
import json
import random
import re
import schedule
import time
import datetime
from pytz import timezone

# Flask app setup
app = Flask(__name__)

# Bot's core functions
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
        print(f"Successfully tweeted: '{text}' at {datetime.datetime.now(timezone('Asia/Bangkok'))}")
    except Exception as e:
        print(f"Could not tweet. Error: {e}")

# The bot's main logic to run in a separate thread
def run_bot():
    print("Starting bot logic...")
    client = get_client()
    quotes_list = load_quotes()

    if quotes_list:
        tweet_quote(client, quotes_list)
        schedule.every(6).hours.do(tweet_quote, client, quotes_list)
        print("Twitter bot scheduled to tweet every 6 hours.")
    else:
        print("No quotes loaded, bot will not schedule tweets.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Flask route for keep-alive pings
@app.route('/')
def index():
    print("Received ping. Bot is online.")
    return "Bot is online."

# Function to start the Flask app in a thread
def run_flask_app():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Start the bot's logic in a separate thread
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    
    # Start the Flask app in a separate thread (this keeps it non-blocking)
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()
