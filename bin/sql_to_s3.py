#!/usr/bin/python

# Standard lib imports
import time
import logging
import os

# Third-party imports
import boto3
from sqlalchemy import create_engine
import pandas as pd

# Constants
DATABASE_URL = os.environ.get('DATABASE_URL')
TMP = os.path.join('/tmp', 'tweets_per_minute_tmp.csv')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
BUCKET_NAME = 'ajcnewsapps'

# Logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TweetHandler(object):
    """
    Update columns in , outputs it as a CSV, and copies our data
    to AWS S3
    """
    def __init__(self, url):
        logging.debug('Attempting to connect to MySQL database...')
        self.engine = create_engine(url)
        self.s3 = self._start_s3_session()
        self.df = None

    def _start_s3_session(self):
        """
        Use boto3 to start an s3 session
        """
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )

        return session.resource('s3')


    def get_tweets(self, table_name):
        """
        Load tweets from MySQL database, add column with formatted time, group
        by that column, and write an updated CSV to S3
        """
        with self.engine.connect() as conn, conn.begin():
            logging.debug('Connection successful! Loading data into dataframe...')
            df = pd.read_sql_table(table_name, conn)

            # Get formatted time from Epoch time down to the minute, not second
            # I should be converting to a datetime object and binning
            # but this is a quick and dirty solution
            df['ftime'] = df.apply(lambda x: time.strftime('%m %d %H:%M',
                                    time.localtime(float(x['time']))), axis=1)
            falcons = df[df['has_falcons'] == '1']
            patriots = df[df['has_patriots'] == '1']

            falcons_g = falcons.groupby(['ftime']).size().reset_index()
            patriots_g = patriots.groupby(['ftime']).size().reset_index()
            ticker = falcons_g.merge(patriots_g, how='outer', on='ftime')
            ticker_f = ticker.rename({'0_x': 'falcons', '0_y': 'patriots'})
            ticker_f.reset_index().to_csv(TMP, index=False)


    def write_to_s3(self, local_path):
        bucket = self.s3.Bucket(BUCKET_NAME)
        bucket.upload_file(local_path, '2017/superbowl_li_twitter/tweets_per_minute.csv')

if __name__ == '__main__':
    tweetHandler = TweetHandler(DATABASE_URL)
    tweetHandler.get_tweets('tweets')
    tweetHandler.write_to_s3(TMP)
