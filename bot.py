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
    # Your tweepy client code remains the same
    client = tweepy.Client(
        consumer_key=os.environ["CONSUMER_KEY"],
        consumer_secret=os.environ["CONSUMER_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
    )
    return client

def load_quotes():
    """Loads and cleans quotes from the text_data.json file."""
    quotes = []
    try:
        with open("text_data.json", "r") as f:
            print("Loading strings...")
            data = json.load(f)
            for s in data["strings"]:
                # Clean up the string using regular expressions
                string = re.sub(r"((\\|\^).[0-9]?)|(\/(.+)?)", "", s)
                string = re.sub(r"&|#", "\n", string)
                if len(string.strip()) > 10:  # Check length after cleaning
                    quotes.append(string.strip())
            return quotes
    except FileNotFoundError:
        print("Error: 'text_data.json' not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Could not decode 'text_data.json'. Check for formatting issues.")
        return []

def tweet_quote(client, quotes):
    """Tweets a single random quote from the provided list."""
    if not quotes:
        print("No quotes available to tweet.")
        return

    text = random.choice(quotes)
    try:
        client.create_tweet(text=text)
        print(f"Successfully tweeted: '{text}' at {datetime.datetime.now(timezone('Asia/Bangkok'))}")
    except Exception as e:
        print(f"Could not tweet. Error: {e}")

if __name__ == "__main__":
    # Start the keep_alive server immediately in the background
    keep_alive()
    print("Keep-alive server started.")

    # Load resources once at the beginning
    client = get_client()
    quotes_list = load_quotes()

    if quotes_list:
        # Run the initial tweet immediately
        tweet_quote(client, quotes_list)
        
        # Schedule the job to run every 6 hours
        schedule.every(6).hours.do(tweet_quote, client, quotes_list)
        print("Twitter bot scheduled to tweet every 6 hours.")
    else:
        print("No quotes loaded, bot will not schedule tweets.")
    
    # Main loop to check and run scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1) # Sleep for a short period to prevent high CPU usage

