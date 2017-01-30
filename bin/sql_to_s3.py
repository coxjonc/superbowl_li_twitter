#!/usr/bin/python

# Standard lib imports
import logging
import os
import time
import re

# Third-party imports
from sqlalchemy import create_engine
import pandas as pd

# Constants
DATABASE_URL = os.environ.get('DATABASE_URL')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s $(name)-12s $(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TweetHandler(object):
    """
    Handles getting data from a MySQL database, doing some regex to
    figure out additional columns, outputting as a CSV, and copying our data
    to AWS S3
    """
    def __init__(self, url):
        self.engine = create_engine(url)
        self.df = None

    def _convert_time(self, row):
        ftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(row['time'])))
        return ftime

    def _check_falcons(self, row):
        regex = re.compile(r'falcons|@atlantafalcons|#riseup', flags=re.IGNORECASE)
        match = regex.search(row['tweet'])
        if match:
            return True
        return False

    def _check_patriots(self, row):
        regex = re.compile(r'patriots|@patriots|#gopats', flags=re.IGNORECASE)
        match = regex.search(row['tweet'])
        if match:
            return True
        return False

    def get_table(self, table_name):
        with self.engine.connect() as conn, conn.begin():
            logger.debug('Connected to database, getting data')
            self.df = pd.read_sql_table(table_name, conn)


    def format_csv(self):
        df = self.df

        # Add Boolean columns for whether a given row contains a reference
        # to the Patriots or the Falcons
        logger.debug('Adding boolean columns for falcons and patriots')
        df['has_falcons'] = df.apply(self._check_falcons, axis=1)
        df['has_patriots'] = df.apply(self._check_patriots, axis=1)

        return df

    def __str__(self):
        print self.df['tweet']

if __name__ == '__main__':
    tweetHandler = TweetHandler(DATABASE_URL)
    tweetHandler.get_table('tweets')
    df = tweetHandler.format_csv()
    df.to_csv(os.path.join(BASE_DIR, 'coolest_csv.csv'))
