#!/usr/bin/python

# Standard lib imports
import re
import logging
import json
import os
import time

# Third-party imports
import MySQLdb
from sqlalchemy.engine.url import make_url
import tweepy

# Constants
KEY = os.environ.get('TWITTER_KEY')
SECRET_KEY = os.environ.get('TWITTER_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')
DB_URL = os.environ.get('DATABASE_URL')

# Twitter API treats commas as logical OR, spaces as logical AND
TERMS = ['#falcons',
         '#patriots',
         '@AtlantaFalcons',
         '@Patriots',
         '#RiseUp',
         '#GoPats',
         'falcons superbowl',
         'patriots superbowl']

# Logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s $(name)-12s $(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class GameStreamListener(tweepy.StreamListener):
    """
    A stream listener that writes tweets on given subjects to the MySQL DB
    using a persistent connection
    """
    def __init__(self):
        logging.debug('Attempting to connect to MySQL database...')
        url = make_url(DB_URL)
        # Need to pass the charset argument so that the connection can
        # handle characters outside the range of normal UTF-8 (eg emojis) - JC
        self.connection = MySQLdb.connect(url.host, url.username,
                url.password, url.database, charset='utf8mb4')
        self.c = self.connection.cursor()

    def _has_falcons(self, tweet):
        regex = re.compile(r'falcons|@atlantafalcons|#riseup', flags=re.IGNORECASE)
        match = regex.search(tweet)
        if match:
            return 1
        return 0

    def _has_patriots(self, tweet):
        regex = re.compile(r'patriots|@patriots|#gopats', flags=re.IGNORECASE)
        match = regex.search(tweet)
        if match:
            return 1
        return 0

    def on_data(self, data):
        fdata = json.loads(data)
        tweet = fdata['text']
        username = fdata['user']['screen_name']
        has_falcons = self._has_falcons(tweet)
        has_patriots = self._has_patriots(tweet)

        self.c.execute('''INSERT INTO tweets (time, username, tweet,
                       has_falcons, has_patriots) VALUES (%s,%s,%s,%s,%s)''',
                       (time.time(), username, tweet, has_falcons, has_patriots))

        self.connection.commit()

    def on_error(self, status_code):
        # Twitter returns a 420 error if the client hits a rate limit, so we
        # need to exit gracefully when this happens
        if status_code == 420:
            logger.debug('Rate limit exceeded')
            # Returning False disconnects the stream
            return False

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
    stream.filter(track=TERMS)
