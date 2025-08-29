# X Bot tweeting UNDERTALE unique quotes (from text_data.json every 6 hours)
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

def get_client():
    """Returns a tweepy client authenticated with environment variables."""
    return tweepy.Client(
        consumer_key=os.environ["CONSUMER_KEY"],
        consumer_secret=os.environ["CONSUMER_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
    )

def tweet_quote(client, quotes):
    """Tweets a random quote from the provided list."""
    quote = random.choice(quotes)
    try:
        client.create_tweet(text=quote)
        print(f"Successfully tweeted: '{quote}' at {datetime.datetime.now(timezone('Asia/Bangkok'))}")
    except tweepy.TweepyException as e:
        print(f"Could not tweet. Error: {e}")

def load_quotes():
    """Loads and cleans quotes from the text_data.json file."""
    try:
        with open("text_data.json", "r") as f:
            print("Loading quotes from file...")
            data = json.load(f)
            strings = []
            for s in data["strings"]:
                # Clean up the string using regular expressions
                string = re.sub(r"((\\|\^).[0-9]?)|(\/(.+)?)", "", s)
                string = re.sub(r"&|#", "\n", string)
                if len(string.strip()) > 10:  # Ensure the quote is a reasonable length
                    strings.append(string.strip())
            return strings
    except FileNotFoundError:
        print("Error: 'text_data.json' not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Could not decode 'text_data.json'. Check for formatting issues.")
        return []

if __name__ == "__main__":
    keep_alive()  # Start the web server in a separate thread
    client = get_client()
    quotes = load_quotes()

    if not quotes:
        print("No quotes were loaded. The bot will not tweet.")
    else:
        # Schedule the job to run every 6 hours.
        schedule.every(6).hours.do(tweet_quote, client, quotes)
        print("Twitter bot scheduled to run every 6 hours.")

        # Run the initial tweet immediately.
        tweet_quote(client, quotes)

        # Main loop to check and run scheduled jobs.
        while True:
            schedule.run_pending()
            time.sleep(1) # Sleep for a short period to prevent high CPU usage

