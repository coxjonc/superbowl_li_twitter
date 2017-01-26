#!/usr/bin/python

# Standard lib imports
import json
import pdb
import os

# Third-party imports
import MySQLdb
from sqlalchemy.engine.url import make_url
import time
import tweepy

# Constants
KEY = os.environ.get('TWITTER_KEY')
SECRET_KEY = os.environ.get('TWITTER_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')
DB_URL = os.environ.get('DATABASE_URL')

class GameStreamListener(tweepy.StreamListener):
    """
    A stream listener that writes tweets on given subjects to the MySQL DB
    using a persistent connection
    """
    def __init__(self):
        url = make_url(DB_URL)
        self.connection = MySQLdb.connect(url.host, url.username,
                url.password, url.database)
        self.c = self.connection.cursor()

    def on_data(self, data):
        fdata = json.loads(data)
        tweet = fdata['text']
        username = fdata['user']['screen_name']

        self.c.execute('INSERT INTO tweets (time, username, tweet) VALUES (%s,%s,%s)',
                (time.time(), username, tweet))

        self.connection.commit()

    def on_error(self, status_code):
        # Twitter returns a 420 error if the client hits a rate limit
        if status_code == 420:
            # Returning False disconnects the stream
            return False

    def on_status(self, status):
        print(status.text)

class StreamAuth(tweepy.OAuthHandler):
    """
    A single class to handle app authentication, set the access token, and
    return an authentication handler object
    """
    def __init__(self, key, secret):
        super(StreamAuth, self).__init__(key, secret)
        self.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

if __name__ == '__main__':
    # Create an authenticated API object
    auth = StreamAuth(KEY, SECRET_KEY)
    api = tweepy.API(auth_handler=auth)
    gameStreamListener = GameStreamListener()

    # Create a stream object and begin listening for terms
    stream = tweepy.Stream(auth=api.auth, listener=gameStreamListener)
    stream.filter(track=['falcons'])
